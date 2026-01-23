# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# FINAL FUN, GAMBLING & POWER PLUGIN - BAKA EDITION

import random
import html
import asyncio
import httpx
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.utils import ensure_user_exists, format_money
from baka.database import users_collection

# --- 🎨 SIMPLE FONT HELPER (NO MONOSPACE) ---
def nezuko_style(text):
    """Converts text to Small Caps ONLY (Simple Font)."""
    mapping = str.maketrans("abcdefghijklmnopqrstuvwxyz", "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ")
    return str(text).lower().translate(mapping)

# --- 🆔 INFO COMMAND (/id) ---
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
        msg = f"👤 {nezuko_style('replied user id')}: {target_id}\n👥 {nezuko_style('group id')}: {chat_id}"
    else:
        msg = f"👥 {nezuko_style('group id')}: {chat_id}"
    await update.message.reply_text(msg)

# --- 🧠 BRAIN/IQ COMMAND ---
async def brain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text(nezuko_style("ʀᴇᴘʟʏ ᴛᴏ sᴏᴍᴇᴏɴᴇ !"))
    
    target = update.message.reply_to_message.from_user.first_name
    iq = random.randint(0, 100)
    emoji = "😎" if iq >= 75 else "🤔" if iq >= 50 else "😐" if iq >= 25 else "🤡"
    await update.message.reply_text(nezuko_style(f"ɪǫ ʟᴇᴠᴇʟ ᴏғ {target} ɪs {iq}% {emoji}"))

# --- 🎭 1. ANIME REACTIONS (PAT, SLAP, HUG, ETC.) ---
async def anime_react(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends anime GIFs for pat, slap, hug, kiss, bite."""
    cmd = update.message.text.split()[0][1:].lower()
    api_url = f"https://nekos.best/api/v2/{cmd}"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(api_url)
            if resp.status_code == 200:
                url = resp.json()['results'][0]['url']
                await update.message.reply_animation(url)
    except: pass

# --- 🛡️ 2. ROAST MODE ---
ROASTS = [
    "ᴛᴜᴍʜᴀʀɪ sʜᴀᴋᴀʟ ᴅᴇᴋʜ ᴋᴇ ᴛᴏʜ ɢᴏᴏɢʟᴇ ʙʜɪ ᴋᴇʜᴛᴀ ʜᴀɪ 'ᴅɪᴅ ʏᴏᴜ ᴍᴇᴀɴ sᴏᴍᴇᴛʜɪɴɢ ʙᴇᴛᴛᴇʀ?'",
    "ᴛᴜᴍʜᴀʀɪ ʙᴜᴅᴅʜɪ ᴜᴛɴɪ ʜɪ ᴛᴇᴢ ʜᴀɪ ᴊɪᴛɴɪ 2005 ᴋɪ ɪɴᴛᴇʀɴᴇᴛ sᴘᴇᴇᴅ.",
    "ʙʜᴀɪ ᴛᴜᴍʜᴀʀᴇ ᴘᴀss ᴅɪᴍᴀɢ ʜᴀɪ, ʙᴀs ᴄʜᴀʟᴛᴀ ɴᴀʜɪ ʜᴀɪ."
]

async def roast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Roasts the target user."""
    target = update.message.reply_to_message.from_user.first_name if update.message.reply_to_message else "ʙʜᴀɪ"
    await update.message.reply_text(nezuko_style(f"{target}, {random.choice(ROASTS)}"))

# --- ✍️ 3. RANDOM SHAYARI ---
SHAYARIS = [
    "ᴋᴜᴄʜ ʜᴏsʜ ɴᴀʜɪ, ᴋᴜᴄʜ ᴋʜᴀʙᴀʀ ɴᴀʜɪ... ʙᴀᴋᴀ ᴋᴇ ʙɪɴᴀ ᴋᴏɪ ᴅᴀɢᴀʀ ɴᴀʜɪ! ✨",
    "ᴍᴜʜᴀʙʙᴀᴛ ᴋᴀ ɪᴍᴛᴇʜᴀᴀɴ ʙᴀʜᴜᴛ sᴀᴋʜᴛ ʜᴀɪ, ᴘᴀʀ ʙᴀᴋᴀ ᴋᴀ ᴘʏᴀᴀʀ ʜᴀʀ ᴡᴀǫᴛ ᴍᴀsᴛ ʜᴀɪ! 💖"
]

async def shayari(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a random BAKA style shayari."""
    await update.message.reply_text(nezuko_style(random.choice(SHAYARIS)))

# --- 🎲 GAMBLING: DICE & SLOTS (RESTORED LOGIC) ---
async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = ensure_user_exists(update.effective_user)
    if not context.args: return await update.message.reply_text(nezuko_style("ᴜsᴀɢᴇ: /dice 100"))
    
    try: bet = int(context.args[0])
    except: return await update.message.reply_text(nezuko_style("⚠️ ɪɴᴠᴀʟɪᴅ ᴀᴍᴏᴜɴᴛ"))
    
    if user['balance'] < bet: return await update.message.reply_text(nezuko_style("📉 ɪɴsᴜғғɪᴄɪᴇɴᴛ ʙᴀʟᴀɴᴄᴇ"))
    
    msg = await context.bot.send_dice(update.effective_chat.id, emoji='🎲')
    result = msg.dice.value 
    await asyncio.sleep(3)
    
    if result > 3:
        users_collection.update_one({"user_id": user["user_id"]}, {"$inc": {"balance": bet}})
        text = nezuko_style(f"🎲 ʀᴇsᴜʟᴛ: {result}\n🎉 ʏᴏᴜ ᴡᴏɴ! +{format_money(bet)}")
    else:
        users_collection.update_one({"user_id": user["user_id"]}, {"$inc": {"balance": -bet}})
        text = nezuko_style(f"🎲 ʀᴇsᴜʟᴛ: {result}\n💀 ʏᴏᴜ ʟᴏsᴛ! -{format_money(bet)}")
    await update.message.reply_text(text, reply_to_message_id=msg.message_id)

async def slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = ensure_user_exists(update.effective_user)
    if user['balance'] < 100: return await update.message.reply_text(nezuko_style("📉 ɴᴇᴇᴅ $100 ᴛᴏ sᴘɪɴ"))
    
    users_collection.update_one({"user_id": user["user_id"]}, {"$inc": {"balance": -100}})
    msg = await context.bot.send_dice(update.effective_chat.id, emoji='🎰')
    await asyncio.sleep(2)
    
    if msg.dice.value == 64:
        users_collection.update_one({"user_id": user["user_id"]}, {"$inc": {"balance": 1000}})
        text = nezuko_style("🎰 ᴊᴀᴄᴋᴘᴏᴛ! (777)\n🎉 ʏᴏᴜ ᴡᴏɴ $1,000!")
    else:
        text = nezuko_style("🎰 ʟᴏsᴛ! ʙᴇᴛᴛᴇʀ ʟᴜᴄᴋ ɴᴇxᴛ ᴛɪᴍᴇ")
    await update.message.reply_text(text, reply_to_message_id=msg.message_id)
