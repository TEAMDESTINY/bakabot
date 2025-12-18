# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Economy Plugin - With Item Gifting & Optimized Logic

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
EXCHANGE_RATE = 10 # 10 EXP = 1 Coin
user_cooldowns = {} 

# --- INVENTORY CALLBACK ---
async def inventory_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split("|")
    item_id = data[1]
    
    item = next((i for i in SHOP_ITEMS if i['id'] == item_id), None)
    if not item: return await query.answer("❌ Item Not Found", show_alert=True)

    rarity = "⚪ Common"
    if item['price'] > 50000: rarity = "🔵 Rare"
    if item['price'] > 500000: rarity = "🟡 Legendary"
    if item['price'] > 10000000: rarity = "🔴 Godly"

    text = f"💎 {stylize_text(item['name'])}\n💰 {format_money(item['price'])}\n🌟 {rarity}\n🛡️ {stylize_text('Protected Status')}"
    await query.answer(text, show_alert=True)

# --- ECONOMY COMMANDS ---

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if users_collection.find_one({"user_id": user.id}): 
        return await update.message.reply_text(f"✨ <b>{stylize_text('Ara?')}</b> {get_mention(user)}, already registered!", parse_mode=ParseMode.HTML)
    
    ensure_user_exists(user)
    users_collection.update_one({"user_id": user.id}, {"$set": {"balance": REGISTER_BONUS}})
    await update.message.reply_text(f"🎉 <b>{stylize_text('Yayy!')}</b> {get_mention(user)} Registered!\n🎁 <b>{stylize_text('Bonus')}:</b> <code>+{format_money(REGISTER_BONUS)}</code>", parse_mode=ParseMode.HTML)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target, error = await resolve_target(update, context)
    if not target and error == "No target": target = ensure_user_exists(update.effective_user)
    elif not target: return await update.message.reply_text(error, parse_mode=ParseMode.HTML)

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
            kb.append(row); row = []
    if row: kb.append(row)
    
    msg = (
        f"👤 <b>{get_mention(target)}</b>\n"
        f"👛 <b>{format_money(bal)}</b> | 🏆 <b>#{rank}</b>\n"
        f"✨ <b>{stylize_text('EXP')}:</b> <code>{current_exp}</code>\n"
        f"❤️ <b>{status}</b> | ⚔️ <b>{target.get('kills', 0)} Kills</b>\n\n"
        f"💎 <b>{stylize_text('Flex Collection')}</b>:"
    )
    if not flex: msg += "\n<i>Empty...</i>"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb) if kb else None)

async def give(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = ensure_user_exists(update.effective_user)
    args = context.args
    if not args: return await update.message.reply_text(f"⚠️ <b>{stylize_text('Usage')}:</b> <code>/give 100 @user</code>")
    
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

    await update.message.reply_text(f"💸 <b>{stylize_text('Transfer Complete')}!</b>\n💰 Sent: <code>{format_money(final)}</code>", parse_mode=ParseMode.HTML)

# --- NEW: GIVE ITEM COMMAND ---
async def give_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender_obj = update.effective_user
    sender_db = ensure_user_exists(sender_obj)
    
    if len(context.args) < 1:
        return await update.message.reply_text(f"⚠️ <b>{stylize_text('Usage')}:</b> <code>/giveitem [name] @user</code>")

    item_query = context.args[0].lower()
    target_db, error = await resolve_target(update, context, specific_arg=context.args[1] if len(context.args) > 1 else None)
    
    if not target_db: return await update.message.reply_text(error or "❌ User not found!")

    inventory = sender_db.get('inventory', [])
    item = next((i for i in inventory if item_query in i['name'].lower() or item_query in i['id'].lower()), None)

    if not item: return await update.message.reply_text(f"❌ {stylize_text('Item aapke paas nahi hai!')}")
    if sender_db['user_id'] == target_db['user_id']: return await update.message.reply_text("🙄")

    users_collection.update_one({"user_id": sender_db['user_id']}, {"$pull": {"inventory": {"id": item['id']}}})
    users_collection.update_one({"user_id": target_db['user_id']}, {"$push": {"inventory": item}})

    await update.message.reply_text(
        f"🎁 <b>{stylize_text('ITEM GIFTED')}!</b>\n\n"
        f"{get_mention(sender_obj)} 𝒏𝒆 {get_mention(target_db)} 𝒌𝒐 <b>{item['name']}</b> 𝒕𝒓𝒂𝒏𝒔𝒇𝒆𝒓 𝒌𝒊𝒚𝒂!",
        parse_mode=ParseMode.HTML
    )

async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    if chat.type == "private": return await update.message.reply_text("❌ Groups Only!")

    ensure_user_exists(user)
    group_doc = get_group_data(chat.id, chat.title)
    
    if group_doc.get("claimed"): 
        return await update.message.reply_text(f"🕒 <b>{stylize_text('Already Claimed!')}</b>")
    
    count = await context.bot.get_chat_member_count(chat.id)
    if count < MIN_CLAIM_MEMBERS:
        return await update.message.reply_text(f"❌ <b>{stylize_text('Group too small')}!</b>")
    
    users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": CLAIM_BONUS}})
    groups_collection.update_one({"chat_id": chat.id}, {"$set": {"claimed": True}})
    
    await update.message.reply_text(f"💎 <b>{stylize_text('Claimed')}</b> <code>{format_money(CLAIM_BONUS)}</code>!", parse_mode=ParseMode.HTML)

# --- AUTO HANDLERS ---
async def check_chat_xp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or update.effective_chat.type == "private" or not update.effective_user: return
    
    user_id = update.effective_user.id
    current_time = time.time()
    update_group_activity(update.effective_chat.id, update.effective_chat.title)

    if user_id in user_cooldowns and (current_time - user_cooldowns[user_id] < EXP_COOLDOWN): return 

    xp_amount = random.randint(*EXP_RANGE)
    users_collection.update_one({"user_id": user_id}, {"$inc": {"exp": xp_amount}}, upsert=True)
    user_cooldowns[user_id] = current_time
