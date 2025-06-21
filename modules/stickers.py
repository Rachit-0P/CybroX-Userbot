#  CybroX-UserBot - telegram userbot
#  Copyright (C) 2025 CybroX UserBot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

import io
import os
import math
import asyncio
import random
from typing import Optional, Tuple, Union
from PIL import Image

from pyrogram import Client, filters, errors
from pyrogram.types import Message, StickerSet
from pyrogram.raw.functions.messages import GetStickerSet
from pyrogram.raw.types import InputStickerSetShortName

from utils.misc import modules_help, prefix
from utils.scripts import edit_or_reply, with_reply
from utils.db import db


async def resize_image(image: bytes, is_sticker: bool = False) -> bytes:
    """Resize image to sticker-friendly size"""
    image = Image.open(io.BytesIO(image))
    
    # Handle RGBA vs RGB
    if image.mode == "RGBA":
        mode = "RGBA"
    else:
        mode = "RGB"
        image = image.convert("RGB")
    
    # Calculate dimensions
    size = 512
    width, height = image.size
    
    # Preserve aspect ratio within Telegram's requirements
    if width > height:
        new_width = size
        new_height = int(height * (size / width))
    else:
        new_height = size
        new_width = int(width * (size / height))
        
    image = image.resize((new_width, new_height))
    
    # Create centered image
    new_image = Image.new(mode, (size, size), (0, 0, 0, 0))
    x_offset = (size - new_width) // 2
    y_offset = (size - new_height) // 2
    new_image.paste(image, (x_offset, y_offset), image if mode == "RGBA" else None)
    
    # Convert to bytes
    output = io.BytesIO()
    if is_sticker:
        new_image.save(output, format="WEBP")
    else:
        new_image.save(output, format="PNG")
    output.seek(0)
    
    return output.getvalue()


