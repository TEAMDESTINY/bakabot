# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Waifu Plugin - Fixed Attribute for Ryan.py

import requests
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.utils import stylize_text

async def waifu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Attribute fix for Ryan.py.
    Fetches a random waifu image from an API.
    """
    try:
        # API call to get random waifu
        response = requests.get("https://api.waifu.pics/sfw/waifu")
        data = response.json()
        image_url = data.get("url")
        
        if image_url:
            await update.message.reply_photo(
                photo=image_url,
                caption=f"🌸 <b>{stylize_text('Your Waifu')}</b>",
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text("❌ Waifu nahi mili, fir se try karein!")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)}")
