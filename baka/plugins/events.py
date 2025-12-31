# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Events Plugin - Group Claim System (Member Based Tiers)

import html
from datetime import datetime
from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from baka.utils import get_mention, track_group, log_to_channel, stylize_text, format_money, ensure_user_exists
from baka.database import groups_collection, users_collection
from baka.config import OWNER_ID, MIN_CLAIM_MEMBERS

# --- 🏰 GROUP CLAIM SYSTEM ---
async def claim_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Claim a one-time reward for adding the bot to a large group."""
    chat = update.effective_chat
    user = update.effective_user
    
    if chat.type == "private":
        return await update.message.reply_text("❌ This command only works in Groups!")

    # 1. Member Count Check (Eligibility)
    members_count = await chat.get_member_count()
    if members_count < MIN_CLAIM_MEMBERS:
        return await update.message.reply_text(
            f"⚠️ <b>Claim Failed!</b>\nYour group needs at least <b>{MIN_CLAIM_MEMBERS}</b> members to be eligible.",
            parse_mode='HTML'
        )

    # 2. Check if already claimed in this group
    group_data = groups_collection.find_one({"chat_id": chat.id})
    if group_data and group_data.get("reward_claimed"):
        return await update.message.reply_text("🚫 <b>One-Time Reward</b> has already been claimed in this group!", parse_mode='HTML')

    # 3. Calculate Reward Tier
    if 100 <= members_count <= 499:
        reward = 10000
    elif 500 <= members_count <= 999:
        reward = 20000
    elif members_count >= 1000:
        reward = 30000
    else:
        return await update.message.reply_text("❌ Group size does not meet criteria.")

    # 4. Process Reward & Mark DB
    ensure_user_exists(user)
    users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": reward}})
    
    groups_collection.update_one(
        {"chat_id": chat.id},
        {"$set": {
            "reward_claimed": True, 
            "claimed_by": user.id, 
            "claim_date": datetime.utcnow(),
            "active": True,
            "title": chat.title
        }},
        upsert=True
    )

    text = (f"🎉 <b>{stylize_text('GROUP REWARD CLAIMED')}!</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👥 <b>Group Size:</b> {members_count} members\n"
            f"💰 <b>Reward:</b> <code>{format_money(reward)}</code>\n"
            f"👤 <b>Claimed By:</b> {user.first_name}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Note: This is a one-time reward for this group.")
    
    await update.message.reply_text(text, parse_mode='HTML')

# --- 🛡️ BOT STATUS TRACKER ---
async def chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles bot join/leave events."""
    if not update.my_chat_member: return
    
    new_member = update.my_chat_member.new_chat_member
    old_member = update.my_chat_member.old_chat_member
    chat = update.my_chat_member.chat
    user = update.my_chat_member.from_user
    
    # Case: Bot Added
    if new_member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR]:
        if old_member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR]: return 

        groups_collection.update_one(
            {"chat_id": chat.id},
            {"$set": {"title": chat.title, "active": True}},
            upsert=True
        )
        await log_to_channel(context.bot, "join", {
            "user": f"{user.first_name} (`{user.id}`)",
            "chat": f"{chat.title} (`{chat.id}`)"
        })
    
    # Case: Bot Kicked
    elif new_member.status in [ChatMember.LEFT, ChatMember.BANNED]:
        groups_collection.update_one({"chat_id": chat.id}, {"$set": {"active": False}})

# --- 📈 ACTIVITY TRACKER ---
async def group_tracker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tracks group activity and title updates."""
    if not update.effective_chat or not update.effective_user: return
    if update.effective_chat.type == "private": return

    chat = update.effective_chat
    groups_collection.update_one(
        {"chat_id": chat.id},
        {
            "$set": {"title": chat.title, "active": True},
            "$inc": {"activity_score": 1}
        },
        upsert=True
    )
