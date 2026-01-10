# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Couple Plugin - Group Member Filter Fixed

import os
import random
import html
from datetime import datetime, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatType
from telegram.error import BadRequest

from baka.utils import stylize_text, get_mention
from baka.database import users_collection

# --- Path Settings ---
ASSETS = Path("baka/assets")
BG_PATH = ASSETS / "couple.png" 
TEMP_DIR = Path("temp_couples")

if not TEMP_DIR.exists():
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

couple_cache = {}

def get_today_date():
    return datetime.now().strftime("%d/%m/%Y")

async def get_circular_avatar(bot, user_id):
    try:
        photos = await bot.get_user_profile_photos(user_id, limit=1)
        if photos.total_count > 0:
            file = await bot.get_file(photos.photos[0][-1].file_id)
            path = TEMP_DIR / f"avatar_{user_id}.png"
            await file.download_to_drive(path)
            
            img = Image.open(path).convert("RGBA").resize((486, 486))
            mask = Image.new("L", (486, 486), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 486, 486), fill=255)
            
            output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
            output.putalpha(mask)
            
            if path.exists(): os.remove(path)
            return output
    except: pass
    return Image.new("RGBA", (486, 486), (220, 220, 220, 255))

async def couple(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == ChatType.PRIVATE:
        return await update.message.reply_text("❌ This command only works in groups.")

    today = get_today_date()
    chat_id = chat.id

    if chat_id in couple_cache and couple_cache[chat_id]['date'] == today:
        data = couple_cache[chat_id]
        return await update.message.reply_photo(photo=data['img_path'], caption=data['caption'], parse_mode=ParseMode.HTML)

    # --- FIX: Filter members who are actually in THIS group ---
    potential_members = list(users_collection.find({"seen_groups": chat_id}))
    
    if len(potential_members) < 2:
        return await update.message.reply_text("⚠️ Not enough active members tracked in this group yet.")

    # Random shuffle and verify membership
    random.shuffle(potential_members)
    selected_couple = []
    
    for user_data in potential_members:
        try:
            # Bot check karega ki kya user abhi bhi group mein hai
            member = await context.bot.get_chat_member(chat_id, user_data["user_id"])
            if member.status not in ["left", "kicked"]:
                selected_couple.append(user_data)
        except BadRequest:
            continue # User not found in chat
            
        if len(selected_couple) == 2:
            break

    if len(selected_couple) < 2:
        return await update.message.reply_text("⚠️ Valid group members not found in database.")

    c1_db, c2_db = selected_couple

    if not BG_PATH.exists():
        return await update.message.reply_text("❌ Background 'couple.png' missing!")

    base = Image.open(BG_PATH).convert("RGBA")
    p1_img = await get_circular_avatar(context.bot, c1_db["user_id"])
    p2_img = await get_circular_avatar(context.bot, c2_db["user_id"])

    base.paste(p1_img, (200, 315), p1_img) 
    base.paste(p2_img, (600, 315), p2_img) 

    final_img_path = TEMP_DIR / f"couple_final_{chat_id}.png"
    base.save(final_img_path)

    m1 = f'<a href="tg://user?id={c1_db["user_id"]}">{html.escape(c1_db["name"])}</a>'
    m2 = f'<a href="tg://user?id={c2_db["user_id"]}">{html.escape(c2_db["name"])}</a>'
    
    caption = (
        "<b>TODAY'S COUPLE OF THE DAY:</b>\n\n"
        f"💞 {m1} + {m2} = ❤️\n\n"
        f"<b>NEXT COUPLES WILL BE SELECTED ON {(datetime.now() + timedelta(days=1)).strftime('%d/%m/%Y')}!!</b>"
    )

    couple_cache[chat_id] = {"date": today, "img_path": str(final_img_path), "caption": caption}
    await update.message.reply_photo(photo=str(final_img_path), caption=caption, parse_mode=ParseMode.HTML)
