# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Shop Plugin - Buying, Gifting & Inventory System

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.utils import ensure_user_exists, format_money, get_mention, stylize_text, resolve_target
from baka.database import users_collection
from baka.config import SHOP_ITEMS
from datetime import datetime

ITEMS_PER_PAGE = 6

# --- 🎁 SOCIAL GIFT ITEMS DATA (As requested earlier) ---
GIFT_ITEMS = {
    "rose": {"name": "🌹 Rose", "price": 500},
    "chocolate": {"name": "🍫 Chocolate", "price": 800},
    "ring": {"name": "💍 Ring", "price": 2000},
    "teddy bear": {"name": "🧸 Teddy Bear", "price": 1500},
    "pizza": {"name": "🍕 Pizza", "price": 600},
    "surprise box": {"name": "🎁 Surprise Box", "price": 2500},
    "puppy": {"name": "🐶 Puppy", "price": 3000},
    "cake": {"name": "🎂 Cake", "price": 1000},
    "love letter": {"name": "💌 Love Letter", "price": 400},
    "cat": {"name": "🐱 Cat", "price": 2500}
}

# --- HELPERS ---
def get_rarity(price):
    if price < 5000: return "⚪ Common"
    if price < 20000: return "🟢 Uncommon"
    if price < 100000: return "🔵 Rare"
    if price < 1000000: return "🟣 Epic"
    if price < 10000000: return "🟡 Legendary"
    return "🔴 GODLY"

def get_description(item):
    if item['id'] == "deathnote": return "Writes names. Deletes people. 60% Kill Buff."
    if item['id'] == "plot": return "Literal Plot Armor. You cannot die. 60% Block."
    if item['type'] == 'weapon': return f"A deadly weapon. +{int(item['buff']*100)}% Kill rewards."
    if item['type'] == 'armor': return f"Protective gear. {int(item['buff']*100)}% Robbery block chance."
    return "A high-value flex item."

# --- KEYBOARD BUILDERS ---
def get_main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚔️ 𝐖𝐞𝐚𝐩𝐨𝐧𝐬", callback_data="shop_cat|weapon|0"),
         InlineKeyboardButton("🛡️ 𝐀𝐫𝐦𝐨𝐫", callback_data="shop_cat|armor|0")],
        [InlineKeyboardButton("💎 𝐅𝐥𝐞𝐱 & 𝐕𝐈𝐏", callback_data="shop_cat|flex|0")],
        [InlineKeyboardButton("🔙 𝐂𝐥𝐨𝐬𝐞", callback_data="shop_close")]
    ])

def get_category_kb(category_type, page=0):
    items = [i for i in SHOP_ITEMS if i['type'] == category_type]
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    current_items = items[start_idx:end_idx]
    
    keyboard = []
    row = []
    for item in current_items:
        price_k = f"{item['price']//1000}k" if item['price'] >= 1000 else item['price']
        text = f"{item['name']} [{price_k}]"
        row.append(InlineKeyboardButton(text, callback_data=f"shop_view|{item['id']}|{category_type}|{page}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row: keyboard.append(row)
    
    nav = []
    if page > 0: nav.append(InlineKeyboardButton("⬅️", callback_data=f"shop_cat|{category_type}|{page-1}"))
    nav.append(InlineKeyboardButton("🔙 𝐌𝐞𝐧υ", callback_data="shop_home"))
    if end_idx < len(items): nav.append(InlineKeyboardButton("➡️", callback_data=f"shop_cat|{category_type}|{page+1}"))
    keyboard.append(nav)
    return InlineKeyboardMarkup(keyboard)

def get_item_kb(item_id, category, page, can_afford, is_owned):
    kb = []
    if is_owned: kb.append([InlineKeyboardButton("✅ 𝐎𝐰𝐧𝐞𝐝", callback_data="shop_owned")])
    elif can_afford: kb.append([InlineKeyboardButton("💳 𝐁υ𝐲 𝐍𝐨𝐰", callback_data=f"shop_buy|{item_id}|{category}|{page}")])
    else: kb.append([InlineKeyboardButton("❌ 𝐂ᴧη'ᴛ ᴧғғσꝛᴅ", callback_data="shop_poor")])
    kb.append([InlineKeyboardButton("🔙 𝐁ᴧᴄᴋ", callback_data=f"shop_cat|{category}|{page}")])
    return InlineKeyboardMarkup(kb)

# --- MENUS & COMMANDS ---
async def shop_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = ensure_user_exists(update.effective_user)
    text = (
        f"🛒 <b>{stylize_text('Baka Marketplace')}</b>\n\n"
        f"👤 <b>Customer:</b> {user['name']}\n"
        f"👛 <b>Wallet:</b> <code>{format_money(user['balance'])}</code>\n\n"
        f"<i>Select a category to browse our goods!</i>"
    )
    kb = get_main_menu_kb()
    if update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)
    else:
        await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)

