#  CybroX-UserBot - telegram userbot
#  Copyright (C) 2025 CybroX UserBot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

import asyncio
import time
import datetime
import html
from pyrogram import Client, filters
from pyrogram.types import Message
import humanize

from utils.misc import modules_help, prefix
from utils.scripts import edit_or_reply
from utils.db import db


@Client.on_message(filters.command("afk", prefix) & filters.me)
async def afk_cmd(client: Client, message: Message):
    """Set your status as AFK (Away From Keyboard)"""
    # Get reason if provided
    if len(message.command) > 1:
        reason = message.text.split(None, 1)[1]
    else:
        reason = "No reason specified"
    
    # Save AFK info to database
    db.set("afk", "afk_status", True)
    db.set("afk", "afk_reason", reason)
    db.set("afk", "afk_time", time.time())
    db.set("afk", "afk_mentions", [])
    
    # Update user's first name to indicate AFK status
    # Only if setting is enabled
    if db.get("afk", "rename_profile", True):
        me = await client.get_me()
        try:
            if not me.first_name.startswith("[AFK] "):
                # Save original name to restore later
                db.set("afk", "original_first_name", me.first_name)
                await client.update_profile(first_name=f"[AFK] {me.first_name}")
        except Exception as e:
            # Don't let renaming issues stop AFK functionality
            pass
    
    # Send AFK notification
    await edit_or_reply(
        message,
        f"<b>🌙 Going AFK</b>\n\n<b>Reason:</b> <i>{html.escape(reason)}</i>"
    )


@Client.on_message(filters.incoming & ~filters.bot & filters.private, group=10)
async def afk_private_handler(client: Client, message: Message):
    """Handle incoming private messages when AFK"""
    if not db.get("afk", "afk_status", False):
        return
    
    # Get AFK info
    afk_time = db.get("afk", "afk_time", 0)
    afk_reason = db.get("afk", "afk_reason", "No reason specified")
    
    # Calculate time difference
    time_diff = time.time() - afk_time
    time_humanized = humanize.naturaltime(datetime.timedelta(seconds=int(time_diff)))
    
    # Store message for later viewing
    mentions = db.get("afk", "afk_mentions", [])
    mentions.append({
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "first_name": message.from_user.first_name,
        "chat_id": message.chat.id,
        "message_id": message.id,
        "text": message.text or "[media or non-text message]",
        "time": time.time()
    })
    
    # Limit to last 50 mentions
    if len(mentions) > 50:
        mentions = mentions[-50:]
    
    db.set("afk", "afk_mentions", mentions)
    
    # Reply to the message
    try:
        await message.reply(
            f"<b>⚠️ I'm currently AFK</b>\n"
            f"<b>Last seen:</b> <i>{time_humanized}</i>\n"
            f"<b>Reason:</b> <i>{html.escape(afk_reason)}</i>\n\n"
            f"<i>I'll respond when I return.</i>"
        )
    except Exception:
        # Don't break on message reply failures
        pass


@Client.on_message(filters.incoming & ~filters.bot & filters.group, group=10)
async def afk_group_handler(client: Client, message: Message):
    """Handle mentions in groups when AFK"""
    if not db.get("afk", "afk_status", False):
        return
    
    # Only process if user is mentioned or message is a reply to the user
    if not (message.mentioned or 
            (message.reply_to_message and message.reply_to_message.from_user and 
             message.reply_to_message.from_user.is_self)):
        return
    
    # Get AFK info
    afk_time = db.get("afk", "afk_time", 0)
    afk_reason = db.get("afk", "afk_reason", "No reason specified")
    
    # Calculate time difference
    time_diff = time.time() - afk_time
    time_humanized = humanize.naturaltime(datetime.timedelta(seconds=int(time_diff)))
    
    # Store mention for later viewing
    mentions = db.get("afk", "afk_mentions", [])
    mentions.append({
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "first_name": message.from_user.first_name,
        "chat_title": message.chat.title,
        "chat_id": message.chat.id,
        "message_id": message.id,
        "text": message.text or "[media or non-text message]",
        "time": time.time()
    })
    
    # Limit to last 50 mentions
    if len(mentions) > 50:
        mentions = mentions[-50:]
    
    db.set("afk", "afk_mentions", mentions)
    
    # Reply to the message
    try:
        await message.reply(
            f"<b>⚠️ I'm currently AFK</b>\n"
            f"<b>Last seen:</b> <i>{time_humanized}</i>\n"
            f"<b>Reason:</b> <i>{html.escape(afk_reason)}</i>"
        )
    except Exception:
        # Don't break on message reply failures
        pass


