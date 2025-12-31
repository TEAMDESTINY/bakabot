# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Bomb Game - Rankings, Medals & Pot System Sync

import random
import asyncio
import html
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.utils import ensure_user_exists, format_money, stylize_text
from baka.database import users_collection
from baka.config import OWNER_ID

# Global Game State
GAMES = {}

# --- 💣 START BOMB GAME ---
async def start_bomb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    if chat_id in GAMES:
        return await update.message.reply_text("⚠️ A game is already running in this group!")

    if not context.args or not context.args[0].isdigit():
        return await update.message.reply_text("❗ <b>Usage:</b> <code>/bomb <amount></code>", parse_mode=ParseMode.HTML)

    entry_fee = int(context.args[0])
    if entry_fee < 100:
        return await update.message.reply_text("❌ Minimum entry fee is 100 coins.")

    user_db = ensure_user_exists(user)
    if user_db.get('balance', 0) < entry_fee:
        return await update.message.reply_text("❌ You don't have enough balance to start!")

    # Deduct fee and setup game
    users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": -entry_fee}})
    GAMES[chat_id] = {
        "fee": entry_fee,
        "players": [{"id": user.id, "name": user.first_name}],
        "pot": entry_fee,
        "status": "joining",
        "holder_idx": 0
    }

    msg = (
        f"💣 <b>{stylize_text('BOMB GAME STARTED')}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Host:</b> {html.escape(user.first_name)}\n"
        f"💰 <b>Entry Fee:</b> <code>{format_money(entry_fee)}</code>\n"
        f"📝 <b>To Join:</b> <code>/join {entry_fee}</code>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<i>Game starts in 60 seconds (Min 2 players required).</i>"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
    
    await asyncio.sleep(60)
    await run_game(update, context, chat_id)

# --- 🤝 JOIN GAME ---
async def join_bomb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    if chat_id not in GAMES or GAMES[chat_id]["status"] != "joining":
        return await update.message.reply_text("❌ No active joining phase found.")

    game = GAMES[chat_id]
    if any(p["id"] == user.id for p in game["players"]):
        return await update.message.reply_text("⚠️ You already joined!")

    if not context.args or not context.args[0].isdigit() or int(context.args[0]) != game["fee"]:
        return await update.message.reply_text(f"❗ <b>Usage:</b> <code>/join {game['fee']}</code>", parse_mode=ParseMode.HTML)

    user_db = ensure_user_exists(user)
    if user_db.get('balance', 0) < game["fee"]:
        return await update.message.reply_text("❌ Low balance!")

    users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": -game["fee"]}})
    game["players"].append({"id": user.id, "name": user.first_name})
    game["pot"] += game["fee"]

    await update.message.reply_text(f"✅ <b>{html.escape(user.first_name)}</b> joined! Pot: <code>{format_money(game['pot'])}</code>", parse_mode=ParseMode.HTML)

# --- 🏃 PASS BOMB ---
async def pass_bomb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    if chat_id not in GAMES or GAMES[chat_id]["status"] != "running":
        return 

    game = GAMES[chat_id]
    current_holder = game["players"][game["holder_idx"]]

    if user.id != current_holder["id"]:
        return await update.message.reply_text("🙄 You don't have the bomb!")

    # Pass to next player
    game["holder_idx"] = (game["holder_idx"] + 1) % len(game["players"])
    new_holder = game["players"][game["holder_idx"]]
    
    await update.message.reply_text(f"🏃 <b>{html.escape(user.first_name)}</b> passed to <b>{html.escape(new_holder['name'])}</b>!")

# --- ⚙️ GAME ENGINE ---
async def run_game(update, context, chat_id):
    game = GAMES.get(chat_id)
    if not game: return

    if len(game["players"]) < 2:
        for p in game["players"]:
            users_collection.update_one({"user_id": p["id"]}, {"$inc": {"balance": game["fee"]}})
        del GAMES[chat_id]
        return await update.effective_chat.send_message("❌ Not enough players. Entry fees refunded.")

    game["status"] = "running"
    await update.effective_chat.send_message(f"🚀 <b>Game Started!</b> {len(game['players'])} players are in. Be quick!")

    while len(game["players"]) > 1:
        holder = game["players"][game["holder_idx"]]
        await update.effective_chat.send_message(f"💣 <b>{html.escape(holder['name'])}</b> has the bomb! Use <code>/pass</code>!")
        
        # Explosion logic: random time between 5-10s
        await asyncio.sleep(random.randint(5, 10))

        # 💥 BOOM!
        exploded = game["players"].pop(game["holder_idx"])
        await update.effective_chat.send_message(f"💥 <b>BOOM!</b> It exploded on <b>{html.escape(exploded['name'])}</b>! Out.")
        
        if len(game["players"]) > 0:
            game["holder_idx"] %= len(game["players"])

    # Winner Logic with Wins Tracking
    winner = game["players"][0]
    users_collection.update_one(
        {"user_id": winner["id"]}, 
        {"$inc": {"balance": game["pot"], "bomb_wins": 1}}
    )
    await update.effective_chat.send_message(
        f"🏆 <b>{stylize_text('WINNER')}!</b>\n"
        f"Congratulations <b>{html.escape(winner['name'])}</b>! Won <code>{format_money(game['pot'])}</code> and 1 Win point!"
    )
    del GAMES[chat_id]

# --- 🥇 BOMB RANKINGS ---
async def bomb_leaders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows top 10 bomb winners with medals."""
    top = users_collection.find({"bomb_wins": {"$gt": 0}}).sort("bomb_wins", -1).limit(10)
    msg = f"💣 <b>{stylize_text('BOMB GAME RANKINGS')}</b>\n━━━━━━━━━━━━━━━━━━\n"
    for i, u in enumerate(top, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🔹"
        msg += f"{medal} <b>{i}.</b> {html.escape(u.get('name', 'User'))} — <code>{u.get('bomb_wins', 0)} Wins</code>\n"
    await update.message.reply_text(msg + "━━━━━━━━━━━━━━━━━━", parse_mode=ParseMode.HTML)

async def bomb_myrank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check bomb stats for self or reply."""
    target = update.message.reply_to_message.from_user if update.message.reply_to_message else update.effective_user
    u = ensure_user_exists(target)
    wins = u.get('bomb_wins', 0)
    rank = users_collection.count_documents({"bomb_wins": {"$gt": wins}}) + 1
    await update.message.reply_text(
        f"💣 <b>{html.escape(target.first_name)}'s Stats</b>\n"
        f"🏆 Wins: <code>{wins}</code>\n"
        f"📊 Rank: <code>#{rank}</code>", 
        parse_mode=ParseMode.HTML
    )

async def bomb_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    chat_id = update.effective_chat.id
    if chat_id in GAMES:
        for p in GAMES[chat_id]["players"]:
            users_collection.update_one({"user_id": p["id"]}, {"$inc": {"balance": GAMES[chat_id]["fee"]}})
        del GAMES[chat_id]
        await update.message.reply_text("🛑 <b>Game Cancelled!</b> Fees refunded.")