@Client.on_message(filters.command("kang", prefix) & filters.me)
async def kang_cmd(client: Client, message: Message):
    """Add sticker to your pack"""
    msg = await edit_or_reply(message, "<b>🔄 Processing sticker...</b>")
    
    # Check for necessary elements (replied message or attachment)
    replied = message.reply_to_message
    if not replied:
        await msg.edit("<b>❌ Reply to a sticker or image to kang it!</b>")
        await asyncio.sleep(3)
        await msg.delete()
        return
    
    # Get sticker pack details from user's settings or defaults
    user = await client.get_me()
    pack_prefix = db.get("stickers", "pack_prefix", "CybroX_")
    max_stickers = 120
    
    # Process media based on type
    try:
        if replied.sticker:
            # Handle sticker
            file_id = replied.sticker.file_id
            emoji = replied.sticker.emoji if replied.sticker.emoji else "🤔"
            is_animated = replied.sticker.is_animated
            is_video = replied.sticker.is_video
            
            # Set appropriate pack type
            if is_animated:
                pack_suffix = "_animated"
                pack_title = f"{user.first_name}'s Animated Pack"
            elif is_video:
                pack_suffix = "_video"
                pack_title = f"{user.first_name}'s Video Pack"
            else:
                pack_suffix = ""
                pack_title = f"{user.first_name}'s Pack"
            
            pack_name = f"{pack_prefix}{user.id}{pack_suffix}"
            
            # Download the sticker file
            await msg.edit("<b>🔄 Downloading sticker...</b>")
            file = await client.download_media(replied, in_memory=False)
            
        elif replied.photo or (replied.document and "image" in replied.document.mime_type):
            # Handle image
            emoji = "🤔"  # Default emoji
            pack_suffix = ""
            pack_name = f"{pack_prefix}{user.id}"
            pack_title = f"{user.first_name}'s Pack"
            
            # Check for custom emoji
            if len(message.command) > 1:
                emoji = message.command[1]
            
            # Download and resize the image
            await msg.edit("<b>🔄 Downloading and processing image...</b>")
            file = await client.download_media(replied, in_memory=False)
            
            with open(file, "rb") as f:
                image_data = f.read()
            
            image_data = await resize_image(image_data, True)
            
            # Save the resized image
            with open(file, "wb") as f:
                f.write(image_data)
            
        else:
            await msg.edit("<b>❌ Only stickers and images are supported!</b>")
            await asyncio.sleep(3)
            await msg.delete()
            return
        
        # Try to find or create the sticker pack
        await msg.edit("<b>🔍 Looking for sticker pack...</b>")
        
        # Try to get sticker set
        try:
            sticker_set = await client.invoke(
                GetStickerSet(
                    stickerset=InputStickerSetShortName(short_name=pack_name),
                    hash=0
                )
            )
            stickers_count = sticker_set.set.count
            await msg.edit(f"<b>📦 Found pack with {stickers_count}/{max_stickers} stickers</b>")
        except errors.StickersetInvalid:
            # Create a new pack if it doesn't exist
            await msg.edit("<b>🆕 Creating a new sticker pack...</b>")
            
            try:
                if replied.sticker and replied.sticker.is_animated:
                    await client.create_animated_sticker_set(
                        user_id=user.id,
                        title=pack_title,
                        short_name=pack_name,
                        stickers=[{"file": file, "emoji": emoji}]
                    )
                elif replied.sticker and replied.sticker.is_video:
                    await client.create_video_sticker_set(
                        user_id=user.id,
                        title=pack_title,
                        short_name=pack_name,
                        stickers=[{"file": file, "emoji": emoji}]
                    )
                else:
                    await client.create_sticker_set(
                        user_id=user.id,
                        title=pack_title,
                        short_name=pack_name,
                        stickers=[{"file": file, "emoji": emoji}]
                    )
                
                # Clean up and show success message
                if os.path.exists(file):
                    os.remove(file)
                
                await msg.edit(
                    f"<b>✅ Sticker added successfully!</b>\n\n"
                    f"<b>Pack:</b> <a href='https://t.me/addstickers/{pack_name}'>{pack_title}</a>"
                )
                return
                
            except Exception as e:
                await msg.edit(f"<b>❌ Error creating sticker pack:</b> {str(e)}")
                
                # Clean up
                if os.path.exists(file):
                    os.remove(file)
                return
        
        # Add sticker to existing pack
        await msg.edit("<b>➕ Adding sticker to pack...</b>")
        
        # Check if pack is full and create new one if needed
        if stickers_count >= max_stickers:
            # Create new pack with incremented number
            pack_number = 1
            while True:
                new_pack_name = f"{pack_prefix}{user.id}{pack_suffix}_{pack_number}"
                try:
                    await client.invoke(
                        GetStickerSet(
                            stickerset=InputStickerSetShortName(short_name=new_pack_name),
                            hash=0
                        )
                    )
                    pack_number += 1
                except errors.StickersetInvalid:
                    pack_name = new_pack_name
                    pack_title = f"{user.first_name}'s Pack {pack_number}"
                    break
            
            # Create a new pack with the incremented name
            await msg.edit(f"<b>🆕 Creating new pack {pack_number}...</b>")
            
            try:
                if replied.sticker and replied.sticker.is_animated:
                    await client.create_animated_sticker_set(
                        user_id=user.id,
                        title=pack_title,
                        short_name=pack_name,
                        stickers=[{"file": file, "emoji": emoji}]
                    )
                elif replied.sticker and replied.sticker.is_video:
                    await client.create_video_sticker_set(
                        user_id=user.id,
                        title=pack_title,
                        short_name=pack_name,
                        stickers=[{"file": file, "emoji": emoji}]
                    )
                else:
                    await client.create_sticker_set(
                        user_id=user.id,
                        title=pack_title,
                        short_name=pack_name,
                        stickers=[{"file": file, "emoji": emoji}]
                    )
            except Exception as e:
                await msg.edit(f"<b>❌ Error creating new pack:</b> {str(e)}")
                
                # Clean up
                if os.path.exists(file):
                    os.remove(file)
                return
        else:
            # Add to existing pack
            try:
                if replied.sticker and replied.sticker.is_animated:
                    await client.add_animated_sticker_to_set(
                        user_id=user.id,
                        short_name=pack_name,
                        sticker={"file": file, "emoji": emoji}
                    )
                elif replied.sticker and replied.sticker.is_video:
                    await client.add_video_sticker_to_set(
                        user_id=user.id,
                        short_name=pack_name,
                        sticker={"file": file, "emoji": emoji}
                    )
                else:
                    await client.add_sticker_to_set(
                        user_id=user.id,
                        short_name=pack_name,
                        sticker={"file": file, "emoji": emoji}
                    )
            except Exception as e:
                await msg.edit(f"<b>❌ Error adding sticker to pack:</b> {str(e)}")
                
                # Clean up
                if os.path.exists(file):
                    os.remove(file)
                return
        
        # Clean up and show success message
        if os.path.exists(file):
            os.remove(file)
        
        await msg.edit(
            f"<b>✅ Sticker added successfully!</b>\n\n"
            f"<b>Pack:</b> <a href='https://t.me/addstickers/{pack_name}'>{pack_title}</a>"
        )
        
    except Exception as e:
        await msg.edit(f"<b>❌ Error processing sticker:</b> {str(e)}")
        # Clean up on error
        if 'file' in locals() and os.path.exists(file):
            os.remove(file)


@Client.on_message(filters.command("stickerinfo", prefix) & filters.me)
async def sticker_info_cmd(client: Client, message: Message):
    """Get info about a sticker"""
    replied = message.reply_to_message
    
    if not replied or not replied.sticker:
        await edit_or_reply(message, "<b>❌ Reply to a sticker to get info!</b>")
        await asyncio.sleep(3)
        await message.delete()
        return
    
    sticker = replied.sticker
    
    info_text = "<b>🔍 Sticker Information</b>\n\n"
    info_text += f"<b>File ID:</b> <code>{sticker.file_id}</code>\n"
    info_text += f"<b>Emoji:</b> {sticker.emoji}\n"
    info_text += f"<b>Set ID:</b> <code>{sticker.set_id}</code>\n"
    info_text += f"<b>Is Animated:</b> {'✅' if sticker.is_animated else '❌'}\n"
    info_text += f"<b>Is Video:</b> {'✅' if sticker.is_video else '❌'}\n"
    info_text += f"<b>Width:</b> {sticker.width}px\n"
    info_text += f"<b>Height:</b> {sticker.height}px\n"
    info_text += f"<b>File Size:</b> {sticker.file_size / 1024} KB\n"
    
    await edit_or_reply(message, info_text)