# This fixes the AttributeError for /items
async def items_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "<b>🛍️ Social Gift Items</b>\n\n"
    for key, val in GIFT_ITEMS.items():
        msg += f"• {val['name']} — <code>{format_money(val['price'])}</code>\n"
    msg += "\n📌 <b>Usage:</b> Reply with <code>/gift [item name]</code>\n"
    msg += "ℹ️ Use <code>/shop</code> for Weapons & Armor."
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# This fixes the AttributeError for /item (Inventory)
async def view_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_db, error = await resolve_target(update, context)
    if not target_db:
        target_db = ensure_user_exists(update.effective_user)

    inv = target_db.get('inventory', [])
    name = target_db.get('name', "User")

    msg = f"📦 <b>{name}'s Inventory</b>\n━━━━━━━━━━━━━━━━━━\n"
    if not inv:
        msg += "<i>Empty... Go earn some gifts or buy gear!</i>"
    else:
        item_counts = {}
        for i in inv:
            name_str = i['name']
            item_counts[name_str] = item_counts.get(name_str, 0) + 1
        
        for item_name, count in item_counts.items():
            msg += f"• {item_name} (x{count})\n"

    msg += "\n━━━━━━━━━━━━━━━━━━"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# GIFTING LOGIC
async def gift_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = update.effective_user
    sender_db = ensure_user_exists(sender)

    if not update.message.reply_to_message:
        return await update.message.reply_text("❗ <b>Usage:</b> Reply to someone with <code>/gift [item name]</code>")

    if not context.args:
        return await update.message.reply_text("⚠️ Specify an item! Example: <code>/gift rose</code>")

    target = update.message.reply_to_message.from_user
    item_query = " ".join(context.args).lower()
    item = GIFT_ITEMS.get(item_query)

    if not item:
        return await update.message.reply_text("❌ Social gift not found! Use <code>/items</code> to see the list.")

    if sender_db.get('balance', 0) < item['price']:
        return await update.message.reply_text(f"❌ Low balance! Needs {format_money(item['price'])}.")

    users_collection.update_one({"user_id": sender.id}, {"$inc": {"balance": -item['price']}})
    users_collection.update_one(
        {"user_id": target.id}, 
        {"$push": {"inventory": {"name": item['name'], "gifted_by": sender.first_name, "date": datetime.utcnow()}}}
    )

    await update.message.reply_text(f"🎁 <b>{sender.first_name}</b> gifted a {item['name']} to <b>{target.first_name}</b>!", parse_mode=ParseMode.HTML)

# --- CALLBACK HANDLER ---
async def shop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() 
    
    user = ensure_user_exists(query.from_user)
    data = query.data.split("|")
    action = data[0]
    
    if action == "shop_close":
        await query.message.delete()
        return
    if action == "shop_home":
        await shop_menu(update, context)
        return
    
    if action == "shop_cat":
        cat_type = data[1]
        page = int(data[2]) if len(data) > 2 else 0
        titles = {"weapon": "⚔️ <b>𝐖𝐞𝐚𝐩𝐨𝐧𝐬 𝐀𝐫𝐦𝐨𝐫𝐲</b>", "armor": "🛡️ <b>𝐃𝐞𝐟𝐞𝐧𝐬𝐞 𝐒𝐲𝐬𝐭𝐞𝐦𝐬</b>", "flex": "💎 <b>𝐕𝐈𝐏 𝐅𝐥𝐞𝐱 𝐙𝐨𝐧𝐞</b>"}
        text = f"{titles.get(cat_type, 'Shop')}\n\n💰 <b>Balance:</b> <code>{format_money(user['balance'])}</code>"
        await query.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=get_category_kb(cat_type, page))

    elif action == "shop_view":
        item_id, cat, page = data[1], data[2], data[3]
        item = next((i for i in SHOP_ITEMS if i['id'] == item_id), None)
        if not item: return
        
        is_owned = any(i['id'] == item_id for i in user.get('inventory', []))
        text = (
            f"🛍️ <b>{item['name']}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📖 <i>{get_description(item)}</i>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💰 <b>Price:</b> <code>{format_money(item['price'])}</code>\n"
            f"🌟 <b>Rarity:</b> {get_rarity(item['price'])}\n"
            f"⏱️ <b>Life:</b> 24 Hours\n\n"
            f"👛 <b>Wallet:</b> <code>{format_money(user['balance'])}</code>"
        )
        await query.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=get_item_kb(item_id, cat, page, user['balance'] >= item['price'], is_owned))

    elif action == "shop_buy":
        item_id, cat, page = data[1], data[2], data[3]
        item = next((i for i in SHOP_ITEMS if i['id'] == item_id), None)
        if not item or user['balance'] < item['price']: return
        
        item_with_time = item.copy()
        item_with_time['bought_at'] = datetime.utcnow()
        users_collection.update_one({"user_id": user['user_id']}, {"$inc": {"balance": -item['price']}, "$push": {"inventory": item_with_time}})
        await query.answer(f"🎉 Bought {item['name']}!", show_alert=True)
        await shop_menu(update, context)

    elif action == "shop_poor": await query.answer("📉 You are too poor!", show_alert=True)
    elif action == "shop_owned": await query.answer("🎒 Already owned!", show_alert=True)
