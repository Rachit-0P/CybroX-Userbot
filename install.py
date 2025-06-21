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
import sys
import logging
from getpass import getpass
from datetime import datetime
from pyrogram import Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_env():
    """Create .env file from .env.dist if not exists"""
    if os.path.exists(".env"):
        return False
    
    if not os.path.exists(".env.dist"):
        logger.error(".env.dist file not found. Please reinstall the repository.")
        return False
    
    logger.info("Creating .env file from template...")
    with open(".env.dist", "r") as template:
        with open(".env", "w") as env_file:
            env_file.write(template.read())
    logger.info("Created .env file. Please edit it with your credentials.")
    return True


def get_string_session():
    """Generate string session"""
    from utils import config
    
    print("Generating string session...\n")
    api_id = input("Enter API ID: ")
    api_hash = input("Enter API HASH: ")
    
    with Client("my_account", api_id=api_id, api_hash=api_hash) as app:
        session_string = app.export_session_string()
        print("\nYour session string:")
        print(f"\n{session_string}\n")
        print("Please store this string securely!")
        
        with open(".env", "r") as file:
            env_content = file.read()
        
        env_content = env_content.replace("API_ID=", f"API_ID={api_id}")
        env_content = env_content.replace("API_HASH=", f"API_HASH={api_hash}")
        env_content = env_content.replace("STRINGSESSION=", f"STRINGSESSION={session_string}")
        
        with open(".env", "w") as file:
            file.write(env_content)
        
        print("\nSession string has been saved to .env file.")


def check_dependencies():
    """Check and install dependencies if needed"""
    try:
        import pymongo
        import pyrogram
        import dns
        import environs
    except ImportError:
        logger.info("Installing required dependencies...")
        os.system(f"{sys.executable} -m pip install -r requirements.txt")


def create_directories():
    """Create necessary directories"""
    dirs = ["modules", "modules/custom_modules", "downloads"]
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
    
    # Create __init__.py in modules directory
    for directory in ["modules", "modules/custom_modules"]:
        init_file = os.path.join(directory, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write("# This file makes the directory a Python package\n")


def setup_database():
    """Setup database connection"""
    from utils import config
    
    if config.db_type.lower() in ["mongo", "mongodb"]:
        try:
            from pymongo import MongoClient
            
            db = MongoClient(config.db_url)
            db.server_info()  # Test connection
            logger.info("MongoDB connection successful")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            return False
    return True


def ask_restart_method():
    """Ask user for preferred restart method"""
    print("\nHow do you want to run CybroX-UserBot?")
    print("1. With PM2 (recommended for VPS)")
    print("2. With systemd (Linux only)")
    print("3. Directly with Python")
    
    choice = input("\nEnter your choice (1-3) [default: 3]: ").strip() or "3"
    return choice


def setup_service(choice):
    """Setup service based on user choice"""
    if choice == "1":
        try:
            os.system("npm install -g pm2")
            with open("cybrox.sh", "w") as f:
                f.write("#!/bin/bash\ncd \"$(dirname \"$0\")\"\npython3 main.py")
            os.system("chmod +x cybrox.sh")
            os.system("pm2 start cybrox.sh --name CybroX")
            logger.info("PM2 service configured! To restart: pm2 restart CybroX")
            return "pm2 restart CybroX"
        except Exception as e:
            logger.error(f"PM2 setup failed: {e}")
            return "cd CybroX/ && python main.py"
    
    elif choice == "2":
        try:
            service_content = f"""[Unit]
Description=CybroX-UserBot
After=network.target

[Service]
Type=simple
WorkingDirectory={os.getcwd()}
ExecStart={sys.executable} {os.getcwd()}/main.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
            with open("/tmp/cybrox.service", "w") as f:
                f.write(service_content)
            
            os.system("sudo mv /tmp/cybrox.service /etc/systemd/system/")
            os.system("sudo systemctl daemon-reload")
            os.system("sudo systemctl enable cybrox")
            os.system("sudo systemctl start cybrox")
            logger.info("Systemd service configured! To restart: sudo systemctl restart cybrox")
            return "sudo systemctl restart cybrox"
        except Exception as e:
            logger.error(f"Systemd setup failed: {e}")
            return "cd CybroX/ && python main.py"
    
    else:
        return "cd CybroX/ && python main.py"


def main():
    logger.info("Starting CybroX-UserBot installation...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required!")
        return
    
    # Create necessary directories
    create_directories()
    
    # Create .env file if not exists
    if create_env():
        logger.info("Please fill in the .env file with your credentials and run install.py again.")
        return
    
    # Check dependencies
    check_dependencies()
    
    try:
        # Import config after dependencies are installed
        from utils import config
        
        # Check if API credentials are set
        if not config.api_id or not config.api_hash:
            logger.error("API_ID and API_HASH are not set in .env file!")
            logger.info("Would you like to set them now? (y/n)")
            if input().lower().strip() == "y":
                get_string_session()
            return
        
        # Check if string session is set
        if not config.STRINGSESSION:
            logger.info("String session not found. Generating now...")
            get_string_session()
        
        # Setup database
        if not setup_database():
            return
        
        # Ask for restart method
        choice = ask_restart_method()
        restart_cmd = setup_service(choice)
        
        # Try to send test message
        with Client("my_account", api_id=config.api_id, api_hash=config.api_hash, session_string=config.STRINGSESSION) as app:
            try:
                app.send_message(
                    "me",
                    f"<b>[{datetime.now()}] CybroX-UserBot installed successfully!</b>\n"
                    f"<b>To restart the bot, use:</b>\n<code>{restart_cmd}</code>"
                )
                logger.info("Installation complete! Test message sent to Saved Messages.")
            except Exception as e:
                logger.error(f"Could not send test message: {e}")
        
        logger.info(f"Installation complete! To restart CybroX-UserBot, use: {restart_cmd}")
        
        if choice == "3":
            logger.info("Starting CybroX-UserBot now...")
            os.system(f"{sys.executable} main.py")
            
    except Exception as e:
        logger.error(f"Installation failed: {e}")


if __name__ == "__main__":
    main()