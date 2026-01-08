# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Couple Plugin with Dynamic Image Generation (PIL)

import os
import random
import html
from datetime import datetime, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatType

from baka.utils import stylize_text
from baka.database import users_collection

# --- Path Settings ---
ASSETS = Path("baka/assets")
BG_PATH = ASSETS / "couple.png" # Place your couple.jpg/png here
TEMP_DIR = Path("temp_couples")

if not TEMP_DIR.exists():
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Temporary storage for 5-minute lock
couple_cache = {}

def get_today():
    return datetime.now().strftime("%d/%m/%Y")

def get_tomorrow():
    return (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")

async def get_user_photo(bot, user_id):
    """Downloads user profile photo and returns a circular PIL image."""
    try:
        photos = await bot.get_user_profile_photos(user_id, limit=1)
        if photos.total_count > 0:
            file = await bot.get_file(photos.photos[0][-1].file_id)
            path = TEMP_DIR / f"{user_id}.png"
            await file.download_to_drive(path)
            
            img = Image.open(path).convert("RGBA").resize((486, 486))
            mask = Image.new("L", (486, 486), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 486, 486), fill=255)
            
            output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
            output.putalpha(mask)
            
            if path.exists():
                os.remove(path)
            return output
    except Exception:
        pass
    # Fallback if no photo
    return Image.new("RGBA", (486, 486), (200, 200, 200, 255))

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
            msg = (
                f"💞 <b>{stylize_text('Still Locked')}</b>\n\n"
                f"{data['couple_str']}\n\n"
                f"⏳ <i>New couple in {rem // 60}m {rem % 60}s!</i>"
            )
            return await update.message.reply_photo(photo=data['img_path'], caption=msg, parse_mode=ParseMode.HTML)

    # 2. Pick Random Users from Database
    all_users = list(users_collection.find({"chat_id": chat_id}).limit(100))
    if len(all_users) < 2:
        all_users = list(users_collection.find().limit(100))

    if len(all_users) < 2:
        return await update.message.reply_text("⚠️ Not enough user data in this group.")

    c1, c2 = random.sample(all_users, 2)
    
    # 3. Generate Image
    if not BG_PATH.exists():
        return await update.message.reply_text("❌ Background image missing in assets!")

    base = Image.open(BG_PATH).convert("RGBA")
    p1 = await get_user_photo(context.bot, c1["user_id"])
    p2 = await get_user_photo(context.bot, c2["user_id"])

    # Coordinates based on your frame circles
    base.paste(p1, (410, 500), p1)
    base.paste(p2, (1395, 500), p2)

    out_path = TEMP_DIR / f"final_{chat_id}.png"
    base.save(out_path)

    # 4. Create Mentions
    m1_name = html.escape(c1.get("name", "User1"))
    m2_name = html.escape(c2.get("name", "User2"))
    m1 = f'<a href="tg://user?id={c1["user_id"]}">{m1_name}</a>'
    m2 = f'<a href="tg://user?id={c2["user_id"]}">{m2_name}</a>'
    
    couple_text = f"{m1} 💞 {m2}"

    # 5. Cache Data
    couple_cache[chat_id] = {
        "couple_str": couple_text,
        "img_path": str(out_path),
        "expiry": now + timedelta(minutes=5)
    }

    # 6. Final Caption
    caption = (
        f"👩‍❤️‍👨 <b>{stylize_text('COUPLE OF THE MOMENT')}</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💌 <b>Today's Couple:</b>\n"
        f"⤷ {couple_text}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"📅 <b>Next Selection:</b> <code>{get_tomorrow()}</code>\n"
        "💘 <i>Tag your crush — you might be next!</i>"
    )

    await update.message.reply_photo(
        photo=str(out_path),
        caption=caption,
        parse_mode=ParseMode.HTML
    )
