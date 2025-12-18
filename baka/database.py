# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Database Logic - Destiny / Baka Bot (OPTIMIZED)

from pymongo import MongoClient, ASCENDING
import certifi
import time
from datetime import datetime
from baka.config import MONGO_URI

# --------------------------------------------------
# Mongo Connection (High Performance)
# --------------------------------------------------
RyanBaka = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = RyanBaka["bakabot_db"]

# Collections
users_collection   = db["users"]
groups_collection  = db["groups"]
sudoers_collection = db["sudoers"]
chatbot_collection = db["chatbot"]
riddles_collection = db["riddles"]

# Indexes
users_collection.create_index([("user_id", ASCENDING)], unique=True)
groups_collection.create_index([("chat_id", ASCENDING)], unique=True)

# --------------------------------------------------
# 👤 USER LOGIC (SMART SYNC)
# --------------------------------------------------

def ensure_user(user):
    """Create or Sync user data atomically."""
    users_collection.update_one(
        {"user_id": user.id},
        {
            "$setOnInsert": {
                "user_id": user.id,
                "balance": 500,
                "kills": 0,
                "status": "alive",
                "waifus": [],
                "inventory": [],
                "protection": None,
                "created_at": datetime.utcnow()
            },
            "$set": {
                "name": user.first_name,
                "username": user.username.lower() if user.username else None
            }
        },
        upsert=True
    )
    return users_collection.find_one({"user_id": user.id})

# --------------------------------------------------
# 🏰 GROUP LOGIC (ECONOMY SYNC)
# --------------------------------------------------

def get_group_data(chat_id, title=None):
    """Fetch group data with auto-repair for missing fields."""
    group = groups_collection.find_one({"chat_id": chat_id})

    if not group:
        group = {
            "chat_id": chat_id,
            "title": title or "Unknown Group",
            "treasury": 10000,
            "claimed": False,
            "shares": 10.0,
            "daily_activity": 0,
            "weekly_activity": 0,
            "last_active": int(time.time())
        }
        groups_collection.insert_one(group)
    else:
        # Auto-fill missing keys if ChatGPT missed them
        defaults = {
            "daily_activity": 0, 
            "weekly_activity": 0, 
            "claimed": False, 
            "treasury": 10000
        }
        updates = {k: v for k, v in defaults.items() if k not in group}
        if title and group.get("title") != title:
            updates["title"] = title
            
        if updates:
            groups_collection.update_one({"chat_id": chat_id}, {"$set": updates})
            group.update(updates)

    return group

def update_group_activity(chat_id, title=None):
    """Increments stats on every message."""
    groups_collection.update_one(
        {"chat_id": chat_id},
        {
            "$inc": {"daily_activity": 1, "weekly_activity": 1, "treasury": 10},
            "$set": {"last_active": int(time.time()), "title": title} if title else {"$set": {"last_active": int(time.time())}}
        },
        upsert=True
    )

# --------------------------------------------------
# 🛡️ PROTECTION & MAINTENANCE
# --------------------------------------------------

def cleanup_expired_protection():
    """Removes protection shield once time is up."""
    now = datetime.utcnow()
    result = users_collection.update_many(
        {"protection": {"$lte": now}},
        {"$set": {"protection": None}}
    )
    return result.modified_count

def reset_daily_stats():
    """Daily reset for /claim and activity."""
    groups_collection.update_many({}, {"$set": {"daily_activity": 0, "claimed": False}})

# --------------------------------------------------
# USER HELPERS
# --------------------------------------------------

def get_user_waifus(user_id):
    user = users_collection.find_one({"user_id": user_id})
    return user.get("waifus", []) if user else []
