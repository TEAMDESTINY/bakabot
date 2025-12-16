# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
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
    msg = f"📈 <b>{stylize_text('STOCK MARKET')}</b>\n\n🏢 <b>Group:</b> <code>{chat.title}</code>\n💎 <b>Price:</b> <code>{format_money(price)}</code>\n📊 <b>Status:</b> {'🔥 High' if active_users > 10 else '💤 Low'}"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# 2. TERRITORY RAID (Group vs Group War)
async def territory_raid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args: return await update.message.reply_text("⚠️ <b>Usage:</b> <code>/raid @GroupUsername</code>")
    target_handle = context.args[0].replace("@", "")
    if random.randint(1, 100) > 70:
        loot = random.randint(5000, 15000)
        users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": loot}})
        await update.message.reply_text(f"⚔️ <b>RAID SUCCESS!</b>\n{get_mention(user)} ne <b>{target_handle}</b> se <code>{format_money(loot)}</code> loot liye!")
    else: await update.message.reply_text("💀 <b>RAID FAILED!</b> Aapki army haar gayi.")

# 3. AI GOVERNOR (Smart Feedback)
async def ai_governor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = f"Act as a strict Economic Governor of group '{update.effective_chat.title}'. Give a funny 2-line report."
    report = await ask_mistral_raw("Governor", prompt)
    await update.message.reply_text(f"🏛️ <b>{stylize_text('GOVERNOR REPORT')}</b>\n\n{report}", parse_mode=ParseMode.HTML)

# 4. BOUNTY (Bounty Hunter)
async def bounty_hunter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎯 <b>Bounty Set!</b>\nJo bhi target ko RPG mein harayega use inaam milega!")

# 5. PASSIVE MINING (Multiplier)
async def passive_mining(update: Update, context: ContextTypes.DEFAULT_TYPE):
    active_users = users_collection.count_documents({"last_chat_id": update.effective_chat.id})
    multiplier = 1.0 + (active_users * 0.1)
    await update.message.reply_text(f"⛏️ <b>MINING SPEED:</b> <code>{multiplier:.1f}x</code>\nActive log: {active_users}")
