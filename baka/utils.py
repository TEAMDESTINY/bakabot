# Copyright...
# (तुम्हारा same header रखा है)

import html
import re
import asyncio
from datetime import datetime, timedelta
from telegram import Bot, User, Chat
from telegram.constants import ParseMode, ChatType
from telegram.error import TelegramError
from baka.database import users_collection, sudoers_collection, groups_collection
from baka.config import OWNER_ID, SUDO_IDS_STR, LOGGER_ID, BOT_NAME, AUTO_REVIVE_HOURS, AUTO_REVIVE_BONUS

# ---------------------------------------------------------
#                  SUDO LOADER
# ---------------------------------------------------------

SUDO_USERS = set()

def reload_sudoers():
    try:
        SUDO_USERS.clear()
        SUDO_USERS.add(OWNER_ID)

        if SUDO_IDS_STR:
            for x in SUDO_IDS_STR.split(","):
                if x.strip().isdigit():
                    SUDO_USERS.add(int(x.strip()))

        for doc in sudoers_collection.find({}):
            SUDO_USERS.add(doc["user_id"])

    except Exception as e:
        print(f"Sudo Load Error: {e}")

reload_sudoers()


# ---------------------------------------------------------
#              AESTHETIC FONT ENGINE
# ---------------------------------------------------------

def stylize_text(text):
    font_map = {
        'A': 'ᴧ','B': 'ʙ','C': 'ᴄ','D': 'ᴅ','E': 'Є','F': 'Ғ','G': 'ɢ',
        'H': 'ʜ','I': 'ɪ','J': 'ᴊ','K': 'ᴋ','L': 'ʟ','M': 'ϻ','N': 'η',
        'O': 'σ','P': 'ᴘ','Q': 'ǫ','R': 'Ꝛ','S': 's','T': 'ᴛ','U': 'υ',
        'V': 'ᴠ','W': 'ᴡ','X': 'x','Y': 'ʏ','Z': 'ᴢ',
        'a': 'ᴧ','b': 'ʙ','c': 'ᴄ','d': 'ᴅ','e': 'є','f': 'ғ','g': 'ɢ',
        'h': 'ʜ','i': 'ɪ','j': 'ᴊ','k': 'ᴋ','l': 'ʟ','m': 'ϻ','n': 'η',
        'o': 'σ','p': 'ᴘ','q': 'ǫ','r': 'ꝛ','s': 's','t': 'ᴛ','u': 'υ',
        'v': 'ᴠ','w': 'ᴡ','x': 'x','y': 'ʏ','z': 'ᴢ',
        '0':'𝟎','1':'𝟏','2':'𝟐','3':'𝟑','4':'𝟒','5':'𝟓','6':'𝟔','7':'𝟕','8':'𝟖','9':'𝟗'
    }

    def apply_style(t):
        return "".join(font_map.get(c, c) for c in t)

    pattern = r"(@\w+|https?://\S+|`[^`]+`|/[a-zA-Z0-9_]+)"
    parts = re.split(pattern, str(text))
    return "".join(
        part if re.match(pattern, part) else apply_style(part)
        for part in parts
    )


# ---------------------------------------------------------
#                   LOGGER ENGINE
# ---------------------------------------------------------

