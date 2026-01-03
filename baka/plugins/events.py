# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
import html
from datetime import datetime
from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatType
from baka.utils import get_mention, log_to_channel, format_money, ensure_user_exists
from baka.database import groups_collection, users_collection
from baka.config import MIN_CLAIM_MEMBERS

async def chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log channel mein Join/Leave reporting (Silent)."""
    if not update.my_chat_member: return
    new, old = update.my_chat_member.new_chat_member, update.my_chat_member.old_chat_member
    chat, user = update.my_chat_member.chat, update.my_chat_member.from_user
    
    # JOIN LOG
    if new.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR] and old.status not in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR]:
        groups_collection.update_one({"chat_id": chat.id}, {"$set": {"title": chat.title, "active": True}}, upsert=True)
        log_details = {"Action": "📥 Bot Joined Group", "Group": f"<b>{html.escape(chat.title)}</b>", "ID": f"<code>{chat.id}</code>", "By": f"{get_mention(user)}"}
        await log_to_channel(context.bot, "group_log", log_details)
    
    # LEAVE LOG
    elif new.status in [ChatMember.LEFT, ChatMember.BANNED, ChatMember.RESTRICTED]:
        groups_collection.update_one({"chat_id": chat.id}, {"$set": {"active": False}})
        log_details = {"Action": "📤 Bot Left Group", "Group": f"<b>{html.escape(chat.title)}</b>", "ID": f"<code>{chat.id}</code>"}
        await log_to_channel(context.bot, "group_log", log_details)

async def claim_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat, user = update.effective_chat, update.effective_user
    if chat.type == ChatType.PRIVATE: return
    
    members_count = await chat.get_member_count()
    if members_count < MIN_CLAIM_MEMBERS:
        return await update.message.reply_text(f"⚠️ Need {MIN_CLAIM_MEMBERS} members!")

    group_data = groups_collection.find_one({"chat_id": chat.id})
    if group_data and group_data.get("reward_claimed"):
        return await update.message.reply_text("🚫 Reward already claimed here!")

    reward = 10000 if members_count < 500 else 25000
    ensure_user_exists(user)
    users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": reward}})
    groups_collection.update_one({"chat_id": chat.id}, {"$set": {"reward_claimed": True}}, upsert=True)
    await update.message.reply_text(f"🎉 <b>Reward Claimed:</b> <code>{format_money(reward)}</code> 🌹", parse_mode=ParseMode.HTML)

async def group_tracker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type == ChatType.PRIVATE: return
    groups_collection.update_one({"chat_id": update.effective_chat.id}, {"$set": {"title": update.effective_chat.title, "active": True}, "$inc": {"activity_score": 1}}, upsert=True)
