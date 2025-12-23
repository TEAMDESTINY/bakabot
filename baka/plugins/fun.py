# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Fun & Gambling Plugin - GIFs + Dice + Slots

import random
import html
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.utils import ensure_user_exists, get_mention, format_money, stylize_text
from baka.database import users_collection

# --- 🎬 GIF DATABASE ---
ACTION_GIFS = {
    "slap": ["https://giphy.com/gifs/yhuW8n4EkcFroBPyEA", "https://giphy.com/gifs/u4NlnT97rltFZEROjo"],
    "punch": ["https://giphy.com/gifs/dsUtTbPhnJYHYTB5z8", "https://giphy.com/gifs/GLhxaMPYFgHZ7oXMEA"],
    "hug": ["https://files.catbox.moe/zknne5.mp4", "https://files.catbox.moe/8skije.mp4" , "https://files.catbox.moe/4oytk6.mp4"],
    "kiss": ["https://files.catbox.moe/rp395w.mp4", "https://files.catbox.moe/bd5t8n.mp4" , "https://files.catbox.moe/1w6ap9.mp4"]
}

# --- ⚙️ ACTION HANDLER ---
async def perform_action(update: Update, context: ContextTypes.DEFAULT_TYPE, action_name: str, emoji: str):
    sender = update.effective_user
    if not update.message.reply_to_message:
        return await update.message.reply_text(f"❗ {stylize_text('Usage')}: Reply to someone to {action_name.lower()} them!")
    
    target = update.message.reply_to_message.from_user
    if target.id == sender.id:
        return await update.message.reply_text(f"🤔 Khud ko hi {action_name.lower()} karoge?")

    gif_url = random.choice(ACTION_GIFS.get(action_name.lower(), []))
    caption = f"{emoji} {get_mention(sender)} <b>{action_name.upper()}ED</b> {get_mention(target)}!"

    try:
        await update.message.reply_animation(animation=gif_url, caption=caption, parse_mode=ParseMode.HTML)
    except:
        await update.message.reply_text(caption, parse_mode=ParseMode.HTML)

# --- 🖐️ FUN ACTIONS (RYAN.PY SYNC) ---
async def slap(update: Update, context: ContextTypes.DEFAULT_TYPE): await perform_action(update, context, "Slap", "🖐️")
async def punch(update: Update, context: ContextTypes.DEFAULT_TYPE): await perform_action(update, context, "Punch", "👊")
async def hug(update: Update, context: ContextTypes.DEFAULT_TYPE): await perform_action(update, context, "Hug", "🫂")
async def kiss(update: Update, context: ContextTypes.DEFAULT_TYPE): await perform_action(update, context, "Kiss", "💋")

# --- 🎲 GAMBLING: DICE ---
async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = ensure_user_exists(update.effective_user)
    if not context.args: return await update.message.reply_text("🎲 <b>Usage:</b> <code>/dice [amount]</code>", parse_mode=ParseMode.HTML)
    
    try: bet = int(context.args[0])
    except: return await update.message.reply_text("⚠️ Invalid bet.")
    
    if bet < 50: return await update.message.reply_text("⚠️ Min bet is $50.")
    if user['balance'] < bet: return await update.message.reply_text("📉 Not enough money.")
    
    msg = await context.bot.send_dice(update.effective_chat.id, emoji='🎲')
    result = msg.dice.value 
    await asyncio.sleep(3) # Animation delay
    
    if result > 3: # Win: 4, 5, 6
        users_collection.update_one({"user_id": user["user_id"]}, {"$inc": {"balance": bet}})
        text = f"🎲 <b>Result:</b> {result}\n🎉 <b>You Won!</b> +<code>{format_money(bet)}</code>"
    else: # Loss: 1, 2, 3
        users_collection.update_one({"user_id": user["user_id"]}, {"$inc": {"balance": -bet}})
        text = f"🎲 <b>Result:</b> {result}\n💀 <b>You Lost!</b> -<code>{format_money(bet)}</code>"
    
    await update.message.reply_text(text, reply_to_message_id=msg.message_id, parse_mode=ParseMode.HTML)

# --- 🎰 GAMBLING: SLOTS ---
async def slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = ensure_user_exists(update.effective_user)
    bet = 100 
    if user['balance'] < bet: return await update.message.reply_text("📉 Need $100 to spin.")
    
    users_collection.update_one({"user_id": user["user_id"]}, {"$inc": {"balance": -bet}})
    msg = await context.bot.send_dice(update.effective_chat.id, emoji='🎰')
    value = msg.dice.value 
    await asyncio.sleep(2)
    
    if value == 64: # Jackpot (777)
        prize = bet * 10
        users_collection.update_one({"user_id": user["user_id"]}, {"$inc": {"balance": prize}})
        text = f"🎰 <b>JACKPOT! (777)</b>\n🎉 You won <code>{format_money(prize)}</code>!"
    elif value in [1, 22, 43]: # Triple Fruits
        prize = bet * 3
        users_collection.update_one({"user_id": user["user_id"]}, {"$inc": {"balance": prize}})
        text = f"🎰 <b>Winner!</b>\n🎉 You won <code>{format_money(prize)}</code>!"
    else:
        text = f"🎰 <b>Lost!</b>"
    
    await update.message.reply_text(text, reply_to_message_id=msg.message_id, parse_mode=ParseMode.HTML)
