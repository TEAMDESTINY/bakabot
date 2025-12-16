# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Database Logic - Fixed "Unknown" Names & Multi-Leaderboard

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

def get_group_data(chat_id, title=None):
    """
    Group ki economy details fetch ya create karne ke liye.
    Multi-Leaderboard ke liye fields ensure karta hai.
    """
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
        # Title update logic agar name change hua ho
        updates = {}
        if title and group.get("title") != title:
            updates["title"] = title
        if "daily_activity" not in group: updates["daily_activity"] = 0
        if "weekly_activity" not in group: updates["weekly_activity"] = 0
        if "shares" not in group: updates["shares"] = 10.0
        
        if updates:
            groups_collection.update_one({"chat_id": chat_id}, {"$set": updates})
            group.update(updates)

    return group

def update_group_activity(chat_id, title=None):
    """
    Har message par group ka naam update karne aur activity badhane ke liye.
    Isse Leaderboard par real names dikhenge.
    """
    update_query = {
        "$inc": {"daily_activity": 1, "weekly_activity": 1},
        "$set": {"last_active": int(time.time())}
    }
    
    # "Unknown" hatane ke liye group title update
    if title:
        update_query["$set"]["title"] = title

    groups_collection.update_one(
        {"chat_id": chat_id},
        update_query,
        upsert=True
    )

# --- RESET LOGIC FUNCTIONS ---

def reset_daily_activity():
    """Daily leaderboard stats reset"""
    result = groups_collection.update_many({}, {"$set": {"daily_activity": 0}})
    print(f"✨ Daily Activity Reset: {result.modified_count} groups updated.")

def reset_weekly_activity():
    """Weekly leaderboard stats reset"""
    result = groups_collection.update_many({}, {"$set": {"weekly_activity": 0}})
    print(f"👑 Weekly Activity Reset: {result.modified_count} groups updated.")
