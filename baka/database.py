# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Database Logic - Destiny / Baka Bot (FIXED IMPORT ERRORS)

from pymongo import MongoClient, ASCENDING
import certifi
import time
from datetime import datetime
from baka.config import MONGO_URI

# --------------------------------------------------
# Mongo Connection
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
# 👤 USER LOGIC
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
# 🏰 GROUP LOGIC
# --------------------------------------------------

def get_group_data(chat_id, title=None):
    group = groups_collection.find_one({"chat_id": chat_id})
    if not group:
        group = {
            "chat_id": chat_id,
            "title": title or "Unknown Group",
            "treasury": 10000,
            "claimed": False,
            "daily_activity": 0,
            "weekly_activity": 0,
            "last_active": int(time.time())
        }
        groups_collection.insert_one(group)
    return group

def update_group_activity(chat_id, title=None):
    groups_collection.update_one(
        {"chat_id": chat_id},
        {
            "$inc": {"daily_activity": 1, "weekly_activity": 1, "treasury": 10},
            "$set": {"last_active": int(time.time()), "title": title} if title else {"$set": {"last_active": int(time.time())}}
        },
        upsert=True
    )

# --------------------------------------------------
# 🔄 RESET LOGIC (FIXED NAMES)
# --------------------------------------------------

def reset_daily_activity():
    """Import fix: Resets daily activity and claims."""
    result = groups_collection.update_many(
        {},
        {"$set": {"daily_activity": 0, "claimed": False}}
    )
    print(f"✨ Daily Stats Reset: {result.modified_count} groups")

def reset_weekly_activity():
    """Import fix: Resets weekly activity."""
    result = groups_collection.update_many(
        {},
        {"$set": {"weekly_activity": 0}}
    )
    print(f"👑 Weekly Stats Reset: {result.modified_count} groups")

# --------------------------------------------------
# 🛡️ PROTECTION CLEANUP
# --------------------------------------------------

def cleanup_expired_protection():
    now = datetime.utcnow()
    result = users_collection.update_many(
        {"protection": {"$lte": now}},
        {"$set": {"protection": None}}
    )
    return result.modified_count
