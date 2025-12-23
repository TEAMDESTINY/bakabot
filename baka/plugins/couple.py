# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Couple Plugin - Custom MP4 Links & Clickable Mentions

import random
import html
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatType
from baka.utils import stylize_text
from baka.database import users_collection

# Temporary storage for 5-minute lock
couple_cache = {}

# --- 🎬 CUSTOM MP4 VIDEO LINKS (Aapke Links) ---
COUPLE_VIDEOS = [
    "https://files.catbox.moe/a9gpqj.mp4",
    "https://files.catbox.moe/i1r03f.mp4",
    "https://files.catbox.moe/pqstlj.mp4",
    "https://files.catbox.moe/dlf5be.mp4"
]

async def couple(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == ChatType.PRIVATE:
        return await update.message.reply_text("❌ Groups only!")

    now = datetime.utcnow()
    chat_id = chat.id

    # 1. 5-Minute Cache Check
    if chat_id in couple_cache:
        data = couple_cache[chat_id]
        if now < data['expiry']:
            rem = int((data['expiry'] - now).total_seconds())
            return await update.message.reply_text(
                f"💞 <b>{stylize_text('Still Locked')}</b>\n\n"
                f"{data['couple_str']}\n\n"
                f"⏳ <i>New couple in {rem // 60}m {rem % 60}s!</i>",
                parse_mode=ParseMode.HTML
            )

    # 2. Pick Random Users from Database
    all_users = list(users_collection.find({"chat_id": chat_id}).limit(100))
    if len(all_users) < 2:
        all_users = list(users_collection.find().limit(100))

    if len(all_users) < 2:
        return await update.message.reply_text("⚠️ Bot doesn't have enough user data in this group.")

    c1, c2 = random.sample(all_users, 2)
    love_per = random.randint(40, 100)
    
    # 3. Create Clickable Mentions (HTML Escape for Safety)
    m1_name = html.escape(c1.get("name", "User1"))
    m2_name = html.escape(c2.get("name", "User2"))
    
    m1 = f'<a href="tg://user?id={c1["user_id"]}">{m1_name}</a>'
    m2 = f'<a href="tg://user?id={c2["user_id"]}">{m2_name}</a>'
    
    couple_text = f"{m1} ❤️ {m2}\n✨ <b>Love Meter:</b> <code>{love_per}%</code>"

    # 4. Save to Cache for 5 Minutes
    couple_cache[chat_id] = {
        "couple_str": couple_text,
        "expiry": now + timedelta(minutes=5)
    }

    # 5. Send with Custom Animation
    video_url = random.choice(COUPLE_VIDEOS)
    caption = (
        f"👩‍❤️‍👨 <b>{stylize_text('COUPLE OF THE MOMENT')}</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{couple_text}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💘 <i>This pair is locked for 5 minutes!</i>"
    )

    try:
        # MP4 links as animation (autoplay/loop in Telegram)
        await update.message.reply_animation(
            animation=video_url,
            caption=caption,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        # Fallback if video fails to load
        await update.message.reply_text(caption, parse_mode=ParseMode.HTML)
