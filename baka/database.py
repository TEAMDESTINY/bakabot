from pymongo import MongoClient
import certifi
from baka.config import MONGO_URI

# Initialize Connection
RyanBaka = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = RyanBaka["bakabot_db"]

# --- DEFINING COLLECTIONS ---
users_collection = db["users"]       
groups_collection = db["groups"]     # Isme ab treasury aur multiplier bhi save hoga
sudoers_collection = db["sudoers"]   
chatbot_collection = db["chatbot"]   
riddles_collection = db["riddles"]

def get_group_data(chat_id, title=None):
    """Group ki economy details fetch ya create karne ke liye"""
    group = groups_collection.find_one({"chat_id": chat_id})
    if not group:
        group = {
            "chat_id": chat_id,
            "title": title or "Unknown Group",
            "treasury": 10000,  # New groups get starting bonus
            "claimed": False,
            "shares": 10.0,     # Initial stock price
            "last_active": 0
        }
        groups_collection.insert_one(group)
    return group
