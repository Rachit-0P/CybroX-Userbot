#  CybroX-UserBot - telegram userbot
#  Copyright (C) 2025 CybroX UserBot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import importlib
import logging
from pyrogram import Client
from pathlib import Path

from utils.misc import modules_help


class ModuleManager:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ModuleManager()
        return cls._instance
    
    async def load_modules(self, client: Client):
        """Load all modules from modules directory"""
        base_path = Path(__file__).parent.parent.absolute()
        modules_path = base_path / "modules"
        
        for filename in sorted(os.listdir(modules_path)):
            if filename.endswith(".py") and not filename.startswith("__"):
                try:
                    module_name = filename[:-3]
                    module_path = f"modules.{module_name}"
                    
                    spec = importlib.util.find_spec(module_path)
                    if spec is None:
                        continue
                        
                    module = importlib.import_module(module_path)
                    importlib.reload(module)
                    logging.info(f"Module {module_name} loaded successfully")
                    
                except Exception as e:
                    logging.error(f"Error loading module {filename}: {e}")
        
        # Load custom modules if they exist
        custom_modules_path = os.path.join(modules_path, "custom_modules")
        if os.path.isdir(custom_modules_path):
            for filename in sorted(os.listdir(custom_modules_path)):
                if filename.endswith(".py"):
                    try:
                        module_name = filename[:-3]
                        module_path = f"modules.custom_modules.{module_name}"
                        
                        spec = importlib.util.find_spec(module_path)
                        if spec is None:
                            continue
                            
                        module = importlib.import_module(module_path)
                        importlib.reload(module)
                        logging.info(f"Custom module {module_name} loaded successfully")
                        
                    except Exception as e:
                        logging.error(f"Error loading custom module {filename}: {e}")
                        
    async def reload_module(self, module_name: str) -> bool:
        """Reload a specific module by name"""
        try:
            module_path = f"modules.{module_name}"
            if importlib.util.find_spec(module_path):
                module = importlib.import_module(module_path)
                importlib.reload(module)
                return True
        except Exception as e:
            logging.error(f"Error reloading {module_name}: {e}")
        return False
        

class HelpNavigator:
    """Class for help navigation"""
    def __init__(self):
        self.current_page = 1
        self.module_list = sorted(list(modules_help.keys()))
        self.total_pages = (len(self.module_list) + 9) // 10
        
    async def send_page(self, message):
        from utils.misc import prefix

        start_index = (self.current_page - 1) * 10
        end_index = start_index + 10
        page_modules = self.module_list[start_index:end_index]
        text = "<b>Help for CybroX-UserBot</b>\n"
        text += f"For more help on how to use a command, type <code>{prefix}help [module]</code>\n\n"
        text += f"Help Page No: {self.current_page}/{self.total_pages}\n\n"
        for module_name in page_modules:
            commands = modules_help[module_name]
            text += f"<b>• {module_name.title()}:</b> {', '.join([f'<code>{prefix + cmd_name.split()[0]}</code>' for cmd_name in commands.keys()])}\n"
        text += f"\n<b>The number of modules in the userbot: {len(modules_help)}</b>"
        
        await message.edit(text)