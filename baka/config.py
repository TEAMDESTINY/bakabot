# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Location: Bihar | All rights reserved.

import os
import time

# --- CORE SYSTEM ---
START_TIME = time.time()
TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
PORT = int(os.environ.get("PORT", 5000))

# --- AI API KEYS ---
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "") 
CODESTRAL_API_KEY = os.getenv("CODESTRAL_API_KEY", MISTRAL_API_KEY)

# --- UPDATER & REPO ---
UPSTREAM_REPO = os.getenv("UPSTREAM_REPO", "")
GIT_TOKEN = os.getenv("GIT_TOKEN", "")

# --- ASSETS & LINKS ---
START_IMG_URL = os.getenv("START_IMG_URL", "https://files.catbox.moe/28no0e.jpg") 
HELP_IMG_URL = os.getenv("HELP_IMG_URL", "https://files.catbox.moe/5g37fy.jpg") 
WELCOME_IMG_URL = os.getenv("WELCOME_IMG_URL", "https://files.catbox.moe/28no0e.jpg") 

SUPPORT_GROUP = os.getenv("SUPPORT_GROUP", "https://t.me/YourSupportGroup")
SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", "https://t.me/YourUpdateChannel")
OWNER_LINK = os.getenv("OWNER_LINK", "https://t.me/YourOwnerUsername")

# --- IDENTITIES (IDs) ---
def get_env_id(var, default=0):
    val = os.getenv(var, str(default)).strip()
    return int(val) if val.replace('-', '').isdigit() else default

LOGGER_ID = get_env_id("LOGGER_ID")
OWNER_ID = get_env_id("OWNER_ID")
SUDO_IDS_STR = os.getenv("SUDO_IDS", "")

# --- GAME CONSTANTS ---
BOT_NAME = "🦋⃟𝘿𝙚𝙨𝙩𝙞𝙣𝙮"
REVIVE_COST = 500
PROTECT_1D_COST = 1000
PROTECT_2D_COST = 1800
REGISTER_BONUS = 5000
CLAIM_BONUS = 2000
RIDDLE_REWARD = 1000
DIVORCE_COST = 2000
WAIFU_PROPOSE_COST = 5000
TAX_RATE = 0.10
MARRIED_TAX_RATE = 0.05
AUTO_REVIVE_HOURS = 6
AUTO_REVIVE_BONUS = 200
MIN_CLAIM_MEMBERS = 100

# --- 🛒 SHOP ITEMS (Categorized for UI) ---
SHOP_ITEMS = [
    # ⚔️ WEAPONS (Attack Buffs)
    {"id": "stick", "name": "🪵 Stick", "price": 500, "type": "weapon", "buff": 0.01},
    {"id": "knife", "name": "🔪 Knife", "price": 3500, "type": "weapon", "buff": 0.05},
    {"id": "pistol", "name": "🔫 Pistol", "price": 25000, "type": "weapon", "buff": 0.20},
    {"id": "ak47", "name": "💥 AK-47", "price": 100000, "type": "weapon", "buff": 0.40},
    {"id": "rpg", "name": "🚀 RPG", "price": 300000, "type": "weapon", "buff": 0.55},
    {"id": "deathnote", "name": "📓 Death Note", "price": 5000000, "type": "weapon", "buff": 0.60},

    # 🛡️ ARMOR (Defense Buffs)
    {"id": "cloth", "name": "👕 Cloth", "price": 2500, "type": "armor", "buff": 0.05},
    {"id": "riot", "name": "🛡️ Riot Shield", "price": 40000, "type": "armor", "buff": 0.15},
    {"id": "iron", "name": "🦾 Iron Suit", "price": 100000, "type": "armor", "buff": 0.25},
    {"id": "vibranium", "name": "🛡️ Vibranium", "price": 1500000, "type": "armor", "buff": 0.50},
    {"id": "plot", "name": "🎬 Plot Armor", "price": 10000000, "type": "armor", "buff": 0.60},

    # 💎 FLEX (Collection)
    {"id": "iphone", "name": "📱 iPhone 16 Pro", "price": 25000, "type": "flex", "buff": 0},
    {"id": "lambo", "name": "🏎️ Lambo", "price": 800000, "type": "flex", "buff": 0},
    {"id": "mansion", "name": "🏰 Mansion", "price": 5000000, "type": "flex", "buff": 0},
    {"id": "island", "name": "🏝️ Island", "price": 50000000, "type": "flex", "buff": 0},
    {"id": "galaxy", "name": "🌌 Milky Way", "price": 5000000000, "type": "flex", "buff": 0},
    {"id": "blackhole", "name": "🕳️ Black Hole", "price": 9999999999, "type": "flex", "buff": 0},
]
