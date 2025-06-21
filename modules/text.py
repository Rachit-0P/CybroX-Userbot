#  CybroX-UserBot - telegram userbot
#  Copyright (C) 2025 CybroX UserBot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import edit_or_reply


@Client.on_message(filters.command("type", prefix) & filters.me)
async def type_cmd(client: Client, message: Message):
    """Type message with a typing animation effect"""
    if len(message.command) < 2:
        await message.edit("<b>Provide some text to type!</b>")
        return
    
    orig_text = message.text.split(prefix + "type ", maxsplit=1)[1]
    text = orig_text
    tbp = ""  # to be printed
    typing_symbol = "▒"
    
    while tbp != orig_text:
        try:
            await message.edit(tbp + typing_symbol)
            await asyncio.sleep(0.1)  # 100 ms delay
            
            tbp = tbp + text[0]
            text = text[1:]
            
            await message.edit(tbp)
            await asyncio.sleep(0.1)
            
        except Exception as e:
            print(e)
            break


@Client.on_message(filters.command("mock", prefix) & filters.me)
async def mock_cmd(client: Client, message: Message):
    """Convert text to mOcK tExT"""
    if message.reply_to_message:
        text = message.reply_to_message.text
    elif len(message.command) > 1:
        text = message.text.split(prefix + "mock ", maxsplit=1)[1]
    else:
        await message.edit("<b>Provide some text to mock or reply to a message!</b>")
        return
    
    mock_text = ""
    for char in text:
        if char.isalpha():
            mock_text += char.upper() if random.random() > 0.5 else char.lower()
        else:
            mock_text += char
    
    await message.edit(mock_text)


@Client.on_message(filters.command("vapor", prefix) & filters.me)
async def vapor_cmd(client: Client, message: Message):
    """Convert text to vaporwave aesthetic (full-width characters)"""
    if message.reply_to_message:
        text = message.reply_to_message.text
    elif len(message.command) > 1:
        text = message.text.split(prefix + "vapor ", maxsplit=1)[1]
    else:
        await message.edit("<b>Provide some text to vaporize or reply to a message!</b>")
        return
    
    vapor_text = ""
    for char in text:
        if 0x21 <= ord(char) <= 0x7F:  # ASCII printable range
            vapor_text += chr(ord(char) + 0xFEE0)  # Convert to full-width
        elif char == " ":
            vapor_text += "　"  # Full-width space
        else:
            vapor_text += char
    
    await message.edit(vapor_text)


@Client.on_message(filters.command("zalgo", prefix) & filters.me)
async def zalgo_cmd(client: Client, message: Message):
    """Corrupt text with zalgo effect"""
    if message.reply_to_message:
        text = message.reply_to_message.text
    elif len(message.command) > 1:
        text = message.text.split(prefix + "zalgo ", maxsplit=1)[1]
    else:
        await message.edit("<b>Provide some text for zalgo or reply to a message!</b>")
        return
    
    # Combining diacritical marks for Zalgo effect
    zalgo_marks = [
        chr(code) for code in range(0x0300, 0x036F + 1)
    ]
    
    # Intensity
    intensity = min(max(random.randint(5, 15), 1), 30)
    
    zalgo_text = ""
    for char in text:
        zalgo_text += char
        if char.isalpha():
            zalgo_text += ''.join(random.choice(zalgo_marks) for _ in range(random.randint(1, intensity)))
    
    await message.edit(zalgo_text)


@Client.on_message(filters.command("reverse", prefix) & filters.me)
async def reverse_cmd(client: Client, message: Message):
    """Reverse the given text"""
    if message.reply_to_message:
        text = message.reply_to_message.text
    elif len(message.command) > 1:
        text = message.text.split(prefix + "reverse ", maxsplit=1)[1]
    else:
        await message.edit("<b>Provide some text to reverse or reply to a message!</b>")
        return
    
    reversed_text = text[::-1]
    await message.edit(reversed_text)


modules_help["text"] = {
    "type [text]": "Type text with typing animation effect",
    "mock [text]": "Convert text to mOcK tExT",
    "vapor [text]": "Convert text to vaporwave aesthetic (full-width characters)",
    "zalgo [text]": "Corrupt text with zalgo effect",
    "reverse [text]": "Reverse the given text",
    "__category__": "fun"
}