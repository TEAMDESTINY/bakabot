# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# FINAL SYNCED CONFIG - AI KEYS & ADMIN LOGIC FIXED

import os
import time

# --- 🛠️ CORE SYSTEM ---
START_TIME = time.time()
TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
PORT = int(os.environ.get("PORT", 5000))

# --- 🔑 AI API KEYS (Fixed Import Issues) ---
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "") 
CODESTRAL_API_KEY = os.getenv("CODESTRAL_API_KEY", "")

# --- 📂 UPDATER & REPO ---
UPSTREAM_REPO = os.getenv("UPSTREAM_REPO", "")
GIT_TOKEN = os.getenv("GIT_TOKEN", "")

# --- 🖼️ ASSETS & LINKS ---
START_IMG_URL = os.getenv("START_IMG_URL", "https://files.catbox.moe/5u4z5p.jpg") 
HELP_IMG_URL = os.getenv("HELP_IMG_URL", "https://files.catbox.moe/5u4z5p.jpg") 
WELCOME_IMG_URL = os.getenv("WELCOME_IMG_URL", "https://files.catbox.moe/5u4z5p.jpg") 

SUPPORT_GROUP = os.getenv("SUPPORT_GROUP", "https://t.me/YourSupportGroup")
SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", "https://t.me/YourUpdateChannel")
OWNER_LINK = os.getenv("OWNER_LINK", "https://t.me/YourOwnerUsername")

# --- 🆔 IDENTITIES ---
def get_env_id(var, default=0):
    val = os.getenv(var, str(default)).strip()
    return int(val) if val.replace('-', '').isdigit() else default

LOGGER_ID = get_env_id("LOGGER_ID")
OWNER_ID = get_env_id("OWNER_ID")

# SUDO_IDS: Heroku environment variable ko list mein convert karna
SUDO_IDS_STR = os.getenv("SUDO_IDS", "")
if SUDO_IDS_STR:
    SUDO_IDS = [int(x.strip()) for x in SUDO_IDS_STR.split(",") if x.strip().isdigit()]
else:
    SUDO_IDS = []

# Safety Check: Owner hamesha Sudo list mein hona chahiye
if OWNER_ID and OWNER_ID not in SUDO_IDS:
    SUDO_IDS.append(OWNER_ID)

# --- 💰 ECONOMY CONSTANTS ---
BOT_NAME = "𝐁ᴀᴋᴀ 💗"
REGISTER_BONUS = 50       
DAILY_BONUS = 1000        # $1000 (DM Only)
BONUS_COOLDOWN = 12        # 12-hour gap

# --- ⚔️ GAME LIMITS ---
KILL_LIMIT_DAILY = 100    
ROB_LIMIT_DAILY = 200     
ROB_MAX_AMOUNT = 500000   
KILL_SPAM_COOLDOWN = 3    

# --- 🛡️ PROTECTION & DEATH ---
PROTECT_1D_COST = 100     
PROTECT_2D_COST = 500     
REVIVE_COST = 200         
AUTO_REVIVE_HOURS = 5     

# --- 📊 SHOP & TAX ---
TAX_RATE = 0.10           
MIN_CLAIM_MEMBERS = 100   
RIDDLE_REWARD = 1000      
CLAIM_BONUS = 2000
DIVORCE_COST = 2000
WAIFU_PROPOSE_COST = 5000

# --- 🛒 SHOP ITEMS ---
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
    {"id": "plot", "name": "🎬 Plot Armor", "price": 10000000, "type": "armor", "buff": 0.60}
]
