# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Complete Utils - No More Missing Imports!

import html
import re
import asyncio
from datetime import datetime, timedelta
from telegram import Bot, User, Chat
from telegram.constants import ParseMode, ChatType
from baka.database import users_collection, sudoers_collection, groups_collection
from baka.config import OWNER_ID, SUDO_IDS_STR, LOGGER_ID, BOT_NAME, AUTO_REVIVE_HOURS, AUTO_REVIVE_BONUS

# --- 👑 SUDO SYSTEM ---
SUDO_USERS = set()

def reload_sudoers():
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

# --- 🌟 LOGGING & NOTIFICATIONS ---
async def log_to_channel(bot: Bot, event_type: str, details: dict):
    if not LOGGER_ID or LOGGER_ID == 0: return
    now = datetime.now().strftime("%I:%M:%S %p")
    text = f"📜 <b>{stylize_text(event_type.upper())}</b>\n━━━━━━━━━━━━━━━━━━\n"
    for k, v in details.items():
        text += f"<b>{k.title()}:</b> {v}\n"
    text += f"━━━━━━━━━━━━━━━━━━\n⌚ <code>{now}</code>"
    try: await bot.send_message(chat_id=LOGGER_ID, text=text, parse_mode=ParseMode.HTML)
    except: pass

async def notify_victim(bot, user_id, message_text):
    try:
        await bot.send_message(chat_id=user_id, text=message_text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except: pass

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

# --- 🛡️ PROTECTION ENGINE (YE MISSING THA) ---
def get_active_protection(user_data):
    """Checks if protection_expiry is still valid."""
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

# --- 👤 MENTION & TARGET ---
def get_mention(user_data, custom_name=None):
    if isinstance(user_data, (User, Chat)):
        uid, name = user_data.id, (user_data.first_name if hasattr(user_data, "first_name") else user_data.title)
    elif isinstance(user_data, dict):
        uid, name = user_data.get("user_id"), user_data.get("name", "User")
    else: return "Unknown"
    return f"<a href='tg://user?id={uid}'><b>{html.escape(custom_name or name)}</b></a>"

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

# --- 💰 ECONOMY UTILS ---
def is_user_new(user_id):
    return users_collection.find_one({"user_id": user_id}) is None

def format_money(amount): return f"${amount:,}"

def format_time(td):
    h, r = divmod(int(td.total_seconds()), 3600)
    m, _ = divmod(r, 60)
    return f"{h}h {m}m"

# --- 👤 DB ENSURE ---
def ensure_user_exists(tg_user):
    user_doc = users_collection.find_one({"user_id": tg_user.id})
    un = tg_user.username.lower() if tg_user.username else None
    if not user_doc:
        new_user = {
            "user_id": tg_user.id, "name": tg_user.first_name, "username": un,
            "balance": 500, "inventory": [], "status": "alive", "protection_expiry": datetime.utcnow()
        }
        users_collection.insert_one(new_user)
        return new_user
    
    updates = {}
    if user_doc.get("username") != un: updates["username"] = un
    if user_doc.get("name") != tg_user.first_name: updates["name"] = tg_user.first_name
    if updates: users_collection.update_one({"user_id": tg_user.id}, {"$set": updates})
    return user_doc
