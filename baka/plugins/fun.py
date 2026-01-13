# Copyright (c) 2026 Telegram:- @WTF_Phantom <DevixOP>
# Final Fun, Gambling & Brain Plugin - HTML Format (No Tap-to-Copy)

import random
import html
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.utils import ensure_user_exists, format_money
from baka.database import users_collection

# --- 🧠 BRAIN/IQ COMMAND (0-100 Range) ---
async def brain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Calculates a random IQ level between 0 and 100."""
    # Check if command is a reply
    if not update.message.reply_to_message:
        return await update.message.reply_text(
            "<b>Reply to someone ! 🤖</b>", 
            parse_mode=ParseMode.HTML
        )

    target_user = update.message.reply_to_message.from_user
    iq_level = random.randint(0, 100) # Range 0-100
    
    # Emoji based on IQ result
    emoji = "😎" if iq_level >= 75 else "🤔" if iq_level >= 50 else "😐" if iq_level >= 25 else "🤡"
    
    # English HTML Output
    response = f"<b>IQ level of {target_user.first_name.upper()} is {iq_level}% {emoji}</b>"
    
    await update.message.reply_text(response, parse_mode=ParseMode.HTML)

# --- 🎬 GIF DATABASE ---
ACTION_GIFS = {
    "slap": ["https://giphy.com/gifs/yhuW8n4EkcFroBPyEA", "https://giphy.com/gifs/u4NlnT97rltFZEROjo"],
    "punch": ["https://giphy.com/gifs/dsUtTbPhnJYHYTB5z8", "https://giphy.com/gifs/GLhxaMPYFgHZ7oXMEA"],
    "hug": ["https://files.catbox.moe/zknne5.mp4", "https://files.catbox.moe/8skije.mp4"],
    "kiss": ["https://files.catbox.moe/rp395w.mp4", "https://files.catbox.moe/bd5t8n.mp4"]
}

# --- ⚙️ ACTION HANDLER ---
async def perform_action(update: Update, context: ContextTypes.DEFAULT_TYPE, action_name: str, emoji: str):
    sender = update.effective_user
    if not update.message.reply_to_message:
        return await update.message.reply_text(
            f"<b>Usage: Reply to someone to {action_name.lower()} them!</b>", 
            parse_mode=ParseMode.HTML
        )
    
    target = update.message.reply_to_message.from_user
    gif_url = random.choice(ACTION_GIFS.get(action_name.lower(), []))
    caption = f"<b>{emoji} {sender.first_name.upper()} {action_name.upper()}ED {target.first_name.upper()}!</b>"

    try:
        await update.message.reply_animation(animation=gif_url, caption=caption, parse_mode=ParseMode.HTML)
    except:
        await update.message.reply_text(caption, parse_mode=ParseMode.HTML)

# Fun Action Commands
async def slap(update: Update, context: ContextTypes.DEFAULT_TYPE): await perform_action(update, context, "Slap", "🖐️")
async def punch(update: Update, context: ContextTypes.DEFAULT_TYPE): await perform_action(update, context, "Punch", "👊")
async def hug(update: Update, context: ContextTypes.DEFAULT_TYPE): await perform_action(update, context, "Hug", "🫂")
async def kiss(update: Update, context: ContextTypes.DEFAULT_TYPE): await perform_action(update, context, "Kiss", "💋")

# --- 🎲 GAMBLING: DICE ---
async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = ensure_user_exists(update.effective_user)
    if not context.args: 
        return await update.message.reply_text("<b>Usage: /dice [amount]</b>", parse_mode=ParseMode.HTML)
    
    try: bet = int(context.args[0])
    except: return await update.message.reply_text("<b>⚠️ Invalid bet amount.</b>", parse_mode=ParseMode.HTML)
    
    if bet < 50: return await update.message.reply_text("<b>⚠️ Minimum bet is $50.</b>", parse_mode=ParseMode.HTML)
    if user['balance'] < bet: return await update.message.reply_text("<b>📉 Insufficient balance.</b>", parse_mode=ParseMode.HTML)
    
    msg = await context.bot.send_dice(update.effective_chat.id, emoji='🎲')
    result = msg.dice.value 
    await asyncio.sleep(3)
    
    if result > 3: # Win
        users_collection.update_one({"user_id": user["user_id"]}, {"$inc": {"balance": bet}})
        text = f"<b>🎲 Result: {result}\n🎉 You Won! +{format_money(bet)}</b>"
    else: # Loss
        users_collection.update_one({"user_id": user["user_id"]}, {"$inc": {"balance": -bet}})
        text = f"<b>🎲 Result: {result}\n💀 You Lost! -{format_money(bet)}</b>"
    
    await update.message.reply_text(text, reply_to_message_id=msg.message_id, parse_mode=ParseMode.HTML)

# --- 🎰 GAMBLING: SLOTS ---
async def slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = ensure_user_exists(update.effective_user)
    bet = 100 
    if user['balance'] < bet: 
        return await update.message.reply_text("<b>📉 Need $100 to spin.</b>", parse_mode=ParseMode.HTML)
    
    users_collection.update_one({"user_id": user["user_id"]}, {"$inc": {"balance": -bet}})
    msg = await context.bot.send_dice(update.effective_chat.id, emoji='🎰')
    value = msg.dice.value 
    await asyncio.sleep(2)
    
    if value == 64: # Jackpot
        prize = bet * 10
        users_collection.update_one({"user_id": user["user_id"]}, {"$inc": {"balance": prize}})
        text = f"<b>🎰 JACKPOT! (777)\n🎉 You won {format_money(prize)}!</b>"
    elif value in [1, 22, 43]: # Small Win
        prize = bet * 3
        users_collection.update_one({"user_id": user["user_id"]}, {"$inc": {"balance": prize}})
        text = f"<b>🎰 Winner!\n🎉 You won {format_money(prize)}!</b>"
    else: # Loss
        text = f"<b>🎰 Better luck next time!</b>"
    
    await update.message.reply_text(text, reply_to_message_id=msg.message_id, parse_mode=ParseMode.HTML)
