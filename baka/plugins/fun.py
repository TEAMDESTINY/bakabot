# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# FINAL POWER PLUGIN - ALL FEATURES SYNCED (NO CRASH)

import random
import asyncio
import httpx
from telegram import Update
from telegram.ext import ContextTypes
from baka.utils import ensure_user_exists, format_money
from baka.database import users_collection

# --- 🎨 SIMPLE FONT HELPER ---
def nezuko_style(text):
    """Converts text to Small Caps ONLY (Simple Font)."""
    mapping = str.maketrans("abcdefghijklmnopqrstuvwxyz", "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ")
    return str(text).lower().translate(mapping)

# --- 🆔 INFO & BRAIN ---
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
        msg = f"👤 {nezuko_style('replied user id')}: {target_id}\n👥 {nezuko_style('group id')}: {chat_id}"
    else:
        msg = f"👥 {nezuko_style('group id')}: {chat_id}"
    await update.message.reply_text(msg)

async def brain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text(nezuko_style("ʀᴇᴘʟʏ ᴛᴏ sᴏᴍᴇᴏɴᴇ !"))
    target = update.message.reply_to_message.from_user.first_name
    iq = random.randint(0, 100)
    emoji = "😎" if iq >= 75 else "🤡"
    await update.message.reply_text(nezuko_style(f"ɪǫ ʟᴇᴠᴇʟ ᴏғ {target} ɪs {iq}% {emoji}"))

