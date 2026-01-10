# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Integrated Couple Plugin for PTB Framework

import os
import random
import html
from datetime import datetime, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatType

from baka.utils import stylize_text, get_mention
from baka.database import users_collection

# --- Path Settings ---
ASSETS = Path("baka/assets")
BG_PATH = ASSETS / "couple.png" # Aapka background file
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
    """Downloads profile photo and crops it into a circle."""
    try:
        photos = await bot.get_user_profile_photos(user_id, limit=1)
        if photos.total_count > 0:
            file = await bot.get_file(photos.photos[0][-1].file_id)
            path = TEMP_DIR / f"avatar_{user_id}.png"
            await file.download_to_drive(path)
            
            # Resizing to 437x437 as per your code
            img = Image.open(path).convert("RGBA").resize((437, 437))
            mask = Image.new("L", (437, 437), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 437, 437), fill=255)
            
            output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
            output.putalpha(mask)
            
            if path.exists(): os.remove(path)
            return output
    except: pass
    return Image.new("RGBA", (437, 437), (220, 220, 220, 255))

async def couple(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main command handler for /couples."""
    chat = update.effective_chat
    if chat.type == ChatType.PRIVATE:
        return await update.message.reply_text("ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs.")

    today = get_today_date()
    chat_id = chat.id

    # 1. Selection stays same for 24 hours per group
    if chat_id in couple_cache and couple_cache[chat_id]['date'] == today:
        data = couple_cache[chat_id]
        return await update.message.reply_photo(
            photo=data['img_path'], 
            caption=data['caption'], 
            parse_mode=ParseMode.HTML
        )

    msg = await update.message.reply_text("ɢᴇɴᴇʀᴀᴛɪɴɢ ᴄᴏᴜᴘʟᴇs ɪᴍᴀɢᴇ...")

    # 2. Filter users seen in this specific group
    members = list(users_collection.find({"seen_groups": chat_id}))
    
    if len(members) < 2:
        await msg.delete()
        return await update.message.reply_text("⚠️ Not enough active members tracked in this group.")

    # 3. Pick Two Random Members
    c1_db, c2_db = random.sample(members, 2)
    
    # 4. Generate Image
    if not BG_PATH.exists():
        await msg.delete()
        return await update.message.reply_text("❌ Background 'couple.png' missing in baka/assets/ folder!")

    base = Image.open(BG_PATH).convert("RGBA")
    p1_img = await get_circular_avatar(context.bot, c1_db["user_id"])
    p2_img = await get_circular_avatar(context.bot, c2_db["user_id"])

    # Paste Avatars (Coordinates adjusted for your frame circles)
    base.paste(p1_img, (116, 160), p1_img) # Left circle
    base.paste(p2_img, (789, 160), p2_img) # Right circle

    final_img_path = TEMP_DIR / f"couple_final_{chat_id}.png"
    base.save(final_img_path)

    # 5. Caption Formatting
    m1 = get_mention(c1_db)
    m2 = get_mention(c2_db)
    
    caption = (
        f"**ᴛᴏᴅᴀʏ's ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ :**\n\n"
        f"{m1} + {m2} = ❤️\n\n"
        f"**ɴᴇxᴛ ᴄᴏᴜᴘʟᴇs ᴡɪʟʟ ʙᴇ sᴇʟᴇᴄᴛᴇᴅ ᴏɴ {get_tomorrow_date()} !!**"
    )

    # 6. Cache and Send
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
    await msg.delete()
