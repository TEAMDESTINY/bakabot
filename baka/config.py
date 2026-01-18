# Copyright (c) 2026
# Telegram: @WTF_Phantom <DevixOP>
# FINAL STABLE CONFIG

import os
import time

# ───────────────────── CORE ─────────────────────
START_TIME = time.time()

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError(
        "❌ BOT_TOKEN is missing.\n"
        "Set it using:\n"
        "export BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN"
    )

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError(
        "❌ MONGO_URI is missing.\n"
        "Set it using:\n"
        "export MONGO_URI=your_mongodb_uri"
    )

PORT = int(os.getenv("PORT", 5000))

# ───────────────────── AI KEYS ─────────────────────
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
CODESTRAL_API_KEY = os.getenv("CODESTRAL_API_KEY", "")

# ───────────────────── GIT / UPDATER ─────────────────────
UPSTREAM_REPO = os.getenv("UPSTREAM_REPO", "")
GIT_TOKEN = os.getenv("GIT_TOKEN", "")

# ───────────────────── ASSETS ─────────────────────
START_IMG_URL = os.getenv(
    "START_IMG_URL",
    "https://files.catbox.moe/5u4z5p.jpg"
)
HELP_IMG_URL = os.getenv(
    "HELP_IMG_URL",
    "https://files.catbox.moe/5u4z5p.jpg"
)
WELCOME_IMG_URL = os.getenv(
    "WELCOME_IMG_URL",
    "https://files.catbox.moe/5u4z5p.jpg"
)

SUPPORT_GROUP = os.getenv("SUPPORT_GROUP", "")
SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", "")
OWNER_LINK = os.getenv("OWNER_LINK", "")

# ───────────────────── IDS ─────────────────────
def get_env_id(name: str, default: int = 0) -> int:
    val = os.getenv(name, "").strip()
    return int(val) if val.lstrip("-").isdigit() else default

OWNER_ID = get_env_id("OWNER_ID")
LOGGER_ID = get_env_id("LOGGER_ID")

SUDO_IDS = []
sudo_raw = os.getenv("SUDO_IDS", "")
if sudo_raw:
    SUDO_IDS = [
        int(x) for x in sudo_raw.split(",")
        if x.strip().lstrip("-").isdigit()
    ]

if OWNER_ID and OWNER_ID not in SUDO_IDS:
    SUDO_IDS.append(OWNER_ID)

# ───────────────────── ECONOMY ─────────────────────
BOT_NAME = "𝐁ᴀᴋᴀ 💗"

REGISTER_BONUS = 50
DAILY_BONUS = 1000
BONUS_COOLDOWN = 12  # hours

REVIVE_COST = 200
DIVORCE_COST = 2000
WAIFU_PROPOSE_COST = 5000

# ───────────────────── GAME LIMITS ─────────────────────
KILL_LIMIT_DAILY = 100
ROB_LIMIT_DAILY = 200
ROB_MAX_AMOUNT = 500_000
KILL_SPAM_COOLDOWN = 3  # seconds

# ───────────────────── PROTECTION ─────────────────────
PROTECT_1D_COST = 100
PROTECT_2D_COST = 500
AUTO_REVIVE_HOURS = 5

# ───────────────────── TAX / CLAIM ─────────────────────
TAX_RATE = 0.10
MIN_CLAIM_MEMBERS = 100
RIDDLE_REWARD = 1000
CLAIM_BONUS = 2000

# ───────────────────── SHOP ─────────────────────
SHOP_ITEMS = [
    {"id": "stick", "name": "🪵 Stick", "price": 500, "type": "weapon", "buff": 0.01},
    {"id": "knife", "name": "🔪 Knife", "price": 3500, "type": "weapon", "buff": 0.05},
    {"id": "pistol", "name": "🔫 Pistol", "price": 25000, "type": "weapon", "buff": 0.20},
    {"id": "ak47", "name": "💥 AK-47", "price": 100000, "type": "weapon", "buff": 0.40},
    {"id": "rpg", "name": "🚀 RPG", "price": 300000, "type": "weapon", "buff": 0.55},
    {"id": "deathnote", "name": "📓 Death Note", "price": 5000000, "type": "weapon", "buff": 0.60},

    {"id": "cloth", "name": "👕 Cloth", "price": 2500, "type": "armor", "buff": 0.05},
    {"id": "riot", "name": "🛡️ Riot Shield", "price": 40000, "type": "armor", "buff": 0.15},
    {"id": "iron", "name": "🦾 Iron Suit", "price": 100000, "type": "armor", "buff": 0.25},
    {"id": "vibranium", "name": "🛡️ Vibranium", "price": 1500000, "type": "armor", "buff": 0.50},
    {"id": "plot", "name": "🎬 Plot Armor", "price": 10000000, "type": "armor", "buff": 0.60},
]
