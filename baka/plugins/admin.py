# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Location: Bihar | All rights reserved.
# Final Admin & Sudo Plugin for Destiny Bot

import html
import os
import sys
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import OWNER_ID, UPSTREAM_REPO, GIT_TOKEN
from baka.utils import SUDO_USERS, get_mention, resolve_target, format_money, reload_sudoers, stylize_text
from baka.database import users_collection, sudoers_collection, groups_collection, reset_daily_activity, reset_weekly_activity

# --- HELP PANEL ---
async def sudo_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in SUDO_USERS: return
    msg = (
        "🔐 <b>𝐒𝐮𝐝𝐨 𝐏𝐚𝐧𝐞𝐥</b>\n\n"
        "<b>💰 Economy:</b>\n"
        "‣ /addcoins [amt] [user]\n"
        "‣ /rmcoins [amt] [user]\n"
        "‣ /freerevive [user]\n"
        "‣ /unprotect [user] (Remove Shield)\n\n"
        "<b>🏆 Competition:</b>\n"
        "‣ /resetstats daily (Clear Today)\n"
        "‣ /resetstats weekly (Clear Week)\n\n"
        "<b>👑 𝐎𝐰𝐧𝐞𝐫 𝐎𝐧𝐥𝐲:</b>\n"
        "‣ /update (Pull Changes)\n"
        "‣ /addsudo [user] | /rmsudo [user]\n"
        "‣ /cleandb (Wipe All)\n"
        "‣ /sudolist"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- LEADERBOARD RESET LOGIC ---
async def reset_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("❌ <b>Owner only command!</b>", parse_mode=ParseMode.HTML)

    if not context.args:
        return await update.message.reply_text("⚠️ Use: <code>/resetstats daily</code> or <code>weekly</code>")

    mode = context.args[0].lower()
    if mode == "daily":
        reset_daily_activity()
        await update.message.reply_text(f"✨ {stylize_text('DAILY STATS RESET')}\nCompetition restarted!")
    elif mode == "weekly":
        reset_weekly_activity()
        await update.message.reply_text(f"👑 {stylize_text('WEEKLY STATS RESET')}\nNew week, new winner!")

# --- UPDATER ---
async def update_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if not UPSTREAM_REPO: return await update.message.reply_text("❌ <b>UPSTREAM_REPO</b> missing!")
    
    msg = await update.message.reply_text("🔄 <b>Checking for updates...</b>", parse_mode=ParseMode.HTML)
    try:
        import git
        repo = git.Repo() if os.path.exists('.git') else git.Repo.init()
        repo.remotes.origin.pull()
        await msg.edit_text("✅ <b>Update Successful!</b> Restarting... 🚀")
        os.execl(sys.executable, sys.executable, "Ryan.py")
    except Exception as e:
        await msg.edit_text(f"❌ <b>Error:</b> <code>{e}</code>", parse_mode=ParseMode.HTML)

# --- SUDO MANAGEMENT ---
async def sudolist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "👑 <b>𝐎𝐰𝐧𝐞𝐫 & 𝐒𝐮𝐝𝐨𝐞𝐫𝐬:</b>\n\n"
    for uid in SUDO_USERS:
        u_doc = users_collection.find_one({"user_id": uid})
        role = "Owner" if uid == OWNER_ID else "Sudoer"
        name = get_mention(u_doc) if u_doc else f"<code>{uid}</code>"
        msg += f"• {name} ({role})\n"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- HANDLERS WITH CONFIRMATION ---
async def addcoins(update, context):
    if update.effective_user.id not in SUDO_USERS: return
    if len(context.args) < 1: return
    amount, target_str = parse_amount_and_target(context.args)
    target, err = await resolve_target(update, context, specific_arg=target_str)
    if target: await ask(update, f"Add {format_money(amount)} to {get_mention(target)}?", "addcoins", f"{target['user_id']}|{amount}")

async def rmcoins(update, context):
    if update.effective_user.id not in SUDO_USERS: return
    amount, target_str = parse_amount_and_target(context.args)
    target, err = await resolve_target(update, context, specific_arg=target_str)
    if target: await ask(update, f"Remove {format_money(amount)} from {get_mention(target)}?", "rmcoins", f"{target['user_id']}|{amount}")

async def addsudo(update, context):
    if update.effective_user.id != OWNER_ID: return
    target, err = await resolve_target(update, context)
    if target: await ask(update, f"Promote {get_mention(target)}?", "addsudo", str(target['user_id']))

async def rmsudo(update, context):
    if update.effective_user.id != OWNER_ID: return
    target, err = await resolve_target(update, context)
    if target: await ask(update, f"Demote {get_mention(target)}?", "rmsudo", str(target['user_id']))

async def freerevive(update, context):
    if update.effective_user.id not in SUDO_USERS: return
    target, err = await resolve_target(update, context)
    if target: await ask(update, f"Revive {get_mention(target)}?", "freerevive", str(target['user_id']))

async def unprotect(update, context):
    if update.effective_user.id not in SUDO_USERS: return
    target, err = await resolve_target(update, context)
    if target: await ask(update, f"Remove 🛡️ from {get_mention(target)}?", "unprotect", str(target['user_id']))

async def cleandb(update, context):
    if update.effective_user.id != OWNER_ID: return
    await ask(update, "<b>WIPE ALL DATABASE?</b> 🗑️", "cleandb", "0")

# --- UTILS & CALLBACK ---
def parse_amount_and_target(args):
    amount = next((int(a) for a in args if a.isdigit()), 0)
    target = next((a for a in args if not a.isdigit()), None)
    return amount, target

async def ask(update, text, act, arg):
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ 𝐘𝐞𝐬", callback_data=f"cnf|{act}|{arg}"),
        InlineKeyboardButton("❌ 𝐍𝐨", callback_data="cnf|cancel|0")
    ]])
    await update.message.reply_text(f"⚠️ {text}", reply_markup=kb, parse_mode=ParseMode.HTML)

