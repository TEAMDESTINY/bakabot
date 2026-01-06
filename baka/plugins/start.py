# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Integrated Code - Games, Economy & Talk Logic

import html
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import BOT_NAME, START_IMG_URL, OWNER_LINK
from baka.utils import ensure_user_exists, track_group

# --- 💠 KEYBOARDS ---
def get_start_keyboard(bot_username):
    """Main start menu keyboard."""
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
    """Universal back button."""
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 𝙱𝚊𝚌𝚔", callback_data="return_start")]])

# --- 🚀 START COMMAND ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command and main menu."""
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
        except:
            pass
    else:
        await update.message.reply_photo(photo=START_IMG_URL, caption=caption, reply_markup=kb, parse_mode=ParseMode.HTML)

# --- 💣 BOMB GAME COMMAND (/game) ---
async def game_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends Bomb Game Rules with <amount> style as per screenshot."""
    bomb_text = (
        "💣 <b>Bomb Game Rules</b>\n\n"
        "1️⃣ /bomb &lt;amount&gt; - Start a bomb game\n"
        "with entry fee\n"
        "2️⃣ /join &lt;amount&gt; - Join the game before it\n"
        "starts\n"
        "3️⃣ /pass - Pass the bomb when you have it\n"
        "4️⃣ /myrank - Check your or your friend's rank\n"
        "5️⃣ /leaders - Check bomb game leaderboard\n\n"
        "⚡ <b>Rules</b>\n"
        "• Minimum 2 players required\n"
        "• Bomb explodes randomly every round\n"
        "• Last player alive wins the pot\n\n"
        "❗ <b>Admin Power</b>\n"
        "• Admins can cancel game using /bombcancel\n"
        "• Entry fees will be refunded\n\n"
        "🎯 Be fast! Hold the bomb too long and BOOM\n"
        "💥"
    )
    await update.message.reply_text(text=bomb_text, parse_mode=ParseMode.HTML)

# --- 💰 ECONOMY COMMAND (/economy) ---
async def economy_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends Economy Guide as per screenshot."""
    eco_text = (
        "💰 <b>Baka Economy System Guide</b>\n\n"
        "💬 <b>How it works:</b>\n"
        "Manage your virtual money and items in the group! Use commands below to earn, gift, buy, or interact with others.\n\n"
        "🔹 <b>Normal Users ( 👤 ):</b>\n"
        "• /daily — Receive $1000 daily reward\n"
        "• /claim — Add Baka in group to claim 10k+\n"
        "• /bal — Check your/your friend's balance ( 👤 prefix)\n"
        "• /rob (reply) &lt;amount&gt; — Max $10k\n"
        "• /kill (reply) — Reward $100-200\n"
        "• /revive (reply or without reply) — Revive you or a friend\n"
        "• /protect 1d — Buy protection\n"
        "• /give (reply) &lt;amount&gt; — Gift money (10% fee)\n"
        "• /toprich — See top 10 richest users ( 👤 normal)\n"
        "• /topkill — See top 10 killers ( 👤 normal)\n\n"
        "👤 Normal users can rob and kill 200 users ."
    )
    await update.message.reply_text(text=eco_text, parse_mode=ParseMode.HTML)

# --- 🖱️ CALLBACK HANDLER ---
async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles button clicks."""
    query = update.callback_query
    data = query.data
    
    if data == "return_start":
        await start(update, context)
        
    elif data == "talk_baka":
        # Screenshot message
        talk_text = "To talk to me, just send me any message 💬✨"
        try:
            await query.message.edit_caption(caption=talk_text, reply_markup=get_back_to_start(), parse_mode=ParseMode.HTML)
        except:
            pass
        
    elif data == "game_features":
        # Game Features menu
        game_text = (
            "🎮 <b>Game Features</b>\n\n"
            "To know about the <b>Lottery System</b>, tap /game\n"
            "To know about the <b>Economy System</b>, tap /economy\n\n"
            "Have fun and be lucky 🍀"
        )
        try:
            await query.message.edit_caption(caption=game_text, reply_markup=get_back_to_start(), parse_mode=ParseMode.HTML)
        except:
            pass
