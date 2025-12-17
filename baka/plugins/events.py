# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Location: Bihar | Activity Tracker Integrated

from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from baka.utils import get_mention, track_group, log_to_channel
from baka.database import groups_collection

async def chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles updates when the Bot's status changes in a chat."""
    if not update.my_chat_member: return
    
    new_member = update.my_chat_member.new_chat_member
    old_member = update.my_chat_member.old_chat_member
    chat = update.my_chat_member.chat
    user = update.my_chat_member.from_user
    
    # Initial Group Tracking
    track_group(chat, user)

    # Case 1: Bot Added or Promoted
    if new_member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR]:
        if old_member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR]: return 

        link = "No Link (Not Admin)"
        if new_member.status == ChatMember.ADMINISTRATOR:
            try: link = await context.bot.export_chat_invite_link(chat.id)
            except: pass
        
        # Database mein group initialize karna agar naya hai
        groups_collection.update_one(
            {"chat_id": chat.id},
            {"$set": {"title": chat.title, "active": True}, "$setOnInsert": {"treasury": 0, "daily_activity": 0, "weekly_activity": 0}},
            upsert=True
        )

        await log_to_channel(context.bot, "join", {
            "user": f"{get_mention(user)} (`{user.id}`)",
            "chat": f"{chat.title} (`{chat.id}`)",
            "link": link,
            "action": "Bot added to a group"
        })
    
    # Case 2: Bot Removed or Banned
    elif new_member.status in [ChatMember.LEFT, ChatMember.BANNED]:
        groups_collection.update_one({"chat_id": chat.id}, {"$set": {"active": False}})
        await log_to_channel(context.bot, "leave", {
            "user": f"{get_mention(user)} (`{user.id}`)",
            "chat": f"{chat.title} (`{chat.id}`)",
            "action": "Bot was kicked or left"
        })

# --- GROUP ACTIVITY TRACKER (FOR TOPGROUPS) ---
async def group_tracker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tracks every message to increase group activity points."""
    if not update.effective_chat or not update.effective_user: return
    if update.effective_chat.type == "private": return

    chat = update.effective_chat
    
    # 1. Basic Tracking (Utils wala)
    track_group(chat, update.effective_user)

    # 2. Activity Points Logic (Jo /topgroups ko data dega)
    # Har message par 1 activity point badhega
    groups_collection.update_one(
        {"chat_id": chat.id},
        {
            "$set": {"title": chat.title},
            "$inc": {
                "daily_activity": 1,
                "weekly_activity": 1,
                "treasury": 10 # Har message par treasury mein $10 add honge
            }
        },
        upsert=True
    )
