# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Economy Plugin - Destiny Bot (Stable Ranking & Name Sync)

import random
import time
import html
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import REGISTER_BONUS, OWNER_ID, TAX_RATE, CLAIM_BONUS, SHOP_ITEMS, MIN_CLAIM_MEMBERS
from baka.utils import ensure_user_exists, get_mention, format_money, resolve_target, stylize_text
from baka.database import users_collection, groups_collection, get_group_data, update_group_activity

# --- CONFIGURATION ---
EXP_COOLDOWN = 60  
EXP_RANGE = (1, 5) 
EXCHANGE_RATE = 10 
user_cooldowns = {} 

# --- 💎 CALLBACKS ---
async def inventory_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split("|")
    item_id = data[1]
    
    item = next((i for i in SHOP_ITEMS if i['id'] == item_id), None)
    if not item: return await query.answer("❌ Item Not Found", show_alert=True)

    text = f"💎 {stylize_text(item['name'])}\n💰 {format_money(item['price'])}\n🛡️ {stylize_text('Flex Item Status')}"
    await query.answer(text, show_alert=True)

# --- 🏦 ECONOMY COMMANDS ---

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if users_collection.find_one({"user_id": user.id}): 
        return await update.message.reply_text(f"✨ <b>{stylize_text('Ara?')}</b> {get_mention(user)}, already registered!", parse_mode=ParseMode.HTML)
    
    ensure_user_exists(user)
    users_collection.update_one({"user_id": user.id}, {"$set": {"balance": REGISTER_BONUS}})
    await update.message.reply_text(f"🎉 <b>{stylize_text('Yayy!')}</b> {get_mention(user)} Registered!\n🎁 <b>{stylize_text('Bonus')}:</b> <code>+{format_money(REGISTER_BONUS)}</code>", parse_mode=ParseMode.HTML)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Checks wallet balance with real-time name sync."""
    target_db, error = await resolve_target(update, context)
    
    if not target_db and error == "No target": 
        target_db = ensure_user_exists(update.effective_user)
    elif not target_db: 
        return await update.message.reply_text(f"❌ {error}", parse_mode=ParseMode.HTML)

    # Name Fix: Database se purana naam lene ke bajaye current name prioritize karein
    real_name = target_db.get('name', "User")
    target_mention = f"<a href='tg://user?id={target_db['user_id']}'><b>{html.escape(real_name)}</b></a>"

    bal = target_db.get('balance', 0)
    rank = users_collection.count_documents({"balance": {"$gt": bal}}) + 1
    status = "💖 Alive" if target_db.get('status', 'alive') == 'alive' else "💀 Dead"
    
    inventory = target_db.get('inventory', [])
    flex = [i for i in inventory if i.get('type') == 'flex']
    
    kb = []
    row = []
    for item in flex:
        row.append(InlineKeyboardButton(item['name'], callback_data=f"inv_view|{item['id']}"))
        if len(row) == 2:
            kb.append(row); row = []
    if row: kb.append(row)
    
    msg = (
        f"👤 {target_mention}\n"
        f"👛 <b>{format_money(bal)}</b> | 🏆 <b>#{rank}</b>\n"
        f"✨ <b>{stylize_text('EXP')}:</b> <code>{target_db.get('exp', 0)}</code>\n"
        f"❤️ <b>{status}</b>\n\n"
        f"💎 <b>{stylize_text('Flex Collection')}</b>:"
    )
    if not flex: msg += "\n<i>Empty...</i>"
    
    await update.message.reply_text(
        msg, 
        parse_mode=ParseMode.HTML, 
        reply_markup=InlineKeyboardMarkup(kb) if kb else None
    )

async def ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Global Richest Leaderboard."""
    rich = users_collection.find().sort("balance", -1).limit(10)
    def get_badge(i): return ["🥇","🥈","🥉"][i-1] if i<=3 else f"<b>{i}.</b>"
    
    msg = f"🏆 <b>{stylize_text('GLOBAL RICHEST')}</b> 🏆\n"
    msg += "━━━━━━━━━━━━━━━━━━\n"
    
    found = False
    for i, d in enumerate(rich, 1): 
        found = True
        msg += f"{get_badge(i)} {get_mention(d)} » <b>{format_money(d.get('balance',0))}</b>\n"
    
    if not found:
        msg += "<i>No billionaires found yet...</i>"
    
    msg += "━━━━━━━━━━━━━━━━━━"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

async def give(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = ensure_user_exists(update.effective_user)
    if not context.args: return await update.message.reply_text(f"⚠️ <b>{stylize_text('Usage')}:</b> <code>/give 100 @user</code>")
    
    try: 
        amount = int(next(arg for arg in context.args if arg.isdigit()))
    except: 
        return await update.message.reply_text("❌ Invalid Amount")
    
    target, error = await resolve_target(update, context)
    if not target or sender.get('balance', 0) < amount or amount <= 0: 
        return await update.message.reply_text("❌ Transaction Failed.")

    tax = int(amount * TAX_RATE)
    users_collection.update_one({"user_id": sender["user_id"]}, {"$inc": {"balance": -amount}})
    users_collection.update_one({"user_id": target["user_id"]}, {"$inc": {"balance": amount - tax}})
    users_collection.update_one({"user_id": OWNER_ID}, {"$inc": {"balance": tax}})
    
    await update.message.reply_text(
        f"💸 <b>{stylize_text('Sent')}!</b>\n"
        f"👤 <b>To:</b> {get_mention(target)}\n"
        f"💰 <b>Amount:</b> <code>{format_money(amount-tax)}</code> (Tax: {TAX_RATE*100}%)", 
        parse_mode=ParseMode.HTML
    )

async def sell_xp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args: return await update.message.reply_text("⚠️ <code>/sellxp 100</code>")
    try: amt = int(context.args[0])
    except: return
    
    user_data = users_collection.find_one({"user_id": user.id})
    if not user_data or user_data.get("exp", 0) < amt: 
        return await update.message.reply_text("❌ Low EXP!")
    
    coins = amt // EXCHANGE_RATE
    users_collection.update_one({"user_id": user.id}, {"$inc": {"exp": -amt, "balance": coins}})
    await update.message.reply_text(f"🔄 {stylize_text('Sold')} {amt} EXP for <code>{format_money(coins)}</code>", parse_mode=ParseMode.HTML)

# --- 📈 AUTO XP HANDLER ---
async def check_chat_xp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type == "private" or not update.effective_user: return
    user_id = update.effective_user.id
    current_time = time.time()
    
    update_group_activity(update.effective_chat.id, update.effective_chat.title)
    
    if user_id in user_cooldowns and (current_time - user_cooldowns[user_id] < EXP_COOLDOWN): return 
    
    xp_amount = random.randint(*EXP_RANGE)
    users_collection.update_one({"user_id": user_id}, {"$inc": {"exp": xp_amount}}, upsert=True)
    user_cooldowns[user_id] = current_time
