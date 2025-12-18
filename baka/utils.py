# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Location: Supaul, Bihar 
# Intellectual Property of @WTF_Phantom.

import html
import re
import asyncio
from datetime import datetime, timedelta
from telegram import Bot, User, Chat
from telegram.constants import ParseMode, ChatType
from telegram.error import TelegramError
from baka.database import users_collection, sudoers_collection, groups_collection
from baka.config import OWNER_ID, SUDO_IDS_STR, LOGGER_ID, BOT_NAME, AUTO_REVIVE_HOURS, AUTO_REVIVE_BONUS

# --- 👑 SUDO SYSTEM ---
SUDO_USERS = set()

def reload_sudoers():
    """Loads Sudo users from Env and DB."""
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
    """Converts normal text to Aesthetic Math Sans Bold (Baka Style)."""
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

# --- 🌟 ULTIMATE DASHBOARD LOGGER ---
async def log_to_channel(bot: Bot, event_type: str, details: dict):
    if not LOGGER_ID or LOGGER_ID == 0: return
    now = datetime.now().strftime("%I:%M:%S %p | %d %b")

    headers = {
        "start": f"🌸 <b>{stylize_text('SYSTEM ONLINE')}</b>",
        "join": f"🥂 <b>{stylize_text('NEW GROUP JOINED')}</b>",
        "leave": f"💔 <b>{stylize_text('LEFT GROUP')}</b>",
        "command": f"👮‍♀️ <b>{stylize_text('ADMIN COMMAND')}</b>",
        "transfer": f"💸 <b>{stylize_text('TRANSACTION')}</b>"
    }
    header = headers.get(event_type, f"📜 <b>{stylize_text('LOG ENTRY')}</b>")
    text = f"{header}\n━━━━━━━━━━━━━━━━━━\n"

    if 'user' in details: text += f"👤 <b>{stylize_text('User')}:</b> {details['user']}\n"
    if 'chat' in details: text += f"🏰 <b>{stylize_text('Chat')}:</b> {html.escape(str(details['chat']))}\n"
    if 'action' in details: text += f"🎬 <b>{stylize_text('Action')}:</b> {details['action']}\n"
    if 'link' in details:
        link_val = details['link']
        if link_val and str(link_val).startswith("http"):
            text += f"🔗 <b>{stylize_text('Invite')}:</b> <a href='{link_val}'>Click to Join</a>\n"
        else: text += f"🔒 <b>{stylize_text('Invite')}:</b> <i>Hidden/Private</i>\n"

    text += f"━━━━━━━━━━━━━━━━━━\n⌚ <code>{now}</code>"
    try: 
        await bot.send_message(chat_id=LOGGER_ID, text=text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except Exception as e: print(f"Log Error: {e}")

# --- 👤 MENTION ENGINE ---
def get_mention(user_data, custom_name=None):
    if isinstance(user_data, (User, Chat)):
        uid = user_data.id
        first_name = user_data.first_name if hasattr(user_data, "first_name") else user_data.title
    elif isinstance(user_data, dict):
        uid = user_data.get("user_id")
        first_name = user_data.get("name", "User")
    else: return "Unknown"
    name = custom_name or first_name
    return f"<a href='tg://user?id={uid}'><b>{html.escape(name)}</b></a>"

# --- 🎯 TARGET RESOLVER ---
async def resolve_target(update, context, specific_arg=None):
    if update.message.reply_to_message:
        return ensure_user_exists(update.message.reply_to_message.from_user), None
    query = specific_arg if specific_arg else (context.args[0] if context.args else None)
    if not query: return None, "No target"
    if query.isdigit():
        doc = users_collection.find_one({"user_id": int(query)})
        if doc: return doc, None
        return None, f"❌ <b>{stylize_text('Baka')}!</b> ID <code>{query}</code> not found."
    clean_username = query.replace("@", "").lower()
    doc = users_collection.find_one({"username": clean_username})
    if doc: return doc, None
    return None, f"❌ <b>{stylize_text('Oops')}!</b> User <code>@{clean_username}</code> has not started me."

# --- 🛡️ PROTECTION & ECONOMY ---
def get_active_protection(user_data):
    try:
        now = datetime.utcnow()
        self_expiry = user_data.get("protection_expiry")
        partner_expiry = None
        partner_id = user_data.get("partner_id")
        if partner_id:
            partner = users_collection.find_one({"user_id": partner_id})
            if partner: partner_expiry = partner.get("protection_expiry")
        valid_expiries = []
        if self_expiry and self_expiry > now: valid_expiries.append(self_expiry)
        if partner_expiry and partner_expiry > now: valid_expiries.append(partner_expiry)
        return max(valid_expiries) if valid_expiries else None
    except: return None

def is_protected(user_data):
    return get_active_protection(user_data) is not None

def format_money(amount): return f"${amount:,}"

def format_time(timedelta_obj):
    total_seconds = int(timedelta_obj.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours}h {minutes}m"

# --- 👤 DB ENSURE & AUTO-REVIVE ---
def ensure_user_exists(tg_user):
    user_doc = users_collection.find_one({"user_id": tg_user.id})
    username = tg_user.username.lower() if tg_user.username else None
    
    if not user_doc:
        new_user = {
            "user_id": tg_user.id, "name": tg_user.first_name, "username": username,
            "balance": 500, "inventory": [], "waifus": [], "kills": 0, "status": "alive",
            "protection_expiry": datetime.utcnow(), "registered_at": datetime.utcnow()
        }
        users_collection.insert_one(new_user)
        return new_user
    
    # Sync Username and Name if changed
    updates = {}
    if user_doc.get("username") != username: updates["username"] = username
    if user_doc.get("name") != tg_user.first_name: updates["name"] = tg_user.first_name
    
    # Auto-Revive Check
    death_time = user_doc.get('death_time')
    if user_doc.get('status') == 'dead' and death_time:
        if datetime.utcnow() - death_time > timedelta(hours=AUTO_REVIVE_HOURS):
            updates.update({"status": "alive", "death_time": None})
            users_collection.update_one({"user_id": tg_user.id}, {"$inc": {"balance": AUTO_REVIVE_BONUS}})
            user_doc['status'] = 'alive'
            
    if updates:
        users_collection.update_one({"user_id": tg_user.id}, {"$set": updates})

    return user_doc

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
