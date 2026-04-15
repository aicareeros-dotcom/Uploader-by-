import os
import re
import sys
import json
import time
import pytz
import asyncio
import requests
import subprocess
import random
from pyromod import listen
from pyrogram import Client, filters
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types.messages_and_media import message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, InputMediaPhoto

import globals
from logs import logging
from html_handler import register_html_handlers
from drm_handler import register_drm_handlers
from text_handler import register_text_handlers
from features import register_feature_handlers
from upgrade import register_upgrade_handlers
from commands import register_commands_handlers
from settings import register_settings_handlers
from broadcast import register_broadcast_handlers
from youtube_handler import register_youtube_handlers
from authorisation import register_authorisation_handlers
from vars import API_ID, API_HASH, BOT_TOKEN, OWNER, CREDIT, AUTH_USERS, TOTAL_USERS, cookies_file_path

# Initialize the bot
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Keyboard
keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("✨ Commands", callback_data="cmd_command")],
    [InlineKeyboardButton("💎 Features", callback_data="feat_command"),
     InlineKeyboardButton("⚙️ Settings", callback_data="setttings")],
    [InlineKeyboardButton("💳 Plans", callback_data="upgrade_command")],
    [InlineKeyboardButton(text="📞 Contact", url=f"tg://openmessage?user_id={OWNER}"),
     InlineKeyboardButton(text="🛠️ Repo", url="https://github.com/nikhilsainiop/saini-txt-direct")],
])

# Start Command
@bot.on_message(filters.command("start"))
async def start(bot, m: Message):
    user_id = m.chat.id
    if user_id not in TOTAL_USERS:
        TOTAL_USERS.append(user_id)

    user = await bot.get_me()

    if m.chat.id in AUTH_USERS:
        caption = (
            f"🌟 Welcome {m.from_user.first_name}! 🌟\n\n"
            f"Great! You are a premium member!\n"
            f"Use button: **✨ Commands** to get started 🌟\n\n"
            f"If you face any problem contact - [{CREDIT}](tg://openmessage?user_id={OWNER})\n"
        )
    else:
        caption = (
            f"🎉 Welcome {m.from_user.first_name} to DRM Bot! 🎉\n\n"
            f"**You are currently using the free version.** 🆓\n\n"
            f"Press /id to get started.\n\n"
            f"💬 Contact: [{CREDIT}](tg://openmessage?user_id={OWNER})\n"
        )

    await bot.send_photo(
        chat_id=m.chat.id,
        photo="https://iili.io/KuCBoV2.jpg",
        caption=caption,
        reply_markup=keyboard
    )

# Back button
@bot.on_callback_query(filters.regex("back_to_main_menu"))
async def back_to_main_menu(client, callback_query):
    user_id = callback_query.from_user.id
    first_name = callback_query.from_user.first_name

    caption = f"✨ **Welcome [{first_name}](tg://user?id={user_id}) in My uploader bot**"

    await callback_query.message.edit_media(
        InputMediaPhoto(
            media="https://envs.sh/GVI.jpg",
            caption=caption
        ),
        reply_markup=keyboard
    )
    await callback_query.answer()

# ID command
@bot.on_message(filters.command(["id"]))
async def id_command(client, message: Message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Send to Owner", url=f"tg://openmessage?user_id={OWNER}")]
    ])
    chat_id = message.chat.id
    text = f"<blockquote><b>Chat ID:</b></blockquote>\n`{chat_id}`"

    await message.reply_text(text, reply_markup=keyboard)

# Info command
@bot.on_message(filters.private & filters.command(["info"]))
async def info(bot: Client, update: Message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="📞 Contact", url=f"tg://openmessage?user_id={OWNER}")]
    ])

    text = (
        f"╭──────────────╮\n"
        f"│✨ **Your Info**\n"
        f"├ Name: `{update.from_user.first_name}`\n"
        f"├ Username: @{update.from_user.username}\n"
        f"├ ID: `{update.from_user.id}`\n"
        f"╰──────────────╯"
    )

    await update.reply_text(text, reply_markup=keyboard)

# Logs command
@bot.on_message(filters.command(["logs"]))
async def send_logs(client: Client, m: Message):
    try:
        if not os.path.exists("logs.txt"):
            with open("logs.txt", "w") as f:
                f.write("No logs yet.")

        await m.reply_document("logs.txt")
    except Exception as e:
        await m.reply_text(f"Error: {e}")

# Reset command
@bot.on_message(filters.command(["reset"]))
async def restart_handler(_, m):
    if m.chat.id != OWNER:
        return
    await m.reply_text("Restarting...")
    os.execl(sys.executable, sys.executable, *sys.argv)

# Stop command
@bot.on_message(filters.command("stop") & filters.private)
async def cancel_handler(client: Client, m: Message):
    if m.chat.id not in AUTH_USERS:
        await m.reply_text("❌ Not Authorized")
        return

    if globals.processing_request:
        globals.cancel_requested = True
        await m.reply_text("Stopping...")
    else:
        await m.reply_text("No active process")

# Register handlers
register_text_handlers(bot)
register_html_handlers(bot)
register_feature_handlers(bot)
register_settings_handlers(bot)
register_upgrade_handlers(bot)
register_commands_handlers(bot)
register_broadcast_handlers(bot)
register_youtube_handlers(bot)
register_authorisation_handlers(bot)
register_drm_handlers(bot)

# Notify owner
def notify_owner():
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": OWNER, "text": "Bot Restarted ✅"}
        )
    except:
        pass

# Set commands
def reset_and_set_commands():
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands",
            json={"commands": [{"command": "start", "description": "Start Bot"}]}
        )
    except:
        pass

# MAIN FIX (IMPORTANT)
if __name__ == "__main__":
    if not os.path.exists("logs.txt"):
        with open("logs.txt", "w") as f:
            f.write("Bot started...\n")

    reset_and_set_commands()
    notify_owner()
    bot.run()
