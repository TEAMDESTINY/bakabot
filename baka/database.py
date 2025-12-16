# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Database Logic for Destiny Bot - Integrated with Reset Logic

from pymongo import MongoClient
import certifi
import time
from baka.config import MONGO_URI

# Initialize Connection
RyanBaka = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = RyanBaka["bakabot_db"]

# --- DEFINING COLLECTIONS ---
users_collection = db["users"]       # Balance, EXP, Inventory, last_chat_id
groups_collection = db["groups"]     # Treasury, Stock Price, Daily/Weekly Activity
sudoers_collection = db["sudoers"]   
chatbot_collection = db["chatbot"]   
riddles_collection = db["riddles"]

def get_group_data(chat_id, title=None):
    """
    Group ki economy details fetch ya create karne ke liye.
    Multi-Leaderboard (Today/Weekly) ke liye fields ensure karta hai.
    """
    group = groups_collection.find_one({"chat_id": chat_id})
    
    if not group:
        group = {
            "chat_id": chat_id,
            "title": title or "Unknown Group",
            "treasury": 10000,          # New groups starting bonus
            "claimed": False,
            "shares": 10.0,             # Initial stock price
            "daily_activity": 0,        # Today's leaderboard ke liye
            "weekly_activity": 0,       # Weekly leaderboard ke liye
            "last_active": int(time.time())
        }
        groups_collection.insert_one(group)
    
    else:
        updates = {}
        if "daily_activity" not in group: updates["daily_activity"] = 0
        if "weekly_activity" not in group: updates["weekly_activity"] = 0
        if "shares" not in group: updates["shares"] = 10.0
        
        if updates:
            groups_collection.update_one({"chat_id": chat_id}, {"$set": updates})
            group.update(updates)

    return group

def update_group_activity(chat_id):
    """
    Har message par group ki activity points badhane ke liye.
    Isse 'Today' aur 'Weekly' ranks decide hongi.
    """
    groups_collection.update_one(
        {"chat_id": chat_id},
        {
            "$inc": {"daily_activity": 1, "weekly_activity": 1},
            "$set": {"last_active": int(time.time())}
        }
    )

# --- RESET LOGIC FUNCTIONS ---

def reset_daily_activity():
    """Daily leaderboard ko har raat 0 karne ke liye"""
    result = groups_collection.update_many({}, {"$set": {"daily_activity": 0}})
    print(f"✨ Daily Activity Reset: {result.modified_count} groups updated.")

def reset_weekly_activity():
    """Weekly leaderboard ko har Sunday 0 karne ke liye"""
    result = groups_collection.update_many({}, {"$set": {"weekly_activity": 0}})
    print(f"👑 Weekly Activity Reset: {result.modified_count} groups updated.")
