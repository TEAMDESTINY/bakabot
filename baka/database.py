# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Database Logic - Sync with Game & Utils

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
# 👤 USER LOGIC (Fixed Field Names)
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
                "daily_kills": 0,
                "daily_robs": 0,
                "status": "alive",
                "waifus": [],
                "inventory": [],
                "protection_expiry": None, # Syncing with game.py
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
# 🛡️ PROTECTION CLEANUP (Fixed Field Name)
# --------------------------------------------------

def cleanup_expired_protection():
    """Sync with protection_expiry field name."""
    now = datetime.utcnow()
    result = users_collection.update_many(
        {"protection_expiry": {"$lte": now}},
        {"$set": {"protection_expiry": None}}
    )
    return result.modified_count
