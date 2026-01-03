# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Version - Group Logs & Simple Font

import random
import html
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatType
from baka.database import groups_collection
from baka.utils import get_mention, ensure_user_exists, log_to_channel
from baka.config import WELCOME_IMG_URL, SUPPORT_GROUP

async def welcome_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enable/Disable Welcomes."""
    chat = update.effective_chat
    user = update.effective_user
    args = context.args
    
    if chat.type == ChatType.PRIVATE:
        return await update.message.reply_text("🍼 <b>This command works in groups only baby!</b>", parse_mode=ParseMode.HTML)
    
    member = await chat.get_member(user.id)
    if member.status not in ['administrator', 'creator']:
        return await update.message.reply_text("❌ <b>Admin only!</b>", parse_mode=ParseMode.HTML)

    if not args:
        return await update.message.reply_text("⚠️ <b>Usage:</b> <code>/welcome on</code> or <code>off</code>", parse_mode=ParseMode.HTML)
    
    state = args[0].lower()
    if state in ['on', 'enable', 'yes']:
        groups_collection.update_one({"chat_id": chat.id}, {"$set": {"welcome_enabled": True}}, upsert=True)
        await update.message.reply_text("✅ <b>Welcome Messages Enabled!</b>", parse_mode=ParseMode.HTML)
    elif state in ['off', 'disable', 'no']:
        groups_collection.update_one({"chat_id": chat.id}, {"$set": {"welcome_enabled": False}}, upsert=True)
        await update.message.reply_text("❌ <b>Welcome Messages Disabled!</b>", parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text("⚠️ Invalid option. Use <code>on</code> or <code>off</code>.", parse_mode=ParseMode.HTML)

async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles new members joining and Bot being added to groups."""
    chat = update.effective_chat
    if not update.message or not update.message.new_chat_members:
        return

    for member in update.message.new_chat_members:
        # --- 🤖 BOT ADDED TO GROUP (Join Log) ---
        if member.id == context.bot.id:
            adder = update.message.from_user
            ensure_user_exists(adder)
            
            groups_collection.update_one(
                {"chat_id": chat.id}, 
                {"$set": {"welcome_enabled": True, "title": chat.title}}, 
                upsert=True
            )
            
            # 📢 SEND LOG TO CHANNEL
            log_details = {
                "Action": "📥 Bot Joined Group",
                "Group Name": f"<b>{html.escape(chat.title)}</b>",
                "Group ID": f"<code>{chat.id}</code>",
                "Added By": f"{get_mention(adder)} (<code>{adder.id}</code>)"
            }
            await log_to_channel(context.bot, "group_log", log_details)

            txt = (
                f"🌹 <b>Welcome {get_mention(adder)}!</b>\n\n"
                f"Thanks for adding me to <b>{html.escape(chat.title)}</b>! ✨\n\n"
                f"🎁 <b>First Time Bonus:</b>\n"
                f"Type <code>/claim</code> fast to get 2,000 Coins!"
            )
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("💬 Support", url=SUPPORT_GROUP)]])
            try: await update.message.reply_photo(WELCOME_IMG_URL, caption=txt, parse_mode=ParseMode.HTML, reply_markup=kb)
            except: await update.message.reply_text(txt, parse_mode=ParseMode.HTML, reply_markup=kb)

        # --- 👤 NORMAL USER JOINED ---
        else:
            ensure_user_exists(member)
            group_data = groups_collection.find_one({"chat_id": chat.id})
            
            if group_data and group_data.get("welcome_enabled"):
                # Simple Welcome message as requested
                welcome_text = f"Welcome {get_mention(member)} 🌹"
                
                try: 
                    await update.message.reply_photo(
                        photo=WELCOME_IMG_URL, 
                        caption=welcome_text, 
                        parse_mode=ParseMode.HTML
                    )
                except: 
                    await update.message.reply_text(welcome_text, parse_mode=ParseMode.HTML)

async def left_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles Bot being removed from groups (Leave Log)."""
    if not update.message or not update.message.left_chat_member:
        return
        
    left_user = update.message.left_chat_member
    chat = update.effective_chat

    # Agar bot ko nikala gaya
    if left_user.id == context.bot.id:
        log_details = {
            "Action": "📤 Bot Left/Removed",
            "Group Name": f"<b>{html.escape(chat.title)}</b>",
            "Group ID": f"<code>{chat.id}</code>"
        }
        await log_to_channel(context.bot, "group_log", log_details)
