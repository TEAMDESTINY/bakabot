# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# FINAL SYNCED CONFIG – VPS READY (LOCAL MONGODB)

import os
import time

# --------------------------------------------------
# 🛠️ CORE SYSTEM
# --------------------------------------------------

START_TIME = time.time()

TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Local MongoDB default (NO SSL)
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://127.0.0.1:27017"
).strip()

PORT = int(os.getenv("PORT", 5000))

# --------------------------------------------------
# 🔑 AI API KEYS
# --------------------------------------------------

MISTRAL_API_KEY   = os.getenv("MISTRAL_API_KEY", "").strip()
GROQ_API_KEY      = os.getenv("GROQ_API_KEY", "").strip()
CODESTRAL_API_KEY = os.getenv("CODESTRAL_API_KEY", "").strip()

# --------------------------------------------------
# 📂 UPDATER & REPO
# --------------------------------------------------

UPSTREAM_REPO = os.getenv("UPSTREAM_REPO", "").strip()
GIT_TOKEN     = os.getenv("GIT_TOKEN", "").strip()

# --------------------------------------------------
# 🖼️ ASSETS & LINKS
# --------------------------------------------------

START_IMG_URL   = os.getenv("START_IMG_URL",   "https://files.catbox.moe/5u4z5p.jpg")
HELP_IMG_URL    = os.getenv("HELP_IMG_URL",    "https://files.catbox.moe/5u4z5p.jpg")
WELCOME_IMG_URL = os.getenv("WELCOME_IMG_URL", "https://files.catbox.moe/5u4z5p.jpg")

SUPPORT_GROUP   = os.getenv("SUPPORT_GROUP",   "https://t.me/YourSupportGroup")
SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", "https://t.me/YourUpdateChannel")
OWNER_LINK      = os.getenv("OWNER_LINK",      "https://t.me/YourOwnerUsername")

# --------------------------------------------------
# 🆔 IDENTITIES
# --------------------------------------------------

def get_env_id(var, default=0):
    val = os.getenv(var, "").strip()
    return int(val) if val.replace("-", "").isdigit() else default

LOGGER_ID = get_env_id("LOGGER_ID")
OWNER_ID  = get_env_id("OWNER_ID")

# SUDO USERS
SUDO_IDS_RAW = os.getenv("SUDO_IDS", "")
SUDO_IDS = [int(x) for x in SUDO_IDS_RAW.split(",") if x.strip().isdigit()]

# Owner must always be sudo
if OWNER_ID and OWNER_ID not in SUDO_IDS:
    SUDO_IDS.append(OWNER_ID)

# --------------------------------------------------
# 💰 ECONOMY CONSTANTS
# --------------------------------------------------

BOT_NAME = "𝐁ᴀᴋᴀ 💗"

REGISTER_BONUS = 50
DAILY_BONUS    = 1000
BONUS_COOLDOWN = 12  # hours

# --------------------------------------------------
# ⚔️ GAME LIMITS
# --------------------------------------------------

KILL_LIMIT_DAILY   = 100
ROB_LIMIT_DAILY    = 200
ROB_MAX_AMOUNT     = 500_000
KILL_SPAM_COOLDOWN = 3  # seconds

# --------------------------------------------------
# 🛡️ PROTECTION & REVIVE
# --------------------------------------------------

PROTECT_1D_COST    = 100
PROTECT_2D_COST    = 500
REVIVE_COST        = 200
AUTO_REVIVE_HOURS  = 5

# --------------------------------------------------
# 📊 SHOP, TAX & EVENTS
# --------------------------------------------------

TAX_RATE           = 0.10
MIN_CLAIM_MEMBERS  = 100
RIDDLE_REWARD      = 1000
CLAIM_BONUS        = 2000
DIVORCE_COST       = 2000
WAIFU_PROPOSE_COST = 5000

# --------------------------------------------------
# 🛒 SHOP ITEMS
# --------------------------------------------------

SHOP_ITEMS = [
    {"id": "stick",      "name": "🪵 Stick",        "price": 500,       "type": "weapon", "buff": 0.01},
    {"id": "knife",      "name": "🔪 Knife",        "price": 3500,      "type": "weapon", "buff": 0.05},
    {"id": "pistol",     "name": "🔫 Pistol",       "price": 25000,     "type": "weapon", "buff": 0.20},
    {"id": "ak47",       "name": "💥 AK-47",        "price": 100000,    "type": "weapon", "buff": 0.40},
    {"id": "rpg",        "name": "🚀 RPG",          "price": 300000,    "type": "weapon", "buff": 0.55},
    {"id": "deathnote",  "name": "📓 Death Note",   "price": 5_000_000, "type": "weapon", "buff": 0.60},

    {"id": "cloth",      "name": "👕 Cloth",        "price": 2500,      "type": "armor",  "buff": 0.05},
    {"id": "riot",       "name": "🛡️ Riot Shield",  "price": 40000,     "type": "armor",  "buff": 0.15},
    {"id": "iron",       "name": "🦾 Iron Suit",    "price": 100000,    "type": "armor",  "buff": 0.25},
    {"id": "vibranium",  "name": "🛡️ Vibranium",   "price": 1_500_000, "type": "armor",  "buff": 0.50},
    {"id": "plot",       "name": "🎬 Plot Armor",   "price": 10_000_000,"type": "armor",  "buff": 0.60},
]

# --------------------------------------------------
# 🔒 SAFETY CHECKS
# --------------------------------------------------

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing in environment variables")
