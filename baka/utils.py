# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Utils - Destiny / Baka Bot (PRODUCTION READY)

import html
import re
from datetime import datetime, timedelta
from telegram import Bot
from telegram.constants import ParseMode, ChatType

from baka.database import users_collection, sudoers_collection, groups_collection
from baka.config import (
    OWNER_ID,
    SUDO_IDS_STR,
    LOGGER_ID,
    AUTO_REVIVE_HOURS,
)

# --------------------------------------------------
# SUDO SYSTEM
# --------------------------------------------------

SUDO_USERS = set()

def reload_sudoers():
    """Load sudo users from env + database."""
    SUDO_USERS.clear()
    SUDO_USERS.add(OWNER_ID)

    if SUDO_IDS_STR:
        for x in SUDO_IDS_STR.split(','):
            if x.strip().isdigit():
                SUDO_USERS.add(int(x.strip()))

    for doc in sudoers_collection.find({}):
        SUDO_USERS.add(doc['user_id'])

reload_sudoers()

# --------------------------------------------------
# 🌸 SERIF ITALIC FONT ENGINE (SAFE)
# --------------------------------------------------

def stylize_text(text: str) -> str:
    font_map = {
        'A': '𝐴','B': '𝐵','C': '𝐶','D': '𝐷','E': '𝐸','F': '𝐹','G': '𝐺',
        'H': '𝐻','I': '𝐼','J': '𝐽','K': '𝐾','L': '𝐿','M': '𝑀','N': '𝑁',
        'O': '𝑂','P': '𝑃','Q': '𝑄','R': '𝑅','S': '𝑆','T': '𝑇','U': '𝑈',
        'V': '𝑉','W': '𝑊','X': '𝑋','Y': '𝑌','Z': '𝑍',
        'a': '𝑎','b': '𝑏','c': '𝑐','d': '𝑑','e': '𝑒','f': '𝑓','g': '𝑔',
        'h': 'ℎ','i': '𝑖','j': '𝑗','k': '𝑘','l': '𝑙','m': '𝑚','n': '𝑛',
        'o': '𝑜','p': '𝑝','q': '𝑞','r': '𝑟','s': '𝑠','t': '𝑡','u': '𝑢',
        'v': '𝑣','w': '𝑤','x': '𝑥','y': '𝑦','z': '𝑧',
        '0': '𝟎','1': '𝟏','2': '𝟐','3': '𝟑','4': '𝟒',
        '5': '𝟓','6': '𝟔','7': '𝟕','8': '𝟖','9': '𝟗'
    }

    def apply(s):
        return ''.join(font_map.get(c, c) for c in s)

    pattern = r"(@\w+|https?://\S+|`[^`]+`|/[a-zA-Z0-9_]+)"
    parts = re.split(pattern, str(text))

    return ''.join(p if re.match(pattern, p) else apply(p) for p in parts)

# --------------------------------------------------
# 👤 MENTION ENGINE (Baka Compatible)
# --------------------------------------------------

def get_mention(user_data, custom_name=None) -> str:
    if not user_data:
        return 'Unknown'

    if hasattr(user_data, 'id'):
        uid = user_data.id
        name = user_data.first_name
    elif isinstance(user_data, dict):
        uid = user_data.get('user_id')
        name = user_data.get('name', 'User')
    else:
        return 'User'

    final_name = custom_name or name
    return f"<a href='tg://user?id={uid}'><b><i>{html.escape(str(final_name))}</i></b></a>"

# --------------------------------------------------
# 📊 LOGGER (HTML SAFE)
# --------------------------------------------------

async def log_to_channel(bot: Bot, event_type: str, details: dict):
    if not LOGGER_ID:
        return

    now = datetime.utcnow().strftime('%I:%M:%S %p')
    text = f"🌸 <b>{stylize_text(event_type.upper())}</b>\n━━━━━━━━━━━━━━━━━━\n"

    for k, v in details.items():
        text += f"🔹 <b>{stylize_text(k.title())}:</b> {html.escape(str(v))}\n"

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

# --------------------------------------------------
# 🏰 GROUP TRACKER
# --------------------------------------------------

def track_group(chat, user=None):
    if chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        return

    groups_collection.update_one(
        {'chat_id': chat.id},
        {
            '$setOnInsert': {
                'chat_id': chat.id,
                'title': chat.title,
                'treasury': 10000,
                'claimed': False,
                'daily_activity': 0,
                'weekly_activity': 0
            }
        },
        upsert=True
    )

    if user:
        users_collection.update_one(
            {'user_id': user.id},
            {'$addToSet': {'seen_groups': chat.id}}
        )

# --------------------------------------------------
# 👤 USER ENSURE (SYNCED WITH DB LOGIC)
# --------------------------------------------------

def ensure_user_exists(tg_user):
    users_collection.update_one(
        {'user_id': tg_user.id},
        {
            '$setOnInsert': {
                'user_id': tg_user.id,
                'name': tg_user.first_name,
                'username': tg_user.username.lower() if tg_user.username else None,
                'balance': 500,
                'kills': 0,
                'status': 'alive',
                'waifus': [],
                'protection': None,
                'created_at': datetime.utcnow()
            }
        },
        upsert=True
    )

    users_collection.update_one(
        {'user_id': tg_user.id},
        {
            '$set': {
                'name': tg_user.first_name,
                'username': tg_user.username.lower() if tg_user.username else None
            }
        }
    )

    return users_collection.find_one({'user_id': tg_user.id})

# --------------------------------------------------
# 🎯 TARGET RESOLVER (ROB / KILL SAFE)
# --------------------------------------------------

async def resolve_target(update, context, specific_arg=None):
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        doc = ensure_user_exists(user)
        doc['user_obj'] = user
        return doc, None

    query = specific_arg or (context.args[0] if context.args else None)
    if not query:
        return None, 'No target'

    if query.isdigit():
        doc = users_collection.find_one({'user_id': int(query)})
    else:
        doc = users_collection.find_one({'username': query.replace('@', '').lower()})

    if not doc:
        return None, f"❌ <b>{stylize_text('User not found!')}</b>"

    doc['user_obj'] = doc
    return doc, None

# --------------------------------------------------
# 🛡️ PROTECTION & TIME
# --------------------------------------------------

def get_active_protection(user_data):
    expiry = user_data.get('protection')
    return expiry if expiry and expiry > datetime.utcnow() else None


def format_money(amount: int) -> str:
    return f"${amount:,}"


def format_time(td: timedelta) -> str:
    secs = int(td.total_seconds())
    h, rem = divmod(secs, 3600)
    m, _ = divmod(rem, 60)
    return f"{h}h {m}m"

# --------------------------------------------------
# ❤️ AUTO REVIVE
# --------------------------------------------------

def check_auto_revive(user_doc):
    if user_doc.get('status') != 'dead':
        return False

    death_time = user_doc.get('death_time')
    if death_time and datetime.utcnow() - death_time >= timedelta(hours=AUTO_REVIVE_HOURS):
        users_collection.update_one(
            {'user_id': user_doc['user_id']},
            {'$set': {'status': 'alive', 'death_time': None}}
        )
        return True

    return False