@Client.on_message(filters.me & ~filters.edited, group=11)
async def unafk_handler(client: Client, message: Message):
    """Handle the user's return from AFK status"""
    # Skip commands
    if message.text and message.text.startswith(prefix):
        return
    
    # Skip the command itself
    if message.text and message.text.split()[0] == f"{prefix}afk":
        return
        
    if db.get("afk", "afk_status", False):
        # Calculate AFK time
        afk_time = db.get("afk", "afk_time", 0)
        time_diff = time.time() - afk_time
        time_humanized = humanize.naturaldelta(datetime.timedelta(seconds=int(time_diff)))
        
        # Restore original name if changed
        if db.get("afk", "rename_profile", True):
            try:
                me = await client.get_me()
                if me.first_name.startswith("[AFK] "):
                    original_name = db.get("afk", "original_first_name", me.first_name[6:])
                    await client.update_profile(first_name=original_name)
            except Exception:
                # Don't let renaming issues stop AFK functionality
                pass
        
        # Get mention count
        mentions = db.get("afk", "afk_mentions", [])
        mention_count = len(mentions)
        
        # Reset AFK status
        db.set("afk", "afk_status", False)
        
        # Notify about return
        try:
            await client.send_message(
                "me",
                f"<b>🌞 Welcome back! You are no longer AFK</b>\n\n"
                f"<b>Duration:</b> <i>{time_humanized}</i>\n"
                f"<b>Mentions:</b> <i>{mention_count}</i>\n\n"
                f"<i>Use <code>{prefix}afklog</code> to see messages received while AFK.</i>"
            )
        except Exception:
            # Don't break on message failures
            pass


@Client.on_message(filters.command(["afklog", "afkm", "mentions"], prefix) & filters.me)
async def afk_log_cmd(client: Client, message: Message):
    """View messages received while AFK"""
    mentions = db.get("afk", "afk_mentions", [])
    
    if not mentions:
        await edit_or_reply(message, "<b>📪 No messages received while you were AFK.</b>")
        return
    
    # Sort mentions by time (newest first)
    mentions.sort(key=lambda x: x.get("time", 0), reverse=True)
    
    output = "<b>📬 Messages received while AFK:</b>\n\n"
    counter = 0
    
    for mention in mentions:
        counter += 1
        # Format time
        mention_time = datetime.datetime.fromtimestamp(mention.get("time", 0)).strftime("%Y-%m-%d %H:%M:%S")
        
        # Private or group?
        if "chat_title" in mention:  # Group
            chat_info = f"<b>👥 Group:</b> {html.escape(mention['chat_title'])}\n"
        else:  # Private
            chat_info = "<b>👤 Private message</b>\n"
        
        # Compose message entry
        user_name = mention.get("first_name", "Unknown")
        if mention.get("username"):
            user_name += f" (@{mention['username']})"
            
        output += (
            f"<b>{counter}.</b> {html.escape(user_name)}\n"
            f"{chat_info}"
            f"<b>💬 Message:</b> <i>{html.escape(mention.get('text', '[No text]'))}</i>\n"
            f"<b>⏰ Time:</b> {mention_time}\n\n"
        )
        
        # Avoid message too long errors by splitting
        if len(output) > 3500:
            await client.send_message("me", output)
            output = "<b>📬 Messages continued:</b>\n\n"
    
    if output:
        await client.send_message("me", output)
    
    # Delete the command if in a group
    if message.chat.type != "private":
        await message.delete()
        await client.send_message(
            message.from_user.id,
            "<b>✅ AFK log sent to your Saved Messages.</b>"
        )
    else:
        await message.edit("<b>✅ AFK log sent to your Saved Messages.</b>")
        

@Client.on_message(filters.command("afkinfo", prefix) & filters.me)
async def afk_info_cmd(client: Client, message: Message):
    """Show current AFK settings"""
    is_afk = db.get("afk", "afk_status", False)
    rename_profile = db.get("afk", "rename_profile", True)
    
    text = "<b>⚙️ AFK Settings:</b>\n\n"
    text += f"<b>Current status:</b> {'🌙 AFK' if is_afk else '🌞 Not AFK'}\n"
    text += f"<b>Auto rename profile:</b> {'✅ Enabled' if rename_profile else '❌ Disabled'}\n"
    
    if is_afk:
        afk_time = db.get("afk", "afk_time", 0)
        afk_reason = db.get("afk", "afk_reason", "No reason specified")
        
        time_diff = time.time() - afk_time
        time_humanized = humanize.naturaldelta(datetime.timedelta(seconds=int(time_diff)))
        
        text += f"\n<b>AFK duration:</b> {time_humanized}\n"
        text += f"<b>AFK reason:</b> {html.escape(afk_reason)}\n"
        
        mentions = db.get("afk", "afk_mentions", [])
        text += f"<b>Messages received:</b> {len(mentions)}"
    
    await edit_or_reply(message, text)


@Client.on_message(filters.command(["toggleafkrename", "afkr"], prefix) & filters.me)
async def toggle_afk_rename_cmd(client: Client, message: Message):
    """Toggle automatic profile renaming during AFK"""
    current_setting = db.get("afk", "rename_profile", True)
    new_setting = not current_setting
    
    db.set("afk", "rename_profile", new_setting)
    
    if new_setting:
        await edit_or_reply(message, "<b>✅ Auto rename profile during AFK enabled.</b>")
    else:
        await edit_or_reply(message, "<b>❌ Auto rename profile during AFK disabled.</b>")


modules_help["afk"] = {
    "afk [reason]": "Set your status as AFK",
    "afklog": "View messages received while AFK",
    "afkm": "Alias for afklog command",
    "mentions": "Alias for afklog command",
    "afkinfo": "Show current AFK settings",
    "toggleafkrename": "Toggle automatic profile renaming during AFK",
    "afkr": "Alias for toggleafkrename command",
    "__category__": "utils"
}