# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Database Logic - Optimized for Destiny Bot

from pymongo import MongoClient
import certifi
import time
from baka.config import MONGO_URI

# Initialize Connection
RyanBaka = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = RyanBaka["bakabot_db"]

# --- DEFINING COLLECTIONS ---
users_collection = db["users"]        
groups_collection = db["groups"]      
sudoers_collection = db["sudoers"]    
chatbot_collection = db["chatbot"]    
riddles_collection = db["riddles"]

# --- GROUP LOGIC ---

def get_group_data(chat_id, title=None):
    """Group details fetch or create logic with multi-field support."""
    group = groups_collection.find_one({"chat_id": chat_id})
    
    if not group:
        group = {
            "chat_id": chat_id,
            "title": title or "Unknown Group",
            "treasury": 10000,          
            "claimed": False, # Daily claim tracker
            "shares": 10.0,             
            "daily_activity": 0,        
            "weekly_activity": 0,       
            "last_active": int(time.time())
        }
        groups_collection.insert_one(group)
    
    else:
        # Auto-update missing fields and title
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
    """Updates group title and increments activity points on every message."""
    update_query = {
        "$inc": {"daily_activity": 1, "weekly_activity": 1, "treasury": 10},
        "$set": {"last_active": int(time.time())}
    }
    
    if title:
        update_query["$set"]["title"] = title

    groups_collection.update_one(
        {"chat_id": chat_id},
        update_query,
        upsert=True
    )

# --- RESET LOGIC FUNCTIONS ---

def reset_daily_activity():
    """Resets daily leaderboard and daily group claims at midnight."""
    # Resetting activity AND daily claim status
    result = groups_collection.update_many({}, {"$set": {"daily_activity": 0, "claimed": False}})
    print(f"✨ Daily Stats & Claims Reset: {result.modified_count} groups updated.")

def reset_weekly_activity():
    """Weekly leaderboard stats reset."""
    result = groups_collection.update_many({}, {"$set": {"weekly_activity": 0}})
    print(f"👑 Weekly Activity Reset: {result.modified_count} groups updated.")

# --- USER HELPER (Optional but recommended) ---
def get_user_waifus(user_id):
    user = users_collection.find_one({"user_id": user_id})
    return user.get("waifus", []) if user else []
