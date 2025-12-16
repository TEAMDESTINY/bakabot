# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Group Economy Plugin - BOLD Names & Fixed Logic

import random
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.utils import get_mention, format_money, stylize_text
from baka.database import users_collection, groups_collection
from baka.plugins.chatbot import ask_mistral_raw

# --- 1. STOCK MARKET ---
async def stock_market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == "private": return await update.message.reply_text("❌ Groups mein use karein!")
    
    active_users = users_collection.count_documents({"last_chat_id": chat.id})
    price = 10.0 + (active_users * 1.5)
    
    msg = (
        f"📈 <b>{stylize_text('STOCK MARKET')}</b>\n\n"
        f"🏢 <b>Group:</b> <b>{chat.title}</b>\n" # Name BOLD
        f"💎 <b>Share Price:</b> <code>{format_money(price)}</code>\n"
        f"📊 <b>Status:</b> {'🔥 Bullish' if active_users > 10 else '💤 Stable'}\n\n"
        f"<i>Tip: Group mein chatting badhao, price badhega!</i>"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 2. TERRITORY RAID ---
async def territory_raid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args: 
        return await update.message.reply_text("⚠️ <b>Usage:</b> <code>/raid @GroupUsername</code>")
    
    target_handle = context.args[0].replace("@", "")
    if random.randint(1, 100) > 70:
        loot = random.randint(5000, 15000)
        users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": loot}})
        await update.message.reply_text(f"⚔️ <b>RAID SUCCESS!</b>\n\n{get_mention(user)} ne <b>{target_handle}</b> se <code>{format_money(loot)}</code> loot liye!")
    else:
        await update.message.reply_text("💀 <b>RAID FAILED!</b> Aapki army haar gayi.")

# --- 3. AI GOVERNOR ---
async def ai_governor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private": return
    prompt = f"Act as a strict but funny Economic Governor of group '{update.effective_chat.title}'. Give a 2-line report."
    report = await ask_mistral_raw("Governor", prompt)
    await update.message.reply_text(f"🏛️ <b>{stylize_text('GOVERNOR REPORT')}</b>\n\n<i>{report}</i>", parse_mode=ParseMode.HTML)

# --- 4. TOP GROUPS (TODAY/WEEKLY/OVERALL) ---
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
        
        # FIX: Agar title nahi hai toh chat_id dikhao, aur name BOLD karo
        group_name = g.get('title') or f"Group {g.get('chat_id')}"
        
        if mode == "overall":
            val_display = f"💰 Treasury: <code>{format_money(g.get('treasury', 0))}</code>"
        else:
            val_display = f"⚡ Activity: <code>{g.get(sort_field, 0)} pts</code>"
            
        msg += f"{badge} <b>{group_name}</b>\n╰ {val_display}\n"

    if count == 0: 
        msg += "<i>No data available yet...</i>"

    keyboard = [[
        InlineKeyboardButton("📅 Today", callback_data="topg_today"),
        InlineKeyboardButton("🗓️ Weekly", callback_data="topg_weekly"),
        InlineKeyboardButton("🌍 Overall", callback_data="topg_overall")
    ]]
    
    if query:
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)

# --- 5. PASSIVE MINING ---
async def passive_mining(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == "private": return
    active_users = users_collection.count_documents({"last_chat_id": chat.id})
    multiplier = 1.0 + (active_users * 0.1)
    msg = (
        f"⛏️ <b>{stylize_text('PASSIVE MINING')}</b>\n\n"
        f"⚡ <b>Speed:</b> <code>{multiplier:.1f}x</code>\n"
        f"👥 <b>Miners:</b> <code>{active_users}</code>\n\n"
        f"<i>Tip: Zyada active log = tezi se kamayi!</i>"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 6. BOUNTY HUNTER ---
async def bounty_hunter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎯 <b>Bounty System Active!</b>\nTarget ko RPG battle mein harao aur inaam lo!")
