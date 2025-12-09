# Copyright (c) 2025 
# Telegram: @WTF_Phantom <DevixOP>
# Location: Supaul, Bihar
#
# All Rights Reserved.
#
# This code is the intellectual property of @WTF_Phantom.
# You are not allowed to copy, modify, redistribute, or use this
# code for commercial or personal projects without explicit permission.
# Contact:
# Email: king25258069@gmail.com

from pymongo import MongoClient
import certifi
from baka.config import MONGO_URI

# ------------------ DATABASE CONNECTION ------------------

RyanBaka = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = RyanBaka["bakabot_db"]

# ------------------ COLLECTIONS ------------------

users_collection = db["users"]         # Stores user data: xp, level, balance, waifus, inventory etc.
groups_collection = db["groups"]       # Group settings
sudoers_collection = db["sudoers"]     # Admin IDs
chatbot_collection = db["chatbot"]     # Chat history
riddles_collection = db["riddles"]     # Active riddles



# ============================================================
#                    XP SYSTEM HELPERS
# ============================================================

def get_user(user_id: int):
    """
    Fetch user from database.
    Create new entry if user doesn't exist.
    """
    user = users_collection.find_one({"_id": user_id})

    if user is None:
        user = {
            "_id": user_id,
            "xp": 0,
            "level": 1,
        }
        users_collection.insert_one(user)

    return user



def update_user(user_id: int, xp: int, level: int):
    """
    Update XP and level for user.
    """
    users_collection.update_one(
        {"_id": user_id},
        {"$set": {"xp": xp, "level": level}}
    )



def add_xp(user_id: int, amount: int = 10):
    """
    Add XP to user and auto-check level up.
    Returns: (leveled_up (bool), new_level, remaining_xp)
    """
    user = get_user(user_id)

    xp = user["xp"] + amount
    level = user["level"]

    next_level_xp = level * 150

    leveled_up = False
    if xp >= next_level_xp:
        xp -= next_level_xp
        level += 1
        leveled_up = True

    update_user(user_id, xp, level)

    return leveled_up, level, xp
