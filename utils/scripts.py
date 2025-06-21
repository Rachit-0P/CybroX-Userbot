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

import asyncio
import os
import sys
import traceback
from typing import Union
from pyrogram.types import Message


async def edit_or_reply(message: Message, text: str, **kwargs):
    """Edit message if from self, reply otherwise"""
    if message.from_user and message.from_user.is_self:
        await message.edit(text, **kwargs)
    else:
        await message.reply(text, **kwargs)


def restart():
    """Restart the userbot"""
    os.execvp(sys.executable, [sys.executable, "main.py"])


def format_exc(e: Exception, **kwargs):
    """Format an exception to a string"""
    return "".join(
        traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)
    )


async def with_reply(message: Message) -> Union[Message, bool]:
    """Check if message has reply and return it"""
    reply = message.reply_to_message
    if not reply:
        await message.edit("<b>Reply to message is required</b>")
        await asyncio.sleep(3)
        await message.delete()
        return False
    return reply