async def confirm_handler(update, context):
    q = update.callback_query
    if q.from_user.id not in SUDO_USERS: return await q.answer("❌ Not for you!", show_alert=True)
    
    data = q.data.split("|")
    act, arg = data[1], data[2]
    if act == "cancel": return await q.message.edit_text("❌ Action Cancelled.")

    if act == "addcoins":
        uid, amt = int(arg), int(data[3])
        users_collection.update_one({"user_id": uid}, {"$inc": {"balance": amt}})
        await q.message.edit_text(f"✅ Added {format_money(amt)} to <code>{uid}</code>.")
    elif act == "rmcoins":
        uid, amt = int(arg), int(data[3])
        users_collection.update_one({"user_id": uid}, {"$inc": {"balance": -amt}})
        await q.message.edit_text(f"✅ Removed {format_money(amt)} from <code>{uid}</code>.")
    elif act == "addsudo":
        sudoers_collection.insert_one({"user_id": int(arg)})
        reload_sudoers()
        await q.message.edit_text(f"✅ <code>{arg}</code> is now Sudoer.")
    elif act == "rmsudo":
        sudoers_collection.delete_one({"user_id": int(arg)})
        reload_sudoers()
        await q.message.edit_text(f"🗑️ <code>{arg}</code> removed from Sudo.")
    elif act == "freerevive":
        users_collection.update_one({"user_id": int(arg)}, {"$set": {"status": "alive", "death_time": None}})
        await q.message.edit_text(f"✅ <code>{arg}</code> Revived.")
    elif act == "unprotect":
        users_collection.update_one({"user_id": int(arg)}, {"$set": {"protection_expiry": datetime.utcnow()}})
        await q.message.edit_text(f"🛡️ Shield Removed for <code>{arg}</code>.")
    elif act == "cleandb":
        users_collection.delete_many({}); groups_collection.delete_many({})
        await q.message.edit_text("🗑️ <b>DATABASE WIPED!</b>")
