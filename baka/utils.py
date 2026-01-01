# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Utils - Fixed Import Error & Normal Font

import html
import re
import asyncio
from datetime import datetime, timedelta
from telegram import Bot, User, Chat
from telegram.constants import ParseMode, ChatType
from baka.database import users_collection, sudoers_collection, groups_collection
from baka.config import OWNER_ID, SUDO_IDS_STR, LOGGER_ID, BOT_NAME # Yahan se import kar liya

# --- 👑 IDENTITY ---
# Ryan.py ko ye yahan chahiye, isliye hum ise export kar rahe hain
BOT_NAME = BOT_NAME

# --- 👑 SUDO SYSTEM ---
SUDO_USERS = set()

def reload_sudoers():
    """Sudo users ko database aur config se load karta hai."""
    try:
        SUDO_USERS.clear()
        SUDO_USERS.add(OWNER_ID)
        if SUDO_IDS_STR:
            for x in SUDO_IDS_STR.split(","):
                if x.strip().isdigit(): SUDO_USERS.add(int(x.strip()))
        for doc in sudoers_collection.find({}):
            SUDO_USERS.add(doc["user_id"])
    except Exception:
        pass

reload_sudoers()

# --- ✨ CLEAN TEXT ENGINE ---
def stylize_text(text):
    """Normal text return karega bina kisi <code> tag ke."""
    return str(text)

# --- 👤 MENTION SYSTEM ---
def get_mention(user_data, custom_name=None):
    """Clickable HTML link."""
    if isinstance(user_data, (User, Chat)):
        uid = user_data.id
        name = user_data.first_name if hasattr(user_data, "first_name") else user_data.title
    elif isinstance(user_data, dict):
        uid = user_data.get("user_id")
        name = user_data.get("name", "User")
    else: 
        return "Unknown"
    
    safe_name = html.escape(custom_name or name or "User")
    return f'<a href="tg://user?id={uid}"><b>{safe_name}</b></a>'

# --- 🌟 LOGGING SYSTEM ---
async def log_to_channel(bot: Bot, event_type: str, details: dict):
    if not LOGGER_ID or LOGGER_ID == 0: return
    now = datetime.now().strftime("%I:%M:%S %p")
    
    text = f"📜 <b>{event_type.upper()}</b>\n"
    text += "━━━━━━━━━━━━━━━━━━\n"
    for k, v in details.items():
        text += f"<b>{k.title()}:</b> {v}\n"
    text += "━━━━━━━━━━━━━━━━━━\n"
    text += f"⌚ <code>{now}</code>"
    
    try: 
        await bot.send_message(chat_id=LOGGER_ID, text=text, parse_mode=ParseMode.HTML)
    except: 
        pass

# --- 🏰 GROUP TRACKER ---
def track_group(chat, user=None):
    if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        groups_collection.update_one(
            {"chat_id": chat.id},
            {"$set": {"title": chat.title}, "$setOnInsert": {"claimed": False}},
            upsert=True
        )
        if user:
            users_collection.update_one({"user_id": user.id}, {"$addToSet": {"seen_groups": chat.id}})

# --- 🛡️ PROTECTION ENGINE ---
def get_active_protection(user_data):
    try:
        now = datetime.utcnow()
        expiry = user_data.get("protection_expiry")
        if expiry and expiry > now:
            return expiry
        return None
    except:
        return None

def is_protected(user_data):
    return get_active_protection(user_data) is not None

# --- 💰 ECONOMY UTILS ---
def format_money(amount): 
    return f"${amount:,}"

def ensure_user_exists(tg_user):
    if not tg_user: return None
    user_doc = users_collection.find_one({"user_id": tg_user.id})
    un = tg_user.username.lower() if tg_user.username else None
    
    if not user_doc:
        new_user = {
            "user_id": tg_user.id, "name": tg_user.first_name, "username": un,
            "balance": 500, "status": "alive", "kills": 0, "daily_kills": 0, "daily_robs": 0
        }
        users_collection.insert_one(new_user)
        return new_user
    return user_doc

async def resolve_target(update, context, specific_arg=None):
    if update.message.reply_to_message:
        return ensure_user_exists(update.message.reply_to_message.from_user), None
    query = specific_arg or (context.args[0] if context.args else None)
    if not query: return None, "No target"
    if str(query).isdigit():
        doc = users_collection.find_one({"user_id": int(query)})
        return (doc, None) if doc else (None, "ID not found")
    clean_un = query.replace("@", "").lower()
    doc = users_collection.find_one({"username": clean_un})
    return (doc, None) if doc else (None, "User not found")

async def notify_victim(bot, user_id, message_text):
    try:
        await bot.send_message(chat_id=user_id, text=message_text, parse_mode=ParseMode.HTML)
    except:
        pass
