# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Events Plugin - Fixed Claim Logic + Nezuko Style Monospace

import html
from datetime import datetime
from telegram import Update, ChatMember
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatType
from baka.utils import get_mention, log_to_channel, format_money, ensure_user_exists
from baka.database import groups_collection, users_collection
from baka.config import MIN_CLAIM_MEMBERS

# --- 🎨 NEZUKO FONT CONVERTER ---
def nezuko_style(text):
    """Converts normal text to Small Caps and wraps in Monospace."""
    lowered = text.lower()
    mapping = str.maketrans(
        "abcdefghijklmnopqrstuvwxyz",
        "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    )
    small_caps = lowered.translate(mapping)
    return f"<code>{small_caps}</code>"

# --- ⚙️ ECONOMY TOGGLE COMMANDS ---

async def open_economy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat, user = update.effective_chat, update.effective_user
    if chat.type == ChatType.PRIVATE:
        return await update.message.reply_text(nezuko_style("❌ ᴜsᴇ ɪɴ ɢʀᴏᴜᴘs ᴏɴʟʏ."))

    member = await chat.get_member(user.id)
    if member.status not in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
        return await update.message.reply_text(nezuko_style("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs."))

    groups_collection.update_one({"chat_id": chat.id}, {"$set": {"economy_enabled": True}}, upsert=True)
    await update.message.reply_text(nezuko_style("✅ ᴇᴄᴏɴᴏᴍʏ ᴄᴏᴍᴍᴀɴᴅs ᴇɴᴀʙʟᴇᴅ."))

async def close_economy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat, user = update.effective_chat, update.effective_user
    if chat.type == ChatType.PRIVATE:
        return await update.message.reply_text(nezuko_style(":) ᴜsᴇ ɪɴ ɢʀᴏᴜᴘs ᴏɴʟʏ."))

    member = await chat.get_member(user.id)
    if member.status not in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
        return await update.message.reply_text(nezuko_style("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs."))

    groups_collection.update_one({"chat_id": chat.id}, {"$set": {"economy_enabled": False}}, upsert=True)
    await update.message.reply_text(nezuko_style("✅ ᴇᴄᴏɴᴏᴍʏ ᴄᴏᴍᴍᴀɴᴅs ᴅɪsᴀʙʟᴇᴅ."))

# --- 📥 CLAIM GROUP (FIXED LOGIC) ---

async def claim_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allows group owners to claim a one-time reward for the bot joining."""
    chat, user = update.effective_chat, update.effective_user
    if chat.type == ChatType.PRIVATE: 
        return await update.message.reply_text(nezuko_style("❌ ᴄʟᴀɪᴍ ɪɴ ɢʀᴏᴜᴘs ᴏɴʟʏ."))
    
    # Member count logic fix
    members_count = await context.bot.get_chat_member_count(chat.id)
    if members_count < MIN_CLAIM_MEMBERS:
        return await update.message.reply_text(nezuko_style(f"⚠️ ɴᴇᴇᴅ {MIN_CLAIM_MEMBERS} ᴍᴇᴍʙᴇʀs ᴛᴏ ᴄʟᴀɪᴍ!"))

    group_data = groups_collection.find_one({"chat_id": chat.id})
    if group_data and group_data.get("reward_claimed"):
        return await update.message.reply_text(nezuko_style("🚫 ʀᴇᴡᴀʀᴅ ᴀʟʀᴇᴀᴅʏ ᴄʟᴀɪᴍᴇᴅ ʜᴇʀᴇ!"))

    # Admin check for the person claiming
    member = await chat.get_member(user.id)
    if member.status not in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
        return await update.message.reply_text(nezuko_style("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴄʟᴀɪᴍ ᴛʜɪs."))

    reward = 10000 if members_count < 500 else 25000
    ensure_user_exists(user)
    
    # Update Database
    users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": reward}})
    groups_collection.update_one({"chat_id": chat.id}, {"$set": {"reward_claimed": True}}, upsert=True)
    
    await update.message.reply_text(
        nezuko_style(f"🎉 ʀᴇᴡᴀʀᴅ ᴄʟᴀɪᴍᴇᴅ: {format_money(reward)} 🌹"), 
        parse_mode=ParseMode.HTML
    )

# --- 📊 TRACKERS ---

async def group_tracker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type == ChatType.PRIVATE: return
    groups_collection.update_one(
        {"chat_id": update.effective_chat.id}, 
        {"$set": {"title": update.effective_chat.title, "active": True}, "$inc": {"activity_score": 1}}, 
        upsert=True
    )

async def chat_member_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.my_chat_member: return
    new, old = update.my_chat_member.new_chat_member, update.my_chat_member.old_chat_member
    chat, user = update.my_chat_member.chat, update.my_chat_member.from_user
    
    if new.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR] and old.status not in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR]:
        groups_collection.update_one({"chat_id": chat.id}, {"$set": {"title": chat.title, "active": True}}, upsert=True)
    elif new.status in [ChatMember.LEFT, ChatMember.BANNED]:
        groups_collection.update_one({"chat_id": chat.id}, {"$set": {"active": False}})
