# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# FINAL FUN.PY – STABLE (NO anime_react ERROR)

import random
import asyncio
import httpx
from telegram import Update
from telegram.ext import ContextTypes
from baka.utils import ensure_user_exists, format_money
from baka.database import users_collection

# --- FONT ---
def nezuko_style(text):
    mapping = str.maketrans(
        "abcdefghijklmnopqrstuvwxyz",
        "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    )
    return str(text).lower().translate(mapping)

# --- ID ---
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if update.message.reply_to_message:
        uid = update.message.reply_to_message.from_user.id
        await update.message.reply_text(
            f"👤 {nezuko_style('user id')}: {uid}\n👥 {nezuko_style('chat id')}: {chat_id}"
        )
    else:
        await update.message.reply_text(f"👥 {nezuko_style('chat id')}: {chat_id}")

# --- BRAIN ---
async def brain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text(nezuko_style("ʀᴇᴘʟʏ ᴛᴏ sᴏᴍᴇᴏɴᴇ"))
    name = update.message.reply_to_message.from_user.first_name
    iq = random.randint(0, 100)
    await update.message.reply_text(
        nezuko_style(f"ɪǫ ʟᴇᴠᴇʟ ᴏғ {name} ɪs {iq}%")
    )

# --- ANIME BASE ---
async def anime_base(update: Update, action: str):
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"https://nekos.best/api/v2/{action}")
            if r.status_code == 200:
                url = r.json()["results"][0]["url"]
                await update.message.reply_animation(url)
    except:
        pass

# --- ANIME COMMANDS ---
async def slap(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    await anime_base(update, "slap")

async def punch(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    await anime_base(update, "punch")

async def hug(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    await anime_base(update, "hug")

async def kiss(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    await anime_base(update, "kiss")

async def pat(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    await anime_base(update, "pat")

async def bite(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    await anime_base(update, "bite")

# --- DICE ---
async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = ensure_user_exists(update.effective_user)
    if not context.args:
        return await update.message.reply_text(nezuko_style("ᴜsᴀɢᴇ: /dice 100"))

    bet = int(context.args[0])
    if user["balance"] < bet:
        return await update.message.reply_text(nezuko_style("ɴᴏᴛ ᴇɴᴏᴜɢʜ ʙᴀʟᴀɴᴄᴇ"))

    msg = await context.bot.send_dice(update.effective_chat.id, emoji="🎲")
    await asyncio.sleep(3)

    if msg.dice.value > 3:
        users_collection.update_one(
            {"user_id": user["user_id"]}, {"$inc": {"balance": bet}}
        )
        await update.message.reply_text(nezuko_style(f"ʏᴏᴜ ᴡᴏɴ +{format_money(bet)}"))
    else:
        users_collection.update_one(
            {"user_id": user["user_id"]}, {"$inc": {"balance": -bet}}
        )
        await update.message.reply_text(nezuko_style(f"ʏᴏᴜ ʟᴏsᴛ -{format_money(bet)}"))

# --- SLOTS ---
async def slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = ensure_user_exists(update.effective_user)
    if user["balance"] < 100:
        return await update.message.reply_text(nezuko_style("ɴᴇᴇᴅ 100"))

    users_collection.update_one(
        {"user_id": user["user_id"]}, {"$inc": {"balance": -100}}
    )
    msg = await context.bot.send_dice(update.effective_chat.id, emoji="🎰")
    await asyncio.sleep(2)

    if msg.dice.value == 64:
        users_collection.update_one(
            {"user_id": user["user_id"]}, {"$inc": {"balance": 1000}}
        )
        await update.message.reply_text(nezuko_style("ᴊᴀᴄᴋᴘᴏᴛ +1000"))
    else:
        await update.message.reply_text(nezuko_style("ʟᴏsᴛ"))
