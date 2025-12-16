# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Utils - Serif Italic + Name Fix + Logger Fixed

import html
import re
import asyncio
from datetime import datetime, timedelta
from telegram import Bot, User, Chat
from telegram.constants import ParseMode, ChatType
from baka.database import users_collection, sudoers_collection, groups_collection
from baka.config import OWNER_ID, SUDO_IDS_STR, LOGGER_ID, BOT_NAME, AUTO_REVIVE_HOURS, AUTO_REVIVE_BONUS

SUDO_USERS = set()

def reload_sudoers():
    """Sudo users ko environment aur database se load karta hai."""
    try:
        SUDO_USERS.clear()
        SUDO_USERS.add(OWNER_ID)
        if SUDO_IDS_STR:
            for x in SUDO_IDS_STR.split(","):
                if x.strip().isdigit(): SUDO_USERS.add(int(x.strip()))
        for doc in sudoers_collection.find({}):
            SUDO_USERS.add(doc["user_id"])
    except Exception as e:
        print(f"Sudo Load Error: {e}")

reload_sudoers()

# --- 🌸 SERIF ITALIC FONT ENGINE ---
def stylize_text(text):
    """Normal text ko Aesthetic Math Serif Italic mein badalta hai."""
    font_map = {
        'A': '𝐴', 'B': '𝐵', 'C': '𝐶', 'D': '𝐷', 'E': '𝐸', 'F': '𝐹', 'G': '𝐺',
        'H': '𝐻', 'I': '𝐼', 'J': '𝐽', 'K': '𝐾', 'L': '𝐿', 'M': '𝑀', 'N': '𝑁',
        'O': '𝑂', 'P': '𝑃', 'Q': '𝑄', 'R': '𝑅', 'S': '𝑆', 'T': '𝑇', 'U': '𝑈',
        'V': '𝑉', 'W': '𝑊', 'X': '𝑋', 'Y': '𝑌', 'Z': '𝑍',
        'a': '𝑎', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'є', 'f': 'ғ', 'g': 'ɢ',
        'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ϻ', 'n': 'η',
        'o': 'σ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ꝛ', 's': 's', 't': 'ᴛ', 'u': 'υ',
        'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ',
        '0': '𝟎', '1': '𝟏', '2': '𝟐', '3': '𝟑', '4': '𝟒', 
        '5': '𝟓', '6': '𝟔', '7': '𝟕', '8': '𝟖', '9': '𝟗'
    }
    def apply_style(t):
        return "".join(font_map.get(c, c) for c in t)

    pattern = r"(@\w+|https?://\S+|`[^`]+`|/[a-zA-Z0-9_]+)"
    parts = re.split(pattern, str(text))
    return "".join(part if re.match(pattern, part) else apply_style(part) for part in parts)

# --- 👤 NAME & MENTION ENGINE ---
def get_mention(user_data, custom_name=None):
    """
    User names ko bold aur clickable banane ke liye.
    Telegram Objects aur Database Dictionaries dono handle karta hai.
    """
    if not user_data: return "Unknown"
    
    if hasattr(user_data, 'id'): # Telegram Object
        uid = user_data.id
        first_name = user_data.first_name if hasattr(user_data, 'first_name') else getattr(user_data, 'title', "User")
    elif isinstance(user_data, dict): # Database Record
        uid = user_data.get("user_id")
        first_name = user_data.get("name") or user_data.get("first_name", "User")
    else: return "User"

    name = custom_name or first_name
    return f"<a href='tg://user?id={uid}'><b>{html.escape(str(name))}</b></a>"

# --- 🌟 ULTIMATE DASHBOARD LOGGER ---
async def log_to_channel(bot: Bot, event_type: str, details: dict):
    """Logs events to the logger channel. Fixes Ryan.py ImportError."""
    if not LOGGER_ID or LOGGER_ID == 0: return
    now = datetime.now().strftime("%I:%M:%S %p")
    header = f"🌸 <b>{stylize_text(event_type.upper())}</b>"
    text = f"{header}\n━━━━━━━━━━━━━━━━━━\n"
    for key, value in details.items():
        text += f"🔹 <b>{stylize_text(key.title())}:</b> {html.escape(str(value))}\n"
    text += f"━━━━━━━━━━━━━━━━━━\n⌚ <code>{now}</code>"
    try:
        await bot.send_message(chat_id=LOGGER_ID, text=text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except: pass

# --- 🔄 DATABASE & PROTECTION ---
def ensure_user_exists(tg_user):
    try:
        user_doc = users_collection.find_one({"user_id": tg_user.id})
        username = tg_user.username.lower() if tg_user.username else None
        if not user_doc:
            new_user = {
                "user_id": tg_user.id, "name": tg_user.first_name, "username": username,
                "balance": 0, "inventory": [], "kills": 0, "status": "alive",
                "protection_expiry": datetime.utcnow(), "registered_at": datetime.utcnow()
            }
            users_collection.insert_one(new_user)
            return new_user
        else:
            updates = {}
            if user_doc.get("name") != tg_user.first_name: updates["name"] = tg_user.first_name
            if user_doc.get("username") != username: updates["username"] = username
            if updates: users_collection.update_one({"user_id": tg_user.id}, {"$set": updates})
            return user_doc
    except: return {"user_id": tg_user.id, "name": tg_user.first_name, "balance": 0}

async def resolve_target(update, context, specific_arg=None):
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        doc = ensure_user_exists(target_user)
        doc['user_obj'] = target_user
        return doc, None
    query = specific_arg or (context.args[0] if context.args else None)
    if not query: return None, "No target"
    if query.isdigit(): doc = users_collection.find_one({"user_id": int(query)})
    else: doc = users_collection.find_one({"username": query.replace("@", "").lower()})
    if doc: 
        doc['user_obj'] = doc
        return doc, None
    return None, f"❌ <b>{stylize_text('Baka')}!</b> User not found."

def get_active_protection(user_data):
    try:
        now = datetime.utcnow()
        expiry = user_data.get("protection_expiry")
        return expiry if expiry and expiry > now else None
    except: return None

def format_money(amount): return f"${amount:,}"

def format_time(timedelta_obj):
    total_seconds = int(timedelta_obj.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours}h {minutes}m"

def check_auto_revive(user_doc):
    if user_doc.get('status') != 'dead': return False
    death_time = user_doc.get('death_time')
    if death_time and (datetime.utcnow() - death_time > timedelta(hours=AUTO_REVIVE_HOURS)):
        users_collection.update_one({"user_id": user_doc["user_id"]}, {"$set": {"status": "alive", "death_time": None}})
        return True
    return False
