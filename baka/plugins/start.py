# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Integrated Code - Fixed Help Callback Error

import html
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, PrefixHandler
from telegram.constants import ParseMode
from baka.config import BOT_NAME, START_IMG_URL, OWNER_LINK
from baka.utils import ensure_user_exists, track_group

# --- 💠 KEYBOARDS ---
def get_start_keyboard(bot_username):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💬 𝚃𝙰𝙻𝙺 𝚃𝙾 𝙱𝙰𝙺𝙰", callback_data="talk_baka"),
            InlineKeyboardButton("⏤͟͞ 𝘽𝘼𝙆𝘼", url=OWNER_LINK)
        ],
        [
            InlineKeyboardButton("🧸 𝙵𝚁𝙸𝙴𝙽𝙳𝚂", url="https://t.me/hamaribaka"),
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
    ensure_user_exists(user)
    track_group(chat, user)
    
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
        except: pass
    else:
        await update.message.reply_photo(photo=START_IMG_URL, caption=caption, reply_markup=kb, parse_mode=ParseMode.HTML)

# --- ❓ HELP COMMAND (.help) ---
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Updated Help Menu showing . commands"""
    help_text = (
        "📖 <b>Baka Help Menu</b>\n\n"
        "🛠 <b>Management:</b>\n"
        "• .ban - User ko hamesha ke liye nikaalein\n"
        "• .mute - User ko chup karayein\n"
        "• .kick - User ko group se nikaalein\n\n"
        "💰 <b>Economy:</b>\n"
        "• /economy - Saari paise wali commands dekhein\n\n"
        "🎮 <b>Games:</b>\n"
        "• /game - Bomb game ke rules dekhein\n\n"
        "✨ Use commands by replying to a user!"
    )
    # Help menu me bhi Back button de diya hai
    await update.message.reply_text(text=help_text, reply_markup=get_back_to_start(), parse_mode=ParseMode.HTML)

# --- 🛡 MANAGEMENT COMMANDS ---
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private": return
    await update.message.reply_text("🚫 <b>Banned!</b>", parse_mode=ParseMode.HTML)

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private": return
    await update.message.reply_text("🤐 <b>Muted!</b>", parse_mode=ParseMode.HTML)

# --- 💣 GAME COMMAND ---
async def game_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bomb_text = (
        "💣 <b>Bomb Game Rules</b>\n\n"
        "1️⃣ /bomb &lt;amount&gt; - Start a bomb game\n"
        "2️⃣ /join &lt;amount&gt; - Join the game\n"
        "3️⃣ /pass - Pass the bomb\n"
        "4️⃣ /myrank - Check rank\n\n"
        "🎯 Be fast! Hold the bomb too long and BOOM 💥"
    )
    await update.message.reply_text(text=bomb_text, parse_mode=ParseMode.HTML)

# --- 💰 ECONOMY COMMAND ---
async def economy_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    eco_text = (
        "💰 <b>Baka Economy System Guide</b>\n\n"
        "💬 <b>How it works:</b>\n"
        "Manage your virtual money and items in the group!\n\n"
        "🔹 <b>Normal Users ( 👤 ):</b>\n"
        "• /daily — Receive $1000 daily reward\n"
        "• /bal — Check balance\n"
        "• /rob (reply) &lt;amount&gt; — Max $10k\n"
        "• /kill (reply) — Reward $100-200\n"
        "• /revive (reply) — Revive friend\n"
        "• /give (reply) &lt;amount&gt; — Gift money\n"
    )
    await update.message.reply_text(text=eco_text, parse_mode=ParseMode.HTML)

# --- 🖱️ MAIN START CALLBACK HANDLER ---
async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == "return_start":
        await start(update, context)
    elif data == "talk_baka":
        await query.message.edit_caption(caption="To talk to me, just send me any message 💬✨", reply_markup=get_back_to_start(), parse_mode=ParseMode.HTML)
    elif data == "game_features":
        game_text = "🎮 <b>Game Features</b>\n\nTo know about <b>Lottery</b>, tap /game\nTo know about <b>Economy</b>, tap /economy\n\nLucky 🍀"
        await query.message.edit_caption(caption=game_text, reply_markup=get_back_to_start(), parse_mode=ParseMode.HTML)

# --- 🆘 MISSING HELP CALLBACK (Yeh Function Add Kiya Hai) ---
async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles callbacks coming from Help menu or Ryan.py generic handler."""
    query = update.callback_query
    data = query.data

    # Agar Ryan.py mein 'return_start' is function par bheja ja raha hai
    if data == "return_start":
        await start(update, context)
    else:
        # Koi aur help button dabaya ho toh
        await query.answer()
