# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Fixed Shop Plugin - Public Access Version

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.utils import ensure_user_exists, format_money, get_mention, stylize_text
from baka.database import users_collection
from baka.config import SHOP_ITEMS
from datetime import datetime

ITEMS_PER_PAGE = 6

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

# --- MENUS ---
async def shop_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = ensure_user_exists(update.effective_user)
    text = (
        f"🛒 <b>{stylize_text('Baka Marketplace')}</b>\n\n"
        f"👤 <b>Customer:</b> {get_mention(user)}\n"
        f"👛 <b>Wallet:</b> <code>{format_money(user['balance'])}</code>\n\n"
        f"<i>Select a category to browse our goods!</i>"
    )
    kb = get_main_menu_kb()
    if update.callback_query:
        await update.callback_query.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)
    else:
        await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)

# --- CALLBACK HANDLER (NO SUDO CHECK) ---
async def shop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    # 🚨 FIX: Sabhi users ke liye answer enable kiya
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
        # Refresh current view
        await shop_menu(update, context)

    elif action == "shop_poor": await query.answer("📉 You are too poor!", show_alert=True)
    elif action == "shop_owned": await query.answer("🎒 Already owned!", show_alert=True)

async def buy(update, context):
    user = ensure_user_exists(update.effective_user)
    if not context.args: return await update.message.reply_text("⚠️ <b>Usage:</b> <code>/buy knife</code>", parse_mode=ParseMode.HTML)
    item_key = context.args[0].lower()
    item = next((i for i in SHOP_ITEMS if i['id'] == item_key), None)
    if not item: return await update.message.reply_text(f"❌ Item <b>{item_key}</b> not found.", parse_mode=ParseMode.HTML)
    if user['balance'] < item['price']: return await update.message.reply_text(f"❌ You need <code>{format_money(item['price'])}</code>!", parse_mode=ParseMode.HTML)
    if any(i['id'] == item_key for i in user.get('inventory', [])): return await update.message.reply_text("⚠️ Already owned!", parse_mode=ParseMode.HTML)

    item_with_time = item.copy()
    item_with_time['bought_at'] = datetime.utcnow()
    users_collection.update_one({"user_id": user['user_id']}, {"$inc": {"balance": -item['price']}, "$push": {"inventory": item_with_time}})
    await update.message.reply_text(f"✅ Bought <b>{item['name']}</b>!", parse_mode=ParseMode.HTML)
