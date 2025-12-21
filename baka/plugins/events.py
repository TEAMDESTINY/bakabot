# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Events Plugin - Tracker | Claim System | Dual Owner Support

import html
from datetime import datetime
from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from baka.utils import get_mention, track_group, log_to_channel, stylize_text
from baka.database import groups_collection
from baka.config import OWNER_ID

# --- 🏰 GROUP CLAIM SYSTEM ---
async def claim_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allows a user or Super Owner to claim group ownership and earnings."""
    chat = update.effective_chat
    user = update.effective_user
    
    if chat.type == "private":
        return await update.message.reply_text("❌ Ye command sirf groups mein kaam karti hai!")

    # Database se check karna
    group_data = groups_collection.find_one({"chat_id": chat.id})
    
    # Check if already claimed
    if group_data and group_data.get("claimed"):
        current_owner = group_data.get("owner_id")
        
        # Super Owner (Aap) Bypass: Aap kisi se bhi group cheen sakte hain
        if user.id == OWNER_ID:
            pass # Force claim allowed
        else:
            return await update.message.reply_text(
                f"🏰 <b>{stylize_text('ALREADY CLAIMED')}</b>\n"
                f"Ye group pehle se claimed hai by ID: <code>{current_owner}</code>",
                parse_mode='HTML'
            )

    # Claim Logic
    groups_collection.update_one(
        {"chat_id": chat.id},
        {"$set": {
            "claimed": True, 
            "owner_id": user.id, 
            "owner_name": user.first_name,
            "claim_date": datetime.utcnow(),
            "active": True
        }},
        upsert=True
    )

    text = (f"🏰 <b>{stylize_text('GROUP CLAIMED')}!</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"👑 <b>New Owner:</b> {get_mention(user)}\n"
            f"💰 <b>Status:</b> Ab is group ki <b>Treasury</b> aur <b>Tax</b> aapko milenge!\n"
            f"━━━━━━━━━━━━━━━━━━")
    
    await update.message.reply_text(text, parse_mode='HTML')

# --- 🛡️ BOT STATUS TRACKER ---
async def chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot join/leave events handle karta hai."""
    if not update.my_chat_member: return
    
    new_member = update.my_chat_member.new_chat_member
    old_member = update.my_chat_member.old_chat_member
    chat = update.my_chat_member.chat
    user = update.my_chat_member.from_user
    
    track_group(chat, user)

    # Case: Bot Added
    if new_member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR]:
        if old_member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR]: return 

        link = "No Link"
        if new_member.status == ChatMember.ADMINISTRATOR:
            try: link = await context.bot.export_chat_invite_link(chat.id)
            except: pass
        
        groups_collection.update_one(
            {"chat_id": chat.id},
            {"$set": {"title": chat.title, "active": True}, 
             "$setOnInsert": {"claimed": False, "treasury": 0, "daily_activity": 0}},
            upsert=True
        )

        await log_to_channel(context.bot, "join", {
            "user": f"{get_mention(user)} (`{user.id}`)",
            "chat": f"{chat.title} (`{chat.id}`)",
            "link": link
        })
    
    # Case: Bot Kicked
    elif new_member.status in [ChatMember.LEFT, ChatMember.BANNED]:
        groups_collection.update_one({"chat_id": chat.id}, {"$set": {"active": False}})
        await log_to_channel(context.bot, "leave", {
            "chat": f"{chat.title} (`{chat.id}`)",
            "action": "Bot removed from chat"
        })

# --- 📈 ACTIVITY TRACKER ---
async def group_tracker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Har message par group ki activity aur treasury badhata hai."""
    if not update.effective_chat or not update.effective_user: return
    if update.effective_chat.type == "private": return

    chat = update.effective_chat
    groups_collection.update_one(
        {"chat_id": chat.id},
        {
            "$set": {"title": chat.title, "active": True},
            "$inc": {
                "daily_activity": 1,
                "weekly_activity": 1,
                "treasury": 10 # Har msg par group bank mein $10 deposit
            }
        },
        upsert=True
    )
