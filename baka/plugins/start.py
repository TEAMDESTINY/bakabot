# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Design - Grid Layout & Custom Brand Name

import html
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatType
from baka.config import BOT_NAME, START_IMG_URL, OWNER_LINK
from baka.utils import ensure_user_exists, track_group

# --- 💠 KEYBOARDS ---
def get_start_keyboard(bot_username):
    # Match with image_0cce46.png grid + Your Custom Name
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💬 𝚃𝙰𝙻𝙺 𝚃𝙾 𝙱𝙰𝙺𝙰", callback_data="talk_baka"),
            InlineKeyboardButton("⏤͟͞ 𝘽𝘼𝙆𝘼", url=OWNER_LINK) # Updated as requested
        ],
        [
            InlineKeyboardButton("🧸 𝙵𝚁𝙸𝙴𝙽𝙳𝚂", url="https://t.me/your_channel"),
            InlineKeyboardButton("𝙶𝙰𝙼𝙴𝚂 🎮", callback_data="game_features")
        ],
        [
            InlineKeyboardButton("➕ 𝙰𝙳𝙳 𝙼𝙴 𝚃𝙾 𝚈𝙾𝚄𝚁 𝙶𝚁𝙾𝚄𝙿 👥", url=f"https://t.me/{bot_username}?startgroup=true")
        ]
    ])

def get_back_to_start():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 𝙱𝚊𝚌𝚔", callback_data="return_start")]])

# --- 🚀 START COMMAND ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    
    # Database Sync
    ensure_user_exists(user)
    track_group(chat, user)
    
    # Styled Text as per image_0cce46.png
    caption = (
        f"✨ <b>𝙷𝚎𝚢 — {user.first_name} ~</b>\n"
        f"💌 𝚈𝚘𝚞'𝚛𝚎 𝚃𝚊𝚕𝚔𝚒𝚗𝚐 𝚃𝚘 𝙱𝙰𝙺𝙰, 𝙰 𝚂𝚊𝚜𝚜𝚢 𝙲𝚞𝚝𝚒𝚎 𝙶𝚒𝚛𝚕 💕\n\n"
        f"➬ 𝙲𝚑𝚘𝚘𝚜𝚎 𝙰𝚗 𝙾𝚙𝚝𝚒𝚘𝚗 𝙱𝚎𝚕𝚘𝚠:"
    )

    kb = get_start_keyboard(context.bot.username)

    if update.callback_query:
        query = update.callback_query
        try:
            await query.message.edit_caption(caption=caption, reply_markup=kb, parse_mode=ParseMode.HTML)
        except:
            pass
    else:
        await update.message.reply_photo(photo=START_IMG_URL, caption=caption, reply_markup=kb, parse_mode=ParseMode.HTML)

# --- 🖱️ CALLBACK HANDLER ---
async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == "return_start":
        await start(update, context)
        
    elif data == "game_features":
        # Text exactly as per image_0cd208.png
        game_text = (
            "🎮 <b>Game Features</b>\n\n"
            "To know about the <b>Lottery System</b>, tap /game\n"
            "To know about the <b>Economy System</b>, tap /economy\n\n"
            "Have fun and be lucky 🍀"
        )
        try:
            await query.message.edit_caption(
                caption=game_text, 
                reply_markup=get_back_to_start(), 
                parse_mode=ParseMode.HTML
            )
        except:
            pass
