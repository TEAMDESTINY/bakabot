# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Couple Plugin with Group Admin/Member Sync & Image Generation

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
BG_PATH = ASSETS / "couple.jpg"  # Ensure your background is named exactly couple.jpg
TEMP_DIR = Path("temp_couples")

if not TEMP_DIR.exists():
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Cache to keep the same couple for 24 hours per group
couple_cache = {}

def get_today_date():
    return datetime.now().strftime("%d/%m/%Y")

def get_tomorrow_date():
    return (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")

async def get_circular_avatar(bot, user_id):
    """Downloads user profile photo and converts it to a circular PIL image."""
    try:
        photos = await bot.get_user_profile_photos(user_id, limit=1)
        if photos.total_count > 0:
            file = await bot.get_file(photos.photos[0][-1].file_id)
            path = TEMP_DIR / f"avatar_{user_id}.png"
            await file.download_to_drive(path)
            
            # Processing the image to 486x486 circle
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
    # Gray fallback circle if user has no photo
    return Image.new("RGBA", (486, 486), (220, 220, 220, 255))

async def couple(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == ChatType.PRIVATE:
        return await update.message.reply_text("❌ This command only works in groups.")

    today = get_today_date()
    chat_id = chat.id

    # 1. 24-Hour Cache Check (Selection stays same for the day)
    if chat_id in couple_cache and couple_cache[chat_id]['date'] == today:
        data = couple_cache[chat_id]
        return await update.message.reply_photo(
            photo=data['img_path'], 
            caption=data['caption'], 
            parse_mode=ParseMode.HTML
        )

    # 2. Get Group Members from DB
    # We fetch users who have been seen in this specific group
    members = list(users_collection.find({"seen_groups": chat_id}))
    
    if len(members) < 2:
        # Fallback if group tracking is fresh
        members = list(users_collection.find().limit(50))

    if len(members) < 2:
        return await update.message.reply_text("⚠️ Not enough members found in my database for this group.")

    # 3. Pick Two Random Distinct Members
    c1_db, c2_db = random.sample(members, 2)
    
    # 4. Generate Image
    if not BG_PATH.exists():
        return await update.message.reply_text("❌ Background 'couple.jpg' missing in baka/assets/ folder!")

    # Load Background
    base = Image.open(BG_PATH).convert("RGBA")
    
    # Download and process Avatars
    p1_img = await get_circular_avatar(context.bot, c1_db["user_id"])
    p2_img = await get_circular_avatar(context.bot, c2_db["user_id"])

    # Paste Avatars onto the frame circles
    # Coordinates (x, y) set to match the pink template circles
    base.paste(p1_img, (200, 315), p1_img) # Left circle
    base.paste(p2_img, (600, 315), p2_img) # Right circle

    final_img_path = TEMP_DIR / f"couple_final_{chat_id}.png"
    base.save(final_img_path)

    # 5. Formatting Mentions and Caption
    m1_name = html.escape(c1_db.get("name", "User1"))
    m2_name = html.escape(c2_db.get("name", "User2"))
    m1 = f'<a href="tg://user?id={c1_db["user_id"]}">{m1_name}</a>'
    m2 = f'<a href="tg://user?id={c2_db["user_id"]}">{m2_name}</a>'
    
    caption = (
        "<b>TODAY'S COUPLE OF THE DAY:</b>\n\n"
        f"💞 {m1} + {m2} = ❤️\n\n"
        f"<b>NEXT COUPLES WILL BE SELECTED ON {get_tomorrow_date()}!!</b>"
    )

    # 6. Save to Cache and Send
    couple_cache[chat_id] = {
        "date": today,
        "img_path": str(final_img_path),
        "caption": caption
    }

    await update.message.reply_photo(
        photo=str(final_img_path),
        caption=caption,
        parse_mode=ParseMode.HTML
    )
