# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Couple Plugin - Logic: Use DP if exists, else upic.png

import os
import random
from datetime import datetime, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatType

from baka.utils import get_mention
from baka.database import users_collection

# --- Path Settings ---
ASSETS = Path("baka/assets")
BG_PATH = ASSETS / "cppic.png"        # Main Background Frame
FALLBACK_PATH = ASSETS / "upic.png"   # Default DP if user has none
TEMP_DIR = Path("temp_couples")

if not TEMP_DIR.exists():
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

couple_cache = {}

async def get_circular_avatar(bot, user_id):
    """Logic: User DP > Fallback (upic.png)"""
    avatar_path = TEMP_DIR / f"avatar_{user_id}.png"
    size = (437, 437) # Exact size for your frame
    
    try:
        # 1. Telegram se photo lene ki koshish
        photos = await bot.get_user_profile_photos(user_id, limit=1)
        if photos.total_count > 0:
            file = await bot.get_file(photos.photos[0][-1].file_id)
            await file.download_to_drive(avatar_path)
            img = Image.open(avatar_path).convert("RGBA")
        else:
            # 2. Agar photo nahi hai toh upic.png load karein
            img = Image.open(FALLBACK_PATH).convert("RGBA")
    except Exception:
        # 3. Agar download error aaye toh bhi upic.png load karein
        img = Image.open(FALLBACK_PATH).convert("RGBA")

    # Image ko circular shape dena
    img = img.resize(size, Image.LANCZOS)
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    
    output = ImageOps.fit(img, size, centering=(0.5, 0.5))
    output.putalpha(mask)

    # Cleanup temporary file
    if avatar_path.exists():
        os.remove(avatar_path)
        
    return output

async def couple(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == ChatType.PRIVATE:
        return await update.message.reply_text("ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs.")

    today = datetime.now().strftime("%d/%m/%Y")
    chat_id = chat.id

    # Cache Check (24h lock)
    if chat_id in couple_cache and couple_cache[chat_id]['date'] == today:
        data = couple_cache[chat_id]
        return await update.message.reply_photo(photo=data['img_path'], caption=data['caption'], parse_mode=ParseMode.HTML)

    if not BG_PATH.exists():
        return await update.message.reply_text("❌ Error: 'cppic.png' background is missing in assets!")

    msg = await update.message.reply_text("ɢᴇɴᴇʀᴀᴛɪɴɢ ᴄᴏᴜᴘʟᴇs ɪᴍᴀɢᴇ...")

    # Group members pick karein
    members = list(users_collection.find({"seen_groups": chat_id}))
    if len(members) < 2:
        await msg.delete()
        return await update.message.reply_text("⚠️ Not enough active members found in this group database.")

    c1_db, c2_db = random.sample(members, 2)

    # Image Processing
    base = Image.open(BG_PATH).convert("RGBA")
    p1_img = await get_circular_avatar(context.bot, c1_db["user_id"])
    p2_img = await get_circular_avatar(context.bot, c2_db["user_id"])

    # Paste logic at your coordinates
    base.paste(p1_img, (116, 160), p1_img)
    base.paste(p2_img, (789, 160), p2_img)

    final_img_path = TEMP_DIR / f"couple_{chat_id}.png"
    base.save(final_img_path)

    # Formatting text
    m1 = get_mention(c1_db)
    m2 = get_mention(c2_db)
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%d/%m/%Y')
    
    caption = (
        f"<b>ᴛᴏᴅᴀʏ's ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ :</b>\n\n"
        f"💞 {m1} + {m2} = ❤️\n\n"
        f"<b>ɴᴇxᴛ ᴄᴏᴜᴘʟᴇs ᴡɪʟʟ ʙᴇ sᴇʟᴇᴄᴛᴇᴅ ᴏɴ {tomorrow} !!</b>"
    )

    couple_cache[chat_id] = {"date": today, "img_path": str(final_img_path), "caption": caption}
    
    await update.message.reply_photo(photo=open(final_img_path, 'rb'), caption=caption, parse_mode=ParseMode.HTML)
    await msg.delete()
