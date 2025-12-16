# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Group Economy Plugin

import random
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.utils import get_mention, format_money, stylize_text
from baka.database import users_collection, groups_collection
from baka.plugins.chatbot import ask_mistral_raw

# 1. STOCK MARKET (Group Activity Value)
async def stock_market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == "private": return await update.message.reply_text("❌ Groups mein use karein!")
    
    active_users = users_collection.count_documents({"last_chat_id": chat.id})
    price = 10.0 + (active_users * 1.5)
    
    msg = (
        f"📈 <b>{stylize_text('STOCK MARKET')}</b>\n\n"
        f"🏢 <b>Group:</b> <code>{chat.title}</code>\n"
        f"💎 <b>Share Price:</b> <code>{format_money(price)}</code>\n"
        f"📊 <b>Status:</b> {'🔥 Bullish' if active_users > 10 else '💤 Stable'}\n\n"
        f"<i>Tip: Group mein chatting badhao, price apne aap badhega!</i>"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# 2. TERRITORY RAID (Group vs Group War)
async def territory_raid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    if chat.type == "private": return
    
    if not context.args:
        return await update.message.reply_text("⚠️ <b>Usage:</b> <code>/raid @GroupUsername</code>")

    target_handle = context.args[0].replace("@", "")
    
    if random.randint(1, 100) > 70: # 30% Chance
        loot = random.randint(5000, 15000)
        users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": loot}})
        await update.message.reply_text(f"⚔️ <b>RAID SUCCESS!</b>\n\n{get_mention(user)} ne <b>{target_handle}</b> ki treasury se <code>{format_money(loot)}</code> loot liye!")
    else:
        await update.message.reply_text("💀 <b>RAID FAILED!</b>\nAapki army haar gayi aur lootera pakda gaya.")

# 3. AI GOVERNOR (Smart Feedback)
async def ai_governor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == "private": return
    
    prompt = f"Act as a strict but funny Economic Governor of group '{chat.title}'. Give a 2-line witty report on their wealth."
    report = await ask_mistral_raw("Governor", prompt)
    
    await update.message.reply_text(f"🏛️ <b>{stylize_text('GOVERNOR REPORT')}</b>\n\n<i>{report}</i>", parse_mode=ParseMode.HTML)

# 4. BOUNTY HUNTER (Global Hitman)
async def bounty_hunter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("🎯 <b>Usage:</b> <code>/bounty 10000 @user</code>")
    
    await update.message.reply_text("🎯 <b>Bounty System Active!</b>\nTarget par inaam lag gaya hai. RPG battle mein harane wale ko inaam milega!")

# 5. PASSIVE MINING (Group Multiplier)
async def passive_mining(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    active_users = users_collection.count_documents({"last_chat_id": chat.id})
    multiplier = 1.0 + (active_users * 0.1)
    
    msg = (
        f"⛏️ <b>{stylize_text('PASSIVE MINING')}</b>\n\n"
        f"⚡ <b>Mining Speed:</b> <code>{multiplier:.1f}x</code>\n"
        f"👥 <b>Active Miners:</b> <code>{active_users}</code>\n\n"
        f"<i>Tip: Jitne zyada log active honge, sabki kamayi utni tezi se badhegi!</i>"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
