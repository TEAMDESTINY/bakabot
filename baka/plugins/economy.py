# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Location: Supaul, Bihar 
# Integrated with Advanced Group Economy Features

import random
import time
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import REGISTER_BONUS, OWNER_ID, TAX_RATE, CLAIM_BONUS, MARRIED_TAX_RATE, SHOP_ITEMS, MIN_CLAIM_MEMBERS
from baka.utils import ensure_user_exists, get_mention, format_money, resolve_target, log_to_channel, stylize_text
from baka.database import users_collection, groups_collection

# --- CONFIGURATION ---
EXP_COOLDOWN = 60  
EXP_RANGE = (1, 5) 
EXCHANGE_RATE = 10 
user_cooldowns = {} 

# --- HELPER FOR GROUP DATA ---
def get_group_econ(chat_id, title="Unknown"):
    group = groups_collection.find_one({"chat_id": chat_id})
    if not group:
        group = {
            "chat_id": chat_id,
            "title": title,
            "treasury": 10000, # Initial Bonus
            "shares": 10.0,
            "claimed": False
        }
        groups_collection.insert_one(group)
    return group

# --- GROUP ECONOMY COMMANDS (Viral Features) ---

async def group_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command: /group - Dikhata hai group kitna ameer hai aur multiplier kya hai"""
    chat = update.effective_chat
    if chat.type == "private":
        return await update.message.reply_text("❌ Ye command sirf groups mein kaam karti hai!")
    
    group = get_group_econ(chat.id, chat.title)
    # Multiplier based on active users in the last 24h (simulated by last_chat_id)
    active_count = users_collection.count_documents({"last_chat_id": chat.id})
    
    multiplier = 1.0 + (active_count // 5) * 0.5 # Har 5 active users par +0.5x
    if multiplier > 5.0: multiplier = 5.0

    msg = (
        f"🏢 <b>GROUP HUB: {stylize_text(chat.title)}</b>\n\n"
        f"💰 <b>Treasury:</b> <code>{format_money(group.get('treasury', 0))}</code>\n"
        f"📈 <b>Group Rank:</b> <code>#ComingSoon</code>\n"
        f"👥 <b>Active Squad:</b> <code>{active_count} Members</code>\n"
        f"⚡ <b>Economy Boost:</b> <code>{multiplier}x</code>\n\n"
        f"<i>💡 Multiplier badhane ke liye aur active log chahiye!</i>"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

async def raid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command: /raid @username - Doosre group ki treasury lootne ke liye"""
    user = update.effective_user
    chat = update.effective_chat
    
    if chat.type == "private": return
    if not context.args:
        return await update.message.reply_text("⚠️ <b>Usage:</b> <code>/raid @TargetGroup</code>")

    target_input = context.args[0].replace("@", "")
    # Finding group by title/username (Note: Ensure your track_group saves username)
    target_group = groups_collection.find_one({"title": {"$regex": target_input, "$options": "i"}})

    if not target_group:
        return await update.message.reply_text("❌ Wo group bot ki radar mein nahi hai!")

    if target_group['chat_id'] == chat.id:
        return await update.message.reply_text("❌ Khud ke group ko lootna gunah hai!")

    chance = random.randint(1, 100)
    if chance > 75: # 25% Success Rate
        loot = int(target_group.get('treasury', 0) * 0.15)
        if loot < 500: loot = 1000
        
        groups_collection.update_one({"chat_id": target_group['chat_id']}, {"$inc": {"treasury": -loot}})
        users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": loot}})
        
        await update.message.reply_text(f"🔥 <b>RAID SUCCESSFUL!</b>\n\n{get_mention(user)} ne <b>{target_group['title']}</b> ki treasury se <code>{format_money(loot)}</code> chura liye!")
    else:
        fine = 5000
        users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": -fine}})
        await update.message.reply_text(f"💀 <b>RAID FAILED!</b>\n\nAapki team pakdi gayi. <code>{format_money(fine)}</code> ka jurmana bharna pada.")

# --- ORIGINAL & EXP COMMANDS ---

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

    # Tracking group activity for multiplier
    users_collection.update_one({"user_id": target['user_id']}, {"$set": {"last_chat_id": update.effective_chat.id}})

    rank = users_collection.count_documents({"balance": {"$gt": target["balance"]}}) + 1
    status = "💖 Alive" if target.get('status', 'alive') == 'alive' else "💀 Dead"
    current_exp = target.get('exp', 0)
    
    inventory = target.get('inventory', [])
    weapons = [i for i in inventory if i['type'] == 'weapon']
    armors = [i for i in inventory if i['type'] == 'armor']
    flex = [i for i in inventory if i['type'] == 'flex']
    
    best_w = max(weapons, key=lambda x: x['buff'])['name'] if weapons else "None"
    best_a = max(armors, key=lambda x: x['buff'])['name'] if armors else "None"
    
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
        f"👛 <b>{format_money(target['balance'])}</b> | 🏆 <b>#{rank}</b>\n"
        f"✨ <b>EXP:</b> <code>{current_exp}</code>\n"
        f"❤️ <b>{status}</b> | ⚔️ <b>{target.get('kills', 0)} Kills</b>\n\n"
        f"🎒 <b>{stylize_text('Active Gear')}</b>:\n"
        f"🗡️ {best_w}\n🛡️ {best_a}\n\n"
        f"💎 <b>{stylize_text('Flex Collection')}</b>:"
    )
    if not flex: msg += "\n<i>Empty...</i>"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(kb) if kb else None)

async def sell_xp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        return await update.message.reply_text("⚠️ <b>Usage:</b> <code>/sellxp [amount]</code>", parse_mode=ParseMode.HTML)
    
    try: amount_to_sell = int(context.args[0])
    except: return await update.message.reply_text("❌ Invalid number.")

    user_doc = users_collection.find_one({"user_id": user.id})
    current_exp = user_doc.get("exp", 0) if user_doc else 0

    if current_exp < amount_to_sell:
        return await update.message.reply_text(f"⚠️ Not enough EXP! You have: <code>{current_exp}</code>")

    coins = amount_to_sell // EXCHANGE_RATE
    if coins < 1: return await update.message.reply_text(f"⚠️ Min {EXCHANGE_RATE} EXP needed.")

    users_collection.update_one({"user_id": user.id}, {"$inc": {"exp": -amount_to_sell, "balance": coins}})
    await update.message.reply_text(f"🔄 <b>Sold:</b> <code>{amount_to_sell} EXP</code>\n➕ <b>Earned:</b> <code>{format_money(coins)}</code>", parse_mode=ParseMode.HTML)

# --- AUTO HANDLERS ---

async def check_chat_xp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private" or not update.message or not update.effective_user:
        return
    
    user_id = update.effective_user.id
    current_time = time.time()

    if user_id in user_cooldowns and (current_time - user_cooldowns[user_id] < EXP_COOLDOWN):
        return 

    xp_amount = random.randint(*EXP_RANGE)
    # Important: Track where the user is talking for multiplier
    users_collection.update_one(
        {"user_id": user_id}, 
        {"$inc": {"exp": xp_amount}, "$set": {"last_chat_id": update.effective_chat.id}}, 
        upsert=True
    )
    user_cooldowns[user_id] = current_time

# Note: Add 'ranking', 'claim', 'give' functions back from your original code here...
