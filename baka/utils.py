# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Utils - Fixed Protection Logic & Timezone Sync

import html
import re
import asyncio
from datetime import datetime, timedelta
from telegram import Bot, User, Chat
from telegram.constants import ParseMode, ChatType
from baka.database import users_collection, sudoers_collection, groups_collection
from baka.config import OWNER_ID, SUDO_IDS, LOGGER_ID, BOT_NAME

# --- 👑 SUDO SYSTEM ---
SUDO_USERS = set()

def reload_sudoers():
    """Sudo users ko database aur config se load karta hai."""
    try:
        SUDO_USERS.clear()
        SUDO_USERS.add(OWNER_ID)
        # Config se list IDs load karna
        if SUDO_IDS:
            for x in SUDO_IDS:
                SUDO_USERS.add(int(x))
        # Database se extra sudoers load karna
        for doc in sudoers_collection.find({}):
            SUDO_USERS.add(doc["user_id"])
    except:
        pass

reload_sudoers()

# --- ✨ CLEAN TEXT ENGINE ---
def stylize_text(text):
    """Normal text return karega."""
    return str(text)

# --- 👤 MENTION SYSTEM ---
def get_mention(user_data, custom_name=None):
    """Clickable HTML link generator."""
    if isinstance(user_data, (User, Chat)):
        uid = user_data.id
        name = getattr(user_data, "first_name", getattr(user_data, "title", "User"))
    elif isinstance(user_data, dict):
        uid = user_data.get("user_id")
        name = user_data.get("name", "User")
    else: 
        return "Unknown"
    
    safe_name = html.escape(custom_name or name or "User")
    return f'<a href="tg://user?id={uid}"><b>{safe_name}</b></a>'

# --- 🛡️ PROTECTION ENGINE (STRICT CHECK) ---
def get_active_protection(user_data):
    """Check karta hai ki user abhi bhi protected hai ya nahi."""
    if not user_data:
        return None
    try:
        now = datetime.utcnow()
        # database.py ke naye field name 'protection_expiry' ke saath sync
        expiry = user_data.get("protection_expiry")
        # Strict Comparison: Agar expiry time bit chuka hai toh None bhejega
        if expiry and isinstance(expiry, datetime):
            if expiry > now:
                return expiry
        return None
    except:
        return None

def is_protected(user_data):
    """Returns True agar protection active hai."""
    return get_active_protection(user_data) is not None

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

# --- 💰 ECONOMY UTILS ---
def format_money(amount): 
    return f"${amount:,}"

def ensure_user_exists(tg_user):
    """User ko database mein ensure karta hai (Bots/Anon excluded)."""
    if not tg_user or tg_user.is_bot or tg_user.id == 1087968824:
        return None
        
    user_doc = users_collection.find_one({"user_id": tg_user.id})
    un = tg_user.username.lower() if tg_user.username else None
    
    if not user_doc:
        new_user = {
            "user_id": tg_user.id, "name": tg_user.first_name, "username": un,
            "balance": 500, "status": "alive", "kills": 0, "daily_kills": 0, "daily_robs": 0,
            "protection_expiry": None # Sync with database.py
        }
        users_collection.insert_one(new_user)
        return new_user
    return user_doc

async def resolve_target(update, context, specific_arg=None):
    """Target user ko reply, ID ya username se dhundta hai."""
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
        if target.is_bot or target.id == 1087968824:
            return None, "Invalid target (Bot/Anon)"
        return ensure_user_exists(target), None
    
    query = specific_arg or (context.args[0] if context.args else None)
    if not query: return None, "No target"
    
    if str(query).isdigit():
        doc = users_collection.find_one({"user_id": int(query)})
        return (doc, None) if doc else (None, "ID not found")
    
    clean_un = query.replace("@", "").lower()
    doc = users_collection.find_one({"username": clean_un})
    return (doc, None) if doc else (None, "User not found")

# --- 🌟 LOGGING & NOTIFY ---
async def log_to_channel(bot: Bot, event_type: str, details: dict):
    if not LOGGER_ID or LOGGER_ID == 0: return
    now = datetime.now().strftime("%I:%M:%S %p")
    text = f"📜 <b>{event_type.upper()}</b>\n━━━━━━━━━━━━━━━━━━\n"
    for k, v in details.items():
        text += f"<b>{k.title()}:</b> {v}\n"
    text += f"━━━━━━━━━━━━━━━━━━\n⌚ <code>{now}</code>"
    try: 
        await bot.send_message(chat_id=LOGGER_ID, text=text, parse_mode=ParseMode.HTML)
    except: pass

async def notify_victim(bot, user_id, message_text):
    try: 
        await bot.send_message(chat_id=user_id, text=message_text, parse_mode=ParseMode.HTML)
    except: pass