async def log_to_channel(bot: Bot, event_type: str, details: dict):
    if LOGGER_ID == 0:
        return

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

    if 'user' in details:
        text += f"👤 <b>User:</b> {details['user']}\n"

    if 'chat' in details:
        text += f"🏰 <b>Chat:</b> {html.escape(details['chat'])}\n"

    if 'action' in details:
        text += f"🎬 <b>Action:</b> {details['action']}\n"

    if 'link' in details:
        text += f"🔗 <b>Invite:</b> {details['link']}\n"

    text += f"━━━━━━━━━━━━━━━━━━\n⌚ <code>{now}</code>"

    try:
        await bot.send_message(
            chat_id=LOGGER_ID,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
    except:
        pass


# ---------------------------------------------------------
#         AUTO REVIVE HANDLER
# ---------------------------------------------------------

def check_auto_revive(user_doc):
    try:
        if user_doc['status'] != 'dead':
            return False

        death_time = user_doc.get('death_time')
        if not death_time:
            return False

        if datetime.utcnow() - death_time > timedelta(hours=AUTO_REVIVE_HOURS):
            users_collection.update_one(
                {"user_id": user_doc["user_id"]},
                {
                    "$set": {"status": "alive", "death_time": None},
                    "$inc": {"balance": AUTO_REVIVE_BONUS}
                }
            )
            return True
    except:
        return False


# ---------------------------------------------------------
#      ENSURE USER EXISTS (NOW WITH XP + LEVEL SYSTEM)
# ---------------------------------------------------------

def ensure_user_fields(user):
    updated = False
    set_data = {}

    if "xp" not in user:
        set_data["xp"] = 0
        updated = True

    if "level" not in user:
        set_data["level"] = 1
        updated = True

    if updated:
        users_collection.update_one(
            {"user_id": user["user_id"]}, {"$set": set_data}
        )
        user.update(set_data)

    return user


def ensure_user_exists(tg_user):
    try:
        user_doc = users_collection.find_one({"user_id": tg_user.id})
        username = tg_user.username.lower() if tg_user.username else None

        if not user_doc:
            new_user = {
                "user_id": tg_user.id,
                "name": tg_user.first_name,
                "username": username,
                "is_bot": tg_user.is_bot,
                "balance": 0,
                "inventory": [],
                "waifus": [],
                "daily_streak": 0,
                "last_daily": None,
                "kills": 0,
                "status": "alive",
                "protection_expiry": datetime.utcnow(),
                "registered_at": datetime.utcnow(),
                "death_time": None,
                "seen_groups": [],
                "xp": 0,
                "level": 1
            }
            users_collection.insert_one(new_user)
            return new_user

        ensure_user_fields(user_doc)

        if check_auto_revive(user_doc):
            user_doc["status"] = "alive"

        return user_doc

    except:
        return {"user_id": tg_user.id, "name": tg_user.first_name, "xp": 0, "level": 1}


# ---------------------------------------------------------
#                GROUP TRACKER (FIXED)
# ---------------------------------------------------------

def track_group(chat, user=None):
    try:
        if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:

            if not groups_collection.find_one({"chat_id": chat.id}):
                groups_collection.insert_one(
                    {"chat_id": chat.id, "title": chat.title, "claimed": False}
                )

            if user:
                users_collection.update_one(
                    {"user_id": user.id},
                    {"$addToSet": {"seen_groups": chat.id}}
                )

    except:
        pass


# ---------------------------------------------------------
#           LEVEL SYSTEM (1–10 + CUSTOM XP)
# ---------------------------------------------------------

LEVEL_XP = {
    1: 200,
    2: 500,
    3: 800,
    4: 1200,
    5: 1600,
    6: 2000,
    7: 2600,
    8: 3200,
    9: 4000,
}

LEVEL_BADGES = {
    1: "🟢 Rookie",
    2: "🔵 Explorer",
    3: "🟣 Elite",
    4: "🟠 Master",
    5: "🔥 Slayer",
    6: "💠 Ultra",
    7: "⭐ Supreme",
    8: "👑 Royal",
    9: "⚡ Mythic",
    10: "🐉 Dragon Lord"
}


def add_xp(user_id, amount: int):
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        return False, 1, 0

    user = ensure_user_fields(user)

    xp = user["xp"] + amount
    level = user["level"]

    if level >= 10:
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"xp": xp, "level": 10}}
        )
        return False, 10, xp

    required = LEVEL_XP[level]

    leveled = False

    if xp >= required:
        xp -= required
        level += 1
        leveled = True

    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"xp": xp, "level": level}}
    )

    return leveled, level, xp


def get_user_badge(level):
    return LEVEL_BADGES.get(level, "❓ Unknown Badge")


# ---------------------------------------------------------
#                XP LEADERBOARD
# ---------------------------------------------------------

def get_global_xp_leaderboard(limit=20):
    return list(
        users_collection.find({}, {"_id": 0})
        .sort("xp", -1)
        .limit(limit)
    )

def get_group_xp_leaderboard(group_id, limit=20):
    return list(
        users_collection.find({"seen_groups": group_id}, {"_id": 0})
        .sort("xp", -1)
        .limit(limit)
    )


# ---------------------------------------------------------
#          SAFE MENTION + FORMATTING
# ---------------------------------------------------------

def get_mention(user_data, custom_name=None):
    if isinstance(user_data, (User, Chat)):
        uid = user_data.id
        first_name = getattr(user_data, "first_name", None) or user_data.title
    elif isinstance(user_data, dict):
        uid = user_data["user_id"]
        first_name = user_data.get("name", "User")
    else:
        return "Unknown"

    name = custom_name or first_name
    return f"<a href='tg://user?id={uid}'><b>{html.escape(name)}</b></a>"


def format_money(v):
    return f"${v:,}"

def format_time(t):
    s = int(t.total_seconds())
    h, r = divmod(s, 3600)
    m, _ = divmod(r, 60)
    return f"{h}h {m}m"


# ---------------------------------------------------------
#               PROGRESS BAR (NEW)
# ---------------------------------------------------------

def get_progress_bar(xp, next_xp):
    filled = int((xp / next_xp) * 10)
    bar = "█" * filled + "░" * (10 - filled)
    return f"[{bar}]"
