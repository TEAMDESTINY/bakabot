# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Group Economy Plugin - Fixed & Optimized

import random
import time
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.utils import format_money, stylize_text, get_mention
from baka.database import users_collection, groups_collection

# --- 1. STOCK MARKET ---
async def stock_market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == "private": 
        return await update.message.reply_text(f"❌ {stylize_text('Groups mein use karein!')}")
    
    # Counting users who have been active in this specific group
    active_users = users_collection.count_documents({"seen_groups": chat.id})
    price = 10.0 + (active_users * 1.5)
    
    msg = (
        f"📈 <b>{stylize_text('STOCK MARKET')}</b>\n\n"
        f"🏢 <b>{stylize_text('Group')}:</b> <b>{chat.title}</b>\n"
        f"💎 <b>{stylize_text('Share Price')}:</b> <code>{format_money(int(price))}</code>\n"
        f"📊 <b>{stylize_text('Status')}:</b> {'🔥 Bullish' if active_users > 5 else '💤 Stable'}\n\n"
        f"<i>{stylize_text('Tip: Chatting badhao, price badhega!')}</i>"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 2. TERRITORY RAID ---
async def territory_raid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    if chat.type == "private": return
    
    if not context.args: 
        return await update.message.reply_text(f"⚠️ {stylize_text('Usage')}: <code>/raid @GroupUsername</code>", parse_mode=ParseMode.HTML)
    
    target_handle = context.args[0].replace("@", "")
    
    # Success Rate check
    if random.randint(1, 100) > 75:
        loot = random.randint(5000, 15000)
        users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": loot}})
        
        await update.message.reply_text(
            f"⚔️ <b>{stylize_text('RAID SUCCESS')}!</b>\n\n"
            f"{get_mention(user)} {stylize_text('ne')} <b>@{target_handle}</b> {stylize_text('se')} <code>{format_money(loot)}</code> {stylize_text('loot liye!')}",
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text(f"💀 <b>{stylize_text('RAID FAILED')}!</b>\n{stylize_text('Aapki army haar gayi.')}", parse_mode=ParseMode.HTML)

# --- 3. AI GOVERNOR (Simplified for Stability) ---
async def ai_governor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private": return
    
    # Using a funny static report if AI is slow or not linked
    reports = [
        "Economy is booming! Everyone is rich but nobody is paying taxes.",
        "The treasury is full, but I spent half of it on anime figurines.",
        "Taxes are up 200%. Why? Because I said so!",
        "Our wealth is immense. We are practically a floating empire."
    ]
    report = random.choice(reports)
    
    await update.message.reply_text(
        f"🏛️ <b>{stylize_text('GOVERNOR REPORT')}</b>\n\n"
        f"🏢 <b>{update.effective_chat.title}</b>\n"
        f"📝 <i>{report}</i>", 
        parse_mode=ParseMode.HTML
    )

# --- 4. TOP GROUPS ---
async def top_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    mode = "overall"
    
    if query:
        await query.answer()
        mode = query.data.split("_")[1]

    if mode == "today":
        title_text = "TODAY'S HOTTEST"
        top_g = groups_collection.find().sort("daily_activity", -1).limit(10)
        sort_field = "daily_activity"
    elif mode == "weekly":
        title_text = "WEEKLY KINGS"
        top_g = groups_collection.find().sort("weekly_activity", -1).limit(10)
        sort_field = "weekly_activity"
    else:
        title_text = "ALL-TIME EMPIRES"
        top_g = groups_collection.find().sort("treasury", -1).limit(10)
        sort_field = "treasury"

    msg = f"🏆 <b>{stylize_text(title_text)}</b> 🏆\n\n"
    count = 0
    for i, g in enumerate(top_g, 1):
        count += 1
        badge = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"<code>{i}.</code>"
        group_name = g.get('title') or f"Group {g.get('chat_id')}"
        
        if mode == "overall":
            val = f"💰 {format_money(g.get('treasury', 0))}"
        else:
            val = f"⚡ {g.get(sort_field, 0)} activity pts"
            
        msg += f"{badge} <b>{group_name}</b>\n╰ {val}\n"

    if count == 0: msg += f"<i>{stylize_text('No data available yet...')}</i>"

    kb = [[
        InlineKeyboardButton("📅 Today", callback_data="topg_today"),
        InlineKeyboardButton("🗓️ Weekly", callback_data="topg_weekly"),
        InlineKeyboardButton("🌍 Overall", callback_data="topg_overall")
    ]]
    
    markup = InlineKeyboardMarkup(kb)
    if query:
        await query.edit_message_text(msg, reply_markup=markup, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(msg, reply_markup=markup, parse_mode=ParseMode.HTML)

# --- 5. PASSIVE MINING ---
async def passive_mining(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    if chat.type == "private": return
    
    user_db = users_collection.find_one({"user_id": user.id})
    last_mine = user_db.get('last_mine_time')
    
    # Cooldown Check (1 Hour)
    if last_mine:
        cooldown = timedelta(hours=1)
        if datetime.utcnow() - last_mine < cooldown:
            rem = cooldown - (datetime.utcnow() - last_mine)
            mins = int(rem.total_seconds() / 60)
            return await update.message.reply_text(f"⏳ {stylize_text('Cooldown')}: {mins} {stylize_text('mins left')}.")

    # Multiplier based on group active users
    active_count = users_collection.count_documents({"seen_groups": chat.id})
    multiplier = 1.0 + (active_count * 0.1)
    reward = int(1500 * multiplier)
    
    users_collection.update_one(
        {"user_id": user.id}, 
        {"$inc": {"balance": reward}, "$set": {"last_mine_time": datetime.utcnow()}}
    )

    await update.message.reply_text(
        f"⛏️ <b>{stylize_text('PASSIVE MINING')}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💰 {stylize_text('Earned')}: <code>{format_money(reward)}</code>\n"
        f"👥 {stylize_text('Bonus Speed')}: <code>{multiplier:.1f}x</code>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 {get_mention(user)} {stylize_text('ne mining khatam ki!')}",
        parse_mode=ParseMode.HTML
    )
