from telegram.ext import MessageHandler, filters
from datetime import datetime
from baka.database import db

users = db.users  # Mongo collection

async def give_exp(update, context):
    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        return

    user_id = update.effective_user.id
    user = users.find_one({"user_id": user_id})

    if not user:
        users.insert_one({
            "user_id": user_id,
            "exp": 0,
            "coins": 0,
            "last_msg": 0
        })
        user = users.find_one({"user_id": user_id})

    now = int(datetime.now().timestamp())

    # 5 sec spam protection
    if now - user.get("last_msg", 0) < 5:
        return

    users.update_one(
        {"user_id": user_id},
        {"$inc": {"exp": 2}, "$set": {"last_msg": now}}
    )

def exp_system_handler(app):
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), give_exp))
