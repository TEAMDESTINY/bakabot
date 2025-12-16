# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Utils - Destiny Bot (Serif Italic + Name Fix)

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
    """Sudo users load karne ke liye logic."""
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
    """Converts normal text to Aesthetic Math Serif Italic."""
    font_map = {
        'A': '𝐴', 'B': '𝐵', 'C': '𝐶', 'D': '𝐷', 'E': '𝐸', 'F': '𝐹', 'G': '𝐺',
        'H': '𝐻', 'I': '𝐼', 'J': '𝐽', 'K': '𝐾', 'L': '𝐿', 'M': '𝑀', 'N': '𝑁',
        'O': '𝑂', 'P': '𝑃', 'Q': '𝑄', 'R': '𝑅', 'S': '𝑆', 'T': '𝑇', 'U': '𝑈',
        'V': '𝑉', 'W': '𝑊', 'X': '𝑋', 'Y': '𝑌', 'Z': '𝑍',
        'a': '𝑎', 'b': '𝑏', 'c': '𝑐', 'd': '𝑑', 'e': '𝑒', 'f': '𝑓', 'g': '𝑔',
        'h': 'ℎ', 'i': '𝑖', 'j': '𝑗', 'k': '𝑘', 'l': '𝑙', 'm': '𝑚', 'n': '𝑛',
        'o': '𝑜', 'p': '𝑝', 'q': '𝑞', 'r': '𝑟', 's': '𝑠', 't': '𝑡', 'u': '𝑢',
        'v': '𝑣', 'w': '𝑤', 'x': '𝑥', 'y': '𝑦', 'z': '𝑧',
        '0': '𝟎', '1': '𝟏', '2': '𝟐', '3': '𝟑', '4': '𝟒', 
        '5': '𝟓', '6': '𝟔', '7': '𝟕', '8': '𝟖', '9': '𝟗'
    }

    def apply_style(t):
        return "".join(font_map.get(c, c) for c in t)

    # Mentions, Links aur Commands ko style nahi karna hai
    pattern = r"(@\w+|https?://\S+|`[^`]+`|/[a-zA-Z0-9_]+)"
    parts = re.split(pattern, str(text))
    return "".join(part if re.match(pattern, part) else apply_style(part) for part in parts)

# --- 👤 NAME & MENTION ENGINE (FINAL FIX) ---
def get_mention(user_data, custom_name=None):
    """
    Asli naam dikhane ke liye final logic.
    Supports Telegram User Objects and Database Dictionaries.
    """
    if not user_data:
        return "Unknown"
    
    if hasattr(user_data, 'id'): # Telegram Object
        uid = user_data.id
        first_name = user_data.first_name if hasattr(user_data, 'first_name') else getattr(user_data, 'title', "User")
    elif isinstance(user_data, dict): # DB Dictionary
        uid = user_data.get("user_id")
        # Preference: Database 'name' -> Telegram 'first_name' -> Default 'User'
        first_name = user_data.get("name") or user_data.get("first_name", "User")
    else:
        return "User"

    name = custom_name or first_name
    return f"<a href='tg://user?id={uid}'><b>{html.escape(str(name))}</b></a>"

# --- 💰 FORMATTERS ---
def format_money(amount):
    return f"${amount:,}"

def format_time(timedelta_obj):
    total_seconds = int(timedelta_obj.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours}h {minutes}m"

# --- 🛡️ PROTECTION ---
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

# --- 🔄 DATABASE HANDLERS ---
def ensure_user_exists(tg_user):
    """User ko DB mein save/update karne ke liye."""
    try:
        user_doc = users_collection.find_one({"user_id": tg_user.id})
        username = tg_user.username.lower() if tg_user.username else None
        
        if not user_doc:
            new_user = {
                "user_id": tg_user.id,
                "name": tg_user.first_name,
                "username": username,
                "balance": 0,
                "inventory": [],
                "kills": 0,
                "status": "alive",
                "protection_expiry": datetime.utcnow(),
                "registered_at": datetime.utcnow()
            }
            users_collection.insert_one(new_user)
            return new_user
        else:
            # Har baar naam update karein taaki "User" na aaye
            updates = {}
            if user_doc.get("name") != tg_user.first_name:
                updates["name"] = tg_user.first_name
            if user_doc.get("username") != username:
                updates["username"] = username
            if updates:
                users_collection.update_one({"user_id": tg_user.id}, {"$set": updates})
            return user_doc
    except Exception as e:
        print(f"Error in ensure_user_exists: {e}")
        return {"user_id": tg_user.id, "name": tg_user.first_name, "balance": 0}

async def resolve_target(update, context, specific_arg=None):
    """Target dhoondne ke liye (Reply ya Tag)."""
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        return ensure_user_exists(target_user), None

    query = specific_arg or (context.args[0] if context.args else None)
    if not query: return None, "No target"

    if query.isdigit():
        doc = users_collection.find_one({"user_id": int(query)})
    else:
        clean_un = query.replace("@", "").lower()
        doc = users_collection.find_one({"username": clean_un})

    if doc: return doc, None
    return None, f"❌ <b>{stylize_text('Baka')}!</b> User not found."
