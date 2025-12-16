# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Economy Plugin - Destiny Bot (Fixed Group Names & Activity)

import random
import time
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

# --- INVENTORY CALLBACK ---
async def inventory_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split("|")
    item_id = data[1]
    
    item = next((i for i in SHOP_ITEMS if i['id'] == item_id), None)
    if not item: return await query.answer("❌ Error: Item Not Found", show_alert=True)

    rarity = "⚪ Common"
    if item['price'] > 50000: rarity = "🔵 Rare"
    if item['price'] > 500000: rarity = "🟡 Legendary"
    if item['price'] > 10000000: rarity = "🔴 Godly"

    text = f"💎 {stylize_text(item['name'])}\n💰 {format_money(item['price'])}\n🌟 {rarity}\n🛡️ Safe (Until Death)"
    await query.answer(text, show_alert=True)

# --- ECONOMY COMMANDS ---

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if users_collection.find_one({"user_id": user.id}): 
        return await update.message.reply_text(f"✨ <b>Ara?</b> {get_mention(user)}, already registered!", parse_mode=ParseMode.HTML)
    
    ensure_user_exists(user)
    users_collection.update_one({"user_id": user.id}, {"$set": {"balance": REGISTER_BONUS}})
    await update.message.reply_text(f"🎉 <b>Yayy!</b> {get_mention(user)} Registered!\n🎁 <b>Bonus:</b> <code>+{format_money(REGISTER_BONUS)}</code>", parse_mode=ParseMode.HTML)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target, error = await resolve_target(update, context)
    if not target and error == "No target": target = ensure_user_exists(update.effective_user)
    elif not target: return await update.message.reply_text(error, parse_mode=ParseMode.HTML)

    # Tracking last group for database consistency
    users_collection.update_one({"user_id": target['user_id']}, {"$set": {"last_chat_id": update.effective_chat.id}})

    bal = target.get('balance', 0)
    rank = users_collection.count_documents({"balance": {"$gt": bal}}) + 1
    status = "💖 Alive" if target.get('status', 'alive') == 'alive' else "💀 Dead"
    current_exp = target.get('exp', 0)
    
    inventory = target.get('inventory', [])
    flex = [i for i in inventory if i.get('type') == 'flex']
    
    kb = []
    row = []
    for item in flex:
        row.append(InlineKeyboardButton(item['name'], callback_data=f"inv_view|{item['id']}"))
        if len(row) == 2:
            kb.append(row)
            row = []
    if row: kb.append(row)
    
    msg = (
        f"👤 <b>{get_mention(target)}</b>\n"
        f"👛 <b>{format_money(bal)}</b> | 🏆 <b>#{rank}</b>\n"
        f"✨ <b>EXP:</b> <code>{current_exp}</code>\n"
        f"❤️ <b>{status}</b> | ⚔️ <b>{target.get('kills', 0)} Kills</b>\n\n"
        f"💎 <b>{stylize_text('Flex Collection')}</b>:"
    )
    if not flex: msg += "\n<i>Empty...</i>"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb) if kb else None)

async def ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rich = users_collection.find().sort("balance", -1).limit(10)
    def get_badge(i): return ["🥇","🥈","🥉"][i-1] if i<=3 else f"<code>{i}.</code>"

    msg = f"🏆 <b>{stylize_text('GLOBAL RICHEST')}</b> 🏆\n\n"
    for i, d in enumerate(rich, 1): msg += f"{get_badge(i)} {get_mention(d)} » <b>{format_money(d.get('balance',0))}</b>\n"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

async def give(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = ensure_user_exists(update.effective_user)
    args = context.args
    if not args: return await update.message.reply_text("⚠️ <b>Usage:</b> <code>/give 100 @user</code>")
    
    try: amount = int(next(arg for arg in args if arg.isdigit()))
    except: return await update.message.reply_text("⚠️ Invalid Amount")

    target, error = await resolve_target(update, context)
    if not target: return await update.message.reply_text(error or "⚠️ Tag someone.")

    if amount <= 0 or sender.get('balance', 0) < amount or sender['user_id'] == target['user_id']: 
        return await update.message.reply_text("⚠️ Invalid Transaction.")

    tax = int(amount * TAX_RATE)
    final = amount - tax
    
    users_collection.update_one({"user_id": sender["user_id"]}, {"$inc": {"balance": -amount}})
    users_collection.update_one({"user_id": target["user_id"]}, {"$inc": {"balance": final}})
    users_collection.update_one({"user_id": OWNER_ID}, {"$inc": {"balance": tax}})

    await update.message.reply_text(f"💸 <b>Transfer Complete!</b>\n💰 Sent: <code>{format_money(final)}</code>", parse_mode=ParseMode.HTML)

async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    ensure_user_exists(user)
    
    # Initialize group and ensure title is saved correctly
    group_doc = get_group_data(chat.id, chat.title)
    if group_doc.get("claimed"): return await update.message.reply_text("❌ Already claimed by this group.")
    
    count = await context.bot.get_chat_member_count(chat.id)
    if count < MIN_CLAIM_MEMBERS:
        return await update.message.reply_text(f"❌ Need {MIN_CLAIM_MEMBERS} members in group.")
    
    users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": CLAIM_BONUS}})
    groups_collection.update_one({"chat_id": chat.id}, {"$set": {"claimed": True}})
    await update.message.reply_text(f"💎 <b>Claimed {format_money(CLAIM_BONUS)}!</b>", parse_mode=ParseMode.HTML)

async def sell_xp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try: amount_to_sell = int(context.args[0])
    except: return await update.message.reply_text("⚠️ Usage: /sellxp 100")

    user_doc = users_collection.find_one({"user_id": user.id})
    if not user_doc or user_doc.get("exp", 0) < amount_to_sell:
        return await update.message.reply_text("⚠️ Not enough EXP!")

    coins = amount_to_sell // EXCHANGE_RATE
    users_collection.update_one({"user_id": user.id}, {"$inc": {"exp": -amount_to_sell, "balance": coins}})
    await update.message.reply_text(f"🔄 Exchanged for <code>{format_money(coins)}</code>", parse_mode=ParseMode.HTML)

# --- AUTO HANDLERS ---

async def check_chat_xp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private" or not update.message or not update.effective_user: 
        return
    
    user_id = update.effective_user.id
    current_time = time.time()
    chat_title = update.effective_chat.title

    # IMPORTANT: Update both activity points AND the group title for the leaderboard
    update_group_activity(update.effective_chat.id, chat_title)

    if user_id in user_cooldowns and (current_time - user_cooldowns[user_id] < EXP_COOLDOWN): 
        return 

    xp_amount = random.randint(*EXP_RANGE)
    users_collection.update_one(
        {"user_id": user_id}, 
        {"$inc": {"exp": xp_amount}, "$set": {"last_chat_id": update.effective_chat.id}}, 
        upsert=True
    )
    user_cooldowns[user_id] = current_time
