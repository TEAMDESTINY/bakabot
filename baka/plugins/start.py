# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Location: Supaul, Bihar 
# FINAL CLEAN VERSION - Simple Font & Updated Commands Sync

import html
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatType
from baka.config import BOT_NAME, START_IMG_URL, HELP_IMG_URL, SUPPORT_GROUP, SUPPORT_CHANNEL, OWNER_LINK
from baka.utils import ensure_user_exists, get_mention, track_group, log_to_channel, SUDO_USERS

SUDO_IMG = "https://files.catbox.moe/28no0e.jpg"

# --- 💠 SIMPLE KEYBOARDS ---
def get_start_keyboard(bot_username):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Channel", url=SUPPORT_CHANNEL),
            InlineKeyboardButton("Support", url=SUPPORT_GROUP)
        ],
        [
            InlineKeyboardButton("➕ Add Me To Your Group ➕", url=f"https://t.me/{bot_username}?startgroup=true")
        ],
        [
            InlineKeyboardButton("Help Menu", callback_data="help_main"),
            InlineKeyboardButton("Developer", url=OWNER_LINK)
        ]
    ])

def get_help_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Social", callback_data="help_social"),
            InlineKeyboardButton("Economy", callback_data="help_economy")
        ],
        [
            InlineKeyboardButton("RPG & War", callback_data="help_rpg"),
            InlineKeyboardButton("Bomb Game", callback_data="help_bomb")
        ],
        [
            InlineKeyboardButton("AI & Fun", callback_data="help_fun"),
            InlineKeyboardButton("Group", callback_data="help_group")
        ],
        [
            InlineKeyboardButton("Sudo", callback_data="help_sudo"),
            InlineKeyboardButton("Back", callback_data="return_start")
        ]
    ])

def get_back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="help_main")]])

# --- 🚀 COMMANDS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        chat = update.effective_chat
        ensure_user_exists(user)
        track_group(chat, user)
        
        user_link = get_mention(user)
        
        caption = (
            f"👋 <b>Welcome {user_link}!</b>\n"
            f"I am {BOT_NAME}, your AI-Powered RPG & Economy Bot! 💞\n\n"
            f"<b>Core Features:</b>\n"
            f"• <b>RPG:</b> Kill, Rob, Protect & Revive\n"
            f"• <b>Games:</b> Bomb Game, Slots, Dice & Riddles\n"
            f"• <b>Economy:</b> Daily Rewards, Shop & Group Claims\n"
            f"• <b>Social:</b> Marriage, Couples & Waifus\n\n"
            f"✦ <i>Use the buttons below to explore my commands!</i>"
        )

        bot_un = context.bot.username if context.bot.username else "RyanBakaBot"
        kb = get_start_keyboard(bot_un)

        if update.callback_query:
            try: await update.callback_query.message.edit_media(InputMediaPhoto(media=START_IMG_URL, caption=caption, parse_mode=ParseMode.HTML), reply_markup=kb)
            except: await update.callback_query.message.edit_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=kb)
        else:
            await update.message.reply_photo(photo=START_IMG_URL, caption=caption, parse_mode=ParseMode.HTML, reply_markup=kb)

        if chat.type == ChatType.PRIVATE and not update.callback_query:
            await log_to_channel(context.bot, "command", {"user": f"{user.first_name} (`{user.id}`)", "action": "Started Bot"})
            
    except Exception as e:
        print(f"Start Error: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_photo(
        photo=HELP_IMG_URL,
        caption=f"📖 <b>{BOT_NAME} Help Guide</b> 🌸\n\nSelect a category from the buttons below to see available commands:",
        parse_mode=ParseMode.HTML, reply_markup=get_help_keyboard()
    )

# --- 🖱️ CALLBACK HANDLER ---

async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == "return_start":
        await start(update, context)
        return

    if data == "help_main":
        caption = f"📖 <b>{BOT_NAME} Help Guide</b> 🌸\n\nSelect a category from the buttons below:"
        try: await query.message.edit_media(InputMediaPhoto(media=HELP_IMG_URL, caption=caption, parse_mode=ParseMode.HTML), reply_markup=get_help_keyboard())
        except: await query.message.edit_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=get_help_keyboard())
        return

    target_photo = HELP_IMG_URL
    kb = get_back_keyboard()
    text = ""
    
    if data == "help_social":
        text = (
            "💍 <b>Social & Love Commands</b>\n\n"
            "• <b>/propose</b> - Propose to a user\n"
            "• <b>/marry</b> - Check marriage status\n"
            "• <b>/divorce</b> - Break up (Costs 2k)\n"
            "• <b>/couple</b> - Matchmaking fun"
        )
    elif data == "help_economy":
        text = (
            "👛 <b>Economy & Wealth</b>\n\n"
            "• <b>/bal</b> - Check wallet and rank\n"
            "• <b>/daily</b> - Claim $1000 (DM Only)\n"
            "• <b>/give [amt]</b> - Transfer (10% Tax)\n"
            "• <b>/toprich</b> - Top 10 Richest players\n"
            "• <b>/claim</b> - Group member reward"
        )
    elif data == "help_rpg":
        text = (
            "⚔️ <b>RPG & Combat</b>\n\n"
            "• <b>/kill</b> - Kill someone (100/day limit)\n"
            "• <b>/rob [amt]</b> - Steal coins (Max 5 Lakh)\n"
            "• <b>/protect</b> - Buy shield (1d or 2d)\n"
            "• <b>/revive</b> - Instant life (Costs 200)"
        )
    elif data == "help_bomb":
        text = (
            "💣 <b>Bomb Game Commands</b>\n\n"
            "• <b>/bomb [amt]</b> - Start a new game\n"
            "• <b>/join [amt]</b> - Join the game pot\n"
            "• <b>/pass</b> - Pass the bomb to next player\n"
            "• <b>/leaders</b> - Bomb game win rankings"
        )
    elif data == "help_fun":
        text = (
            "🧠 <b>AI & Fun Mini-Games</b>\n\n"
            "• <b>/ask [prompt]</b> - Talk to AI Chatbot\n"
            "• <b>/riddle</b> - Solve and earn $1000\n"
            "• <b>/dice</b> - Roll for luck\n"
            "• <b>/slots</b> - Gamble your coins"
        )
    elif data == "help_group":
        text = (
            "⛩️ <b>Group Management</b>\n\n"
            "• <b>/ping</b> - Check bot speed\n"
            "• <b>/welcome on/off</b> - Toggle welcome media"
        )
    elif data == "help_sudo":
        if query.from_user.id not in SUDO_USERS: 
            return await query.answer("❌ Owner Only Access!", show_alert=True)
        target_photo = SUDO_IMG
        text = (
            "🔐 <b>Sudo Admin Panel</b>\n\n"
            "• <b>/addcoins</b>, <b>/rmcoins</b>\n"
            "• <b>/broadcast</b>, <b>/bombcancel</b>\n"
            "• <b>/freerevive</b>, <b>/unprotect</b>"
        )

    try: await query.message.edit_media(InputMediaPhoto(media=target_photo, caption=text, parse_mode=ParseMode.HTML), reply_markup=kb)
    except: await query.message.edit_caption(caption=text, parse_mode=ParseMode.HTML, reply_markup=kb)
