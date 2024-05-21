import os
import json
import pyfiglet
from pyrogram import Client, filters
from pyrogram.types import ReplyKeyboardMarkup
import random
import time
import asyncio

font = pyfiglet.Figlet(font='standard')
print(font.renderText('FibonaSource'))
print("by @fibonasource on Telegram.")

try:
    import os
    import json
    import pyfiglet
    from pyrogram import Client, filters
    from pyrogram.types import ReplyKeyboardMarkup
    import asyncio
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyfiglet", "pyrogram", "asyncio"])

API_ID = 123
API_HASH = "fibonasource x irkral"
BOT_TOKEN = "xd"

app = Client("fibonasource", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# File size limit
file_size_limit = 1024  # 1 GB
# User file size limit
user_file_size_limit = 2048  # 2 GB
ADMIN_ID = "fibonadev"
HOST = "https://kittymc.ir/ups"
LOG_ID = 2459778
chat_ids = {}
if os.path.exists("chat_ids.json"):
    with open("chat_ids.json", "r") as f:
        chat_ids = json.load(f)
if not os.path.exists("ups"):
    os.makedirs("ups")

# Start command handler
@app.on_message(filters.command("start"))
async def start_command(client, message):
    chat_id = message.chat.id
    username = message.from_user.username
    if str(chat_id) not in chat_ids:
        chat_ids[str(chat_id)] = {"file_size_limit": user_file_size_limit}
        with open("chat_ids.json", "w") as f:
            json.dump(chat_ids, f)

    await message.reply(f"Welcome!\nThis is the file to link conversion bot!\nSend your file and I'll upload it for you.\nAllowed file size: {file_size_limit} MB", reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            ["My Account"],
            ["Support"]
        ],
        resize_keyboard=True
    ))

# Account button handler
@app.on_message(filters.regex('^My Account$'))
async def handle_account(client, message):
    chat_id = message.chat.id
    username = message.from_user.username
    size_limit = chat_ids[str(chat_id)]["file_size_limit"]
    await message.reply(f"CHAT ID: {chat_id}\nUSERNAME: @{username}\nRemaining file size: {size_limit} MB\nAllowed file size: {file_size_limit} MB")

# Support button handler
@app.on_message(filters.regex('^Support$'))
async def handle_support(client, message):
    await message.reply(f"Bot support: @{ADMIN_ID}")

# Media file handler
@app.on_message(filters.document | filters.photo | filters.video)
async def handle_media(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username
    if str(chat_id) not in chat_ids:
        chat_ids[str(chat_id)] = {"file_size_limit": file_size_limit}
        with open("chat_ids.json", "w") as f:
            json.dump(chat_ids, f)

    if message.document:
        file_name = message.document.file_name
        file_size = message.document.file_size
        file_type = os.path.splitext(file_name)[1][1:].lower()
    elif message.photo:
        file_name = f"{message.photo.file_unique_id}.jpg"
        file_size = message.photo.file_size
        file_type = "jpg"
    elif message.video:
        file_name = f"{message.video.file_unique_id}.mp4"
        file_size = message.video.file_size
        file_type = "mp4"
    else:
        await message.reply("Sorry, the file format is not allowed.")
        return

    allowed_types = ["py", "html", "php", "json", "css", "js"]
    if file_type.lower() in allowed_types:
        await message.reply("The file format is not allowed.")
        return
    file_size_mb = file_size / 1024 / 1024
    if file_size_mb > chat_ids[str(chat_id)]["file_size_limit"]:
        await message.reply(f"The file size {file_size_mb:.2f} MB exceeds the allowed limit of {chat_ids[str(chat_id)]['file_size_limit']} MB.")
        return
    if file_size_mb > file_size_limit:
        await message.reply(f"The maximum allowed file size is {file_size_limit} MB.")
        return
    else:
        file_path = os.path.join("ups", file_name)
    await message.reply(
        text=f"File name: {file_name}\nStatus: Downloading\n"
    )
    downloaded = await message.download(file_path)
    original_size = file_size
    if downloaded == original_size:
        await app.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.id + 1 ,
            text=f"File name: {file_name}\nStatus: Successful\nDownload link: {HOST}/{os.path.basename(file_path)}"
        )
    else:
        os.remove(file_path)
        await app.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.id + 1,
            text=f"File name: {file_name}\nStatus: Failed"
        )

    await app.send_message(LOG_ID, f"User {chat_id} with @{username} uploaded {HOST}/{os.path.basename(file_path)}")

    file_size_mb = file_size / (1024 * 1024)
    if str(chat_id) in chat_ids:
        chat_ids[str(chat_id)]["file_size_limit"] -= file_size_mb
    else:
        chat_ids[str(chat_id)] = {"file_size_limit": file_size_limit - file_size_mb}
    with open("chat_ids.json", "w") as f:
        json.dump(chat_ids, f)

app.run()