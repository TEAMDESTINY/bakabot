# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Database Logic - Destiny / Baka Bot (PRODUCTION READY)

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

# --------------------------------------------------
# Collections
# --------------------------------------------------

users_collection   = db["users"]
groups_collection  = db["groups"]
sudoers_collection = db["sudoers"]
chatbot_collection = db["chatbot"]
riddles_collection = db["riddles"]

# --------------------------------------------------
# Indexes (Performance Boost)
# --------------------------------------------------

users_collection.create_index([("user_id", ASCENDING)], unique=True)
groups_collection.create_index([("chat_id", ASCENDING)], unique=True)

# --------------------------------------------------
# USER LOGIC (SAFE AUTO CREATE)
# --------------------------------------------------

def ensure_user(user):
    """Create user if not exists (atomic & safe)."""
    users_collection.update_one(
        {"user_id": user.id},
        {
            "$setOnInsert": {
                "user_id": user.id,
                "name": user.first_name,
                "username": user.username,
                "balance": 500,
                "kills": 0,
                "status": "alive",
                "waifus": [],
                "protection": None,
                "created_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    return users_collection.find_one({"user_id": user.id})

# --------------------------------------------------
# GROUP LOGIC
# --------------------------------------------------

def get_group_data(chat_id, title=None):
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
        updates = {}
        if title and group.get("title") != title:
            updates["title"] = title
        if "daily_activity" not in group: updates["daily_activity"] = 0
        if "weekly_activity" not in group: updates["weekly_activity"] = 0
        if "claimed" not in group: updates["claimed"] = False
        if "shares" not in group: updates["shares"] = 10.0

        if updates:
            groups_collection.update_one({"chat_id": chat_id}, {"$set": updates})
            group.update(updates)

    return group

def update_group_activity(chat_id, title=None):
    update_query = {
        "$inc": {
            "daily_activity": 1,
            "weekly_activity": 1,
            "treasury": 10
        },
        "$set": {
            "last_active": int(time.time())
        }
    }

    if title:
        update_query["$set"]["title"] = title

    groups_collection.update_one(
        {"chat_id": chat_id},
        update_query,
        upsert=True
    )

# --------------------------------------------------
# RESET LOGIC
# --------------------------------------------------

def reset_daily_activity():
    result = groups_collection.update_many(
        {},
        {"$set": {"daily_activity": 0, "claimed": False}}
    )
    print(f"✨ Daily Stats Reset: {result.modified_count} groups")

def reset_weekly_activity():
    result = groups_collection.update_many(
        {},
        {"$set": {"weekly_activity": 0}}
    )
    print(f"👑 Weekly Stats Reset: {result.modified_count} groups")

# --------------------------------------------------
# CLEANUP: EXPIRED PROTECTION
# --------------------------------------------------

def cleanup_expired_protection():
    now = datetime.utcnow()
    users_collection.update_many(
        {"protection": {"$lte": now}},
        {"$set": {"protection": None}}
    )

# --------------------------------------------------
# USER HELPER
# --------------------------------------------------

def get_user_waifus(user_id):
    user = users_collection.find_one({"user_id": user_id})
    return user.get("waifus", []) if user else []
