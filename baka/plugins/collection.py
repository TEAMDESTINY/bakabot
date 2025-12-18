# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Location: Supaul, Bihar 
# Intellectual Property of @WTF_Phantom.

import random
import httpx
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.database import groups_collection, users_collection
from baka.utils import ensure_user_exists, get_mention, stylize_text

# In-Memory Drop Storage
active_drops = {}
DROP_MESSAGE_COUNT = 100

WAIFU_NAMES = [
    ("Rem", "rem"), ("Ram", "ram"), ("Emilia", "emilia"), ("Asuna", "asuna"), 
    ("Zero Two", "zero two"), ("Makima", "makima"), ("Nezuko", "nezuko"),
    ("Hinata", "hinata"), ("Sakura", "sakura"), ("Mikasa", "mikasa"), 
    ("Yor", "yor"), ("Anya", "anya"), ("Power", "power")
]

# --- 🌸 SPAWN LOGIC ---
async def check_drops(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat: return
    chat = update.effective_chat
    if chat.type == "private": return

    # Increment message count atomically
    group = groups_collection.find_one_and_update(
        {"chat_id": chat.id}, {"$inc": {"msg_count": 1}}, upsert=True, return_document=True
    )
    
    if group.get("msg_count", 0) % DROP_MESSAGE_COUNT == 0:
        char = random.choice(WAIFU_NAMES)
        name, slug = char
        
        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(f"https://api.waifu.im/search?included_tags={slug}")
                url = r.json()['images'][0]['url'] if r.status_code == 200 else "https://telegra.ph/file/5e5480760e412bd402e88.jpg"
            except:
                url = "https://telegra.ph/file/5e5480760e412bd402e88.jpg"

        active_drops[chat.id] = name.lower()
        
        caption = (
            f"👧 <b>{stylize_text('A Waifu Appeared')}!</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"ɢυєss ʜєꝛ ηᴧϻє ᴛσ ᴄσʟʟєᴄᴛ ʜєꝛ!\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<i>Reply to this image with her name.</i>"
        )
        
        await update.message.reply_photo(
            photo=url,
            caption=caption,
            parse_mode=ParseMode.HTML
        )

# --- 🌸 COLLECTION LOGIC (FIXED CRASH) ---
async def collect_waifu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    msg = update.message
    
    # 🛑 CRITICAL FIX: Check if message exists and has text
    if not msg or not msg.text:
        return

    if chat.id not in active_drops: 
        return
    
    guess = msg.text.lower().strip()
    correct = active_drops[chat.id]
    
    if guess == correct:
        user = ensure_user_exists(msg.from_user)
        
        # Remove from active drops immediately to prevent double claim
        del active_drops[chat.id]
        
        rarity_list = ["Common"] * 50 + ["Rare"] * 30 + ["Epic"] * 15 + ["Legendary"] * 5
        rarity = random.choice(rarity_list)
        
        waifu_data = {
            "name": correct.title(), 
            "rarity": rarity, 
            "date": datetime.utcnow()
        }
        
        users_collection.update_one(
            {"user_id": user['user_id']}, 
            {"$push": {"waifus": waifu_data}}
        )
        
        response = (
            f"🎉 <b>{stylize_text('Collected')}!</b>\n\n"
            f"👤 {get_mention(user)} ᴄᴧυɢʜᴛ <b>{correct.title()}</b>!\n"
            f"🌟 <b>{stylize_text('Rarity')}:</b> {rarity}"
        )
        
        await msg.reply_text(response, parse_mode=ParseMode.HTML)
