# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Complete Utils - Synced Clickable Names & Log System

import html
import re
import asyncio
from datetime import datetime, timedelta
from telegram import Bot, User, Chat
from telegram.constants import ParseMode, ChatType
from baka.database import users_collection, sudoers_collection, groups_collection
from baka.config import OWNER_ID, SUDO_IDS_STR, LOGGER_ID, BOT_NAME

# --- 👑 SUDO SYSTEM ---
SUDO_USERS = set()

def reload_sudoers():
    """Reloads sudo users from config and database."""
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

# --- 🌸 AESTHETIC FONT ENGINE ---
def stylize_text(text):
    """Applies aesthetic font styles to text."""
    font_map = {
        'A': 'ᴧ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'Є', 'F': 'Ғ', 'G': 'ɢ',
        'H': 'ʜ', 'I': 'ɪ', 'J': 'ᴊ', 'K': 'ᴋ', 'L': 'ʟ', 'M': 'ϻ', 'N': 'η',
        'O': 'σ', 'P': 'ᴘ', 'Q': 'ǫ', 'R': 'Ꝛ', 'S': 's', 'T': 'ᴛ', 'U': 'υ',
        'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x', 'Y': 'ʏ', 'Z': 'ᴢ',
        'a': 'ᴧ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'є', 'f': 'ғ', 'g': 'ɢ',
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

# --- 👤 MENTION SYSTEM (CLICKABLE NAMES) ---
def get_mention(user_data, custom_name=None):
    """
    Creates a clickable HTML link for any user.
    Uses tg://user?id= even if username is missing.
    """
    if isinstance(user_data, (User, Chat)):
        uid = user_data.id
        # Username missing? Use first_name
        name = user_data.first_name if hasattr(user_data, "first_name") else user_data.title
    elif isinstance(user_data, dict):
        uid = user_data.get("user_id")
        name = user_data.get("name", "User")
    else: 
        return "Unknown"
    
    # HTML escape is necessary to prevent breaking tags
    safe_name = html.escape(custom_name or name or "User")
    return f'<a href="tg://user?id={uid}"><b>{safe_name}</b></a>'

# --- 🌟 LOGGING SYSTEM ---
async def log_to_channel(bot: Bot, event_type: str, details: dict):
    """Sends stylized logs to the defined log channel."""
    if not LOGGER_ID or LOGGER_ID == 0: return
    now = datetime.now().strftime("%I:%M:%S %p")
    
    # Exact structure from your screenshot
    text = f"📜 <b>{stylize_text(event_type.upper())}</b>\n"
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
    """Tracks group data and user group membership."""
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
    """Checks if protection shield is active."""
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

def format_time(td):
    h, r = divmod(int(td.total_seconds()), 3600)
    m, _ = divmod(r, 60)
    return f"{h}h {m}m"

# --- 👤 DB ENSURE ---
def ensure_user_exists(tg_user):
    """Syncs Telegram user data with MongoDB."""
    if not tg_user: return None
    user_doc = users_collection.find_one({"user_id": tg_user.id})
    un = tg_user.username.lower() if tg_user.username else None
    
    if not user_doc:
        new_user = {
            "user_id": tg_user.id, "name": tg_user.first_name, "username": un,
            "balance": 500, "inventory": [], "status": "alive", 
            "protection_expiry": None # Shield starts empty
        }
        users_collection.insert_one(new_user)
        return new_user
    
    updates = {}
    if user_doc.get("username") != un: updates["username"] = un
    if user_doc.get("name") != tg_user.first_name: updates["name"] = tg_user.first_name
    if updates: 
        users_collection.update_one({"user_id": tg_user.id}, {"$set": updates})
        user_doc.update(updates)
    return user_doc

async def resolve_target(update, context, specific_arg=None):
    """Resolves a target user via reply, ID, or Username."""
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
