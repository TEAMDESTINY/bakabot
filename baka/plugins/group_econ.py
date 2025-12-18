# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Group Economy Plugin - Mentions Fixed & Serif Font

import random
import time
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.utils import format_money, stylize_text
from baka.database import users_collection, groups_collection
from baka.plugins.chatbot import ask_mistral_raw

# --- 1. STOCK MARKET ---
async def stock_market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == "private": return await update.message.reply_text(f"❌ {stylize_text('Groups mein use karein!')}")
    
    active_users = users_collection.count_documents({"last_chat_id": chat.id})
    price = 10.0 + (active_users * 1.5)
    
    msg = (
        f"📈 <b>{stylize_text('STOCK MARKET')}</b>\n\n"
        f"🏢 <b>{stylize_text('Group')}:</b> <b>{chat.title}</b>\n"
        f"💎 <b>{stylize_text('Share Price')}:</b> <code>{format_money(price)}</code>\n"
        f"📊 <b>{stylize_text('Status')}:</b> {'🔥 Bullish' if active_users > 10 else '💤 Stable'}\n\n"
        f"<i>{stylize_text('Tip: Chatting badhao, price badhega!')}</i>"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- 2. TERRITORY RAID ---
async def territory_raid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    if chat.type == "private": return
    
    if not context.args: 
        return await update.message.reply_text(f"⚠️ {stylize_text('Usage')}: <code>/raid @GroupUsername</code>")
    
    target_handle = context.args[0].replace("@", "")
    
    # Simple Clickable Name without showing UserID text
    user_mention = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
    
    # 30% Success Rate
    if random.randint(1, 100) > 70:
        loot = random.randint(5000, 15000)
        users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": loot}})
        
        await update.message.reply_text(
            f"⚔️ <b>{stylize_text('RAID SUCCESS')}!</b>\n\n"
            f"{user_mention} {stylize_text('𝒏𝒆')} <b>{target_handle}</b> {stylize_text('𝒔𝒆')} <code>{format_money(loot)}</code> {stylize_text('𝒍𝒐𝒐𝒕 𝒍𝒊𝒚𝒆!')}",
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text(f"💀 <b>{stylize_text('RAID FAILED')}!</b> {stylize_text('Aapki army haar gayi.')}", parse_mode=ParseMode.HTML)

# --- 3. AI GOVERNOR ---
async def ai_governor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private": return
    prompt = f"Act as a strict but funny Economic Governor of group '{update.effective_chat.title}'. Give a 2-line report on taxes and wealth."
    report = await ask_mistral_raw("Governor", prompt)
    await update.message.reply_text(f"🏛️ <b>{stylize_text('GOVERNOR REPORT')}</b>\n\n<i>{report}</i>", parse_mode=ParseMode.HTML)

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
        val = f"💰 {format_money(g.get('treasury', 0))}" if mode == "overall" else f"⚡ {g.get(sort_field, 0)} pts"
        msg += f"{badge} <b>{group_name}</b>\n╰ {val}\n"

    if count == 0: msg += f"<i>{stylize_text('No data available yet...')}</i>"

    kb = [[
        InlineKeyboardButton(f"📅 Today", callback_data="topg_today"),
        InlineKeyboardButton(f"🗓️ Weekly", callback_data="topg_weekly"),
        InlineKeyboardButton(f"🌍 Overall", callback_data="topg_overall")
    ]]
    
    if query:
        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

# --- 5. PASSIVE MINING ---
async def passive_mining(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    if chat.type == "private": return
    
    last_mine = context.user_data.get('last_mine', 0)
    if time.time() - last_mine < 3600:
        rem = int((3600 - (time.time() - last_mine)) / 60)
        return await update.message.reply_text(f"⏳ {stylize_text('Cooldown')}: {rem} mins.")

    active_users = users_collection.count_documents({"last_chat_id": chat.id})
    multiplier = 1.0 + (active_users * 0.1)
    reward = int(2000 * multiplier)
    
    users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": reward}})
    context.user_data['last_mine'] = time.time()

    await update.message.reply_text(
        f"⛏️ <b>{stylize_text('PASSIVE MINING')}</b>\n\n"
        f"💰 {stylize_text('Earned')}: <code>{format_money(reward)}</code>\n"
        f"👥 {stylize_text('Miners Speed')}: <code>{multiplier:.1f}x</code>",
        parse_mode=ParseMode.HTML
    )