# --- 🎭 ANIME REACTIONS (FIXED INDIVIDUAL FUNCTIONS) ---
async def anime_base(update, cmd):
    """Internal helper to fetch anime GIFs."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"https://nekos.best/api/v2/{cmd}")
            if resp.status_code == 200:
                url = resp.json()['results'][0]['url']
                await update.message.reply_animation(url)
    except: pass

async def slap(update: Update, context: ContextTypes.DEFAULT_TYPE): await anime_base(update, "slap")
async def punch(update: Update, context: ContextTypes.DEFAULT_TYPE): await anime_base(update, "punch")
async def hug(update: Update, context: ContextTypes.DEFAULT_TYPE): await anime_base(update, "hug")
async def kiss(update: Update, context: ContextTypes.DEFAULT_TYPE): await anime_base(update, "kiss")
async def pat(update: Update, context: ContextTypes.DEFAULT_TYPE): await anime_base(update, "pat")
async def bite(update: Update, context: ContextTypes.DEFAULT_TYPE): await anime_base(update, "bite")

# --- 🛡️ ROAST MODE (AS REQUESTED) ---
ROASTS = [
    "ᴛᴜᴍʜᴀʀɪ sʜᴀᴋᴀʟ ᴅᴇᴋʜ ᴋᴇ ᴛᴏʜ ɢᴏᴏɢʟᴇ ʙʜɪ ᴋᴇʜᴛᴀ ʜᴀɪ 'ᴅɪᴅ ʏᴏᴜ ᴍᴇᴀɴ sᴏᴍᴇᴛʜɪɴɢ ʙᴇᴛᴛᴇʀ?'",
    "ᴛᴜᴍʜᴀʀɪ ʙᴜᴅᴅʜɪ ᴜᴛɴɪ ʜɪ ᴛᴇᴢ ʜᴀɪ ᴊɪᴛɴɪ 2005 ᴋɪ ɪɴᴛᴇʀɴᴇᴛ sᴘᴇᴇᴅ.",
    "ʙʜᴀɪ ᴛᴜᴍʜᴀʀᴇ ᴘᴀss ᴅɪᴍᴀɢ ʜᴀɪ, ʙᴀs ᴄʜᴀʟᴛᴀ ɴᴀʜɪ ʜᴀɪ.",
    "ᴀɢᴀʀ ᴄʜᴜᴘ ʀᴇʜɴᴇ ᴋᴇ ᴘᴀɪsᴇ ᴍɪʟᴛᴇ ᴛᴏʜ ᴛᴜᴍ ᴀʙ ᴛᴀᴋ ᴀᴍʙᴀɴɪ ᴋᴏ ᴋʜᴀʀᴇᴇᴅ ʟᴇᴛᴇ."
]

async def roast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message.reply_to_message.from_user.first_name if update.message.reply_to_message else "ʙʜᴀɪ"
    await update.message.reply_text(nezuko_style(f"{target}, {random.choice(ROASTS)}"))

# --- ✍️ RANDOM SHAYARI (AS REQUESTED) ---
SHAYARIS = [
    "ᴋᴜᴄʜ ʜᴏsʜ ɴᴀʜɪ, ᴋᴜᴄʜ ᴋʜᴀʙᴀʀ ɴᴀʜɪ... ʙᴀᴋᴀ ᴋᴇ ʙɪɴᴀ ᴋᴏɪ ᴅᴀɢᴀʀ ɴᴀʜɪ! ✨",
    "ᴍᴜʜᴀʙʙᴀᴛ ᴋᴀ ɪᴍᴛᴇʜᴀᴀɴ ʙᴀʜᴜᴛ sᴀᴋʜᴛ ʜᴀɪ, ᴘᴀʀ ʙᴀᴋᴀ ᴋᴀ ᴘʏᴀᴀʀ ʜᴀʀ ᴡᴀǫᴛ ᴍᴀsᴛ ʜᴀɪ! 💖",
    "ᴅɪʟ ᴅɪʏᴀ ᴛʜᴀ ᴛᴜᴍʜᴇɪɴ ᴀɪsʜ ᴋᴀʀɴᴇ ᴋᴏ, ᴛᴜᴍɴᴇ ᴛᴏʜ ʀᴏʙ ᴋᴀʀ ʟɪʏᴀ! 💸"
]

async def shayari(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(nezuko_style(random.choice(SHAYARIS)))

# --- 🎲 GAMBLING (RESTORED) ---
async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = ensure_user_exists(update.effective_user)
    if not context.args: return await update.message.reply_text(nezuko_style("ᴜsᴀɢᴇ: /dice 100"))
    try:
        bet = int(context.args[0])
        if user['balance'] < bet: return await update.message.reply_text(nezuko_style("📉 ɪɴsᴜғғɪᴄɪᴇɴᴛ ʙᴀʟᴀɴᴄᴇ"))
        msg = await context.bot.send_dice(update.effective_chat.id, emoji='🎲')
        await asyncio.sleep(3)
        if msg.dice.value > 3:
            users_collection.update_one({"user_id": user["user_id"]}, {"$inc": {"balance": bet}})
            await update.message.reply_text(nezuko_style(f"🎉 ʏᴏᴜ ᴡᴏɴ! +{format_money(bet)}"))
        else:
            users_collection.update_one({"user_id": user["user_id"]}, {"$inc": {"balance": -bet}})
            await update.message.reply_text(nezuko_style(f"💀 ʏᴏᴜ ʟᴏsᴛ! -{format_money(bet)}"))
    except: pass

async def slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = ensure_user_exists(update.effective_user)
    if user['balance'] < 100: return await update.message.reply_text(nezuko_style("📉 ɴᴇᴇᴅ $100"))
    users_collection.update_one({"user_id": user["user_id"]}, {"$inc": {"balance": -100}})
    msg = await context.bot.send_dice(update.effective_chat.id, emoji='🎰')
    await asyncio.sleep(2)
    if msg.dice.value == 64:
        users_collection.update_one({"user_id": user["user_id"]}, {"$inc": {"balance": 1000}})
        await update.message.reply_text(nezuko_style("🎰 ᴊᴀᴄᴋᴘᴏᴛ! 🎉 +$1,000"))
    else: await update.message.reply_text(nezuko_style("🎰 ʟᴏsᴛ!"))
