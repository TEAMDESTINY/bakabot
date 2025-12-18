# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Location: Supaul, Bihar 
# All rights reserved. @WTF_Phantom.

import html
import os
import sys
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from baka.config import OWNER_ID, UPSTREAM_REPO, GIT_TOKEN
from baka.utils import SUDO_USERS, get_mention, resolve_target, format_money, reload_sudoers, stylize_text
from baka.database import users_collection, sudoers_collection, groups_collection

# --- HELP PANEL ---
async def sudo_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in SUDO_USERS: return
    msg = (
        f"🔐 <b>{stylize_text('Sudo Panel')}</b>\n\n"
        f"<b>💰 {stylize_text('Economy')}:</b>\n"
        "‣ /addcoins [amt] [user]\n"
        "‣ /rmcoins [amt] [user]\n"
        "‣ /freerevive [user]\n"
        "‣ /unprotect [user] (Remove Shield)\n\n"
        f"<b>📢 {stylize_text('Broadcast')}:</b>\n"
        "‣ /broadcast -user (Reply)\n"
        "‣ /broadcast -group (Reply)\n\n"
        f"<b>👑 {stylize_text('Owner Only')}:</b>\n"
        "‣ /update (Pull Changes)\n"
        "‣ /addsudo [user]\n"
        "‣ /rmsudo [user]\n"
        "‣ /cleandb\n"
        "‣ /sudolist"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- UPDATER LOGIC ---
async def update_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if not UPSTREAM_REPO: return await update.message.reply_text("❌ <b>UPSTREAM_REPO</b> missing!", parse_mode=ParseMode.HTML)
    msg = await update.message.reply_text("🔄 <b>Checking for updates...</b>", parse_mode=ParseMode.HTML)
    try:
        import git
        try: repo = git.Repo()
        except: 
            repo = git.Repo.init()
            origin = repo.create_remote('origin', UPSTREAM_REPO)
            origin.fetch()
            repo.create_head('master', origin.refs.master).set_tracking_branch(origin.refs.master).checkout()
        
        repo_url = UPSTREAM_REPO
        if GIT_TOKEN and "github.com" in repo_url: 
            repo_url = repo_url.replace("https://", f"https://{GIT_TOKEN}@")
        
        repo.remotes.origin.set_url(repo_url)
        repo.remotes.origin.pull()
        await msg.edit_text("✅ <b>Update Found!</b>\nRestarting bot now... 🚀", parse_mode=ParseMode.HTML)
        os.execl(sys.executable, sys.executable, "Ryan.py")
    except Exception as e: 
        await msg.edit_text(f"❌ <b>Update Failed!</b>\nError: <code>{e}</code>", parse_mode=ParseMode.HTML)

# --- ADMIN ACTIONS ---
async def sudolist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in SUDO_USERS: return
    msg = f"👑 <b>{stylize_text('Owner & Sudoers')}:</b>\n\n"
    for uid in list(SUDO_USERS):
        u_doc = users_collection.find_one({"user_id": uid})
        role = "Owner" if uid == OWNER_ID else "Sudoer"
        msg += f"• {get_mention(u_doc) if u_doc else f'<code>{uid}</code>'} - {role}\n"
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- HANDLERS (With Confirmation) ---
async def addsudo(update, context):
    if update.effective_user.id != OWNER_ID: return
    target, err = await resolve_target(update, context)
    if not target: return await update.message.reply_text(err or "Usage: /addsudo <target>", parse_mode=ParseMode.HTML)
    await ask(update, f"Promote {get_mention(target)} to Sudo?", "addsudo", str(target['user_id']))

async def rmsudo(update, context):
    if update.effective_user.id != OWNER_ID: return
    target, err = await resolve_target(update, context)
    if not target: return await update.message.reply_text(err or "Usage: /rmsudo <target>", parse_mode=ParseMode.HTML)
    await ask(update, f"Demote {get_mention(target)} from Sudo?", "rmsudo", str(target['user_id']))

async def addcoins(update, context):
    if update.effective_user.id not in SUDO_USERS: return
    amount, target_str = parse_amount_and_target(context.args)
    if amount is None: return await update.message.reply_text("⚠️ Usage: <code>/addcoins 100 @user</code>", parse_mode=ParseMode.HTML)
    target, err = await resolve_target(update, context, specific_arg=target_str)
    if not target: return await update.message.reply_text(err or "⚠️ Target not found.", parse_mode=ParseMode.HTML)
    await ask(update, f"Give <b>{format_money(amount)}</b> to {get_mention(target)}?", "addcoins", f"{target['user_id']}|{amount}")

async def rmcoins(update, context):
    if update.effective_user.id not in SUDO_USERS: return
    amount, target_str = parse_amount_and_target(context.args)
    if amount is None: return await update.message.reply_text("⚠️ Usage: <code>/rmcoins 100 @user</code>", parse_mode=ParseMode.HTML)
    target, err = await resolve_target(update, context, specific_arg=target_str)
    if not target: return await update.message.reply_text(err or "⚠️ Target not found.", parse_mode=ParseMode.HTML)
    await ask(update, f"Remove <b>{format_money(amount)}</b> from {get_mention(target)}?", "rmcoins", f"{target['user_id']}|{amount}")

async def freerevive(update, context):
    if update.effective_user.id not in SUDO_USERS: return
    target, err = await resolve_target(update, context)
    if target: await ask(update, f"Free Revive {get_mention(target)}?", "freerevive", str(target['user_id']))

async def unprotect(update, context):
    if update.effective_user.id not in SUDO_USERS: return
    target, err = await resolve_target(update, context)
    if target: await ask(update, f"Remove 🛡️ from {get_mention(target)}?", "unprotect", str(target['user_id']))

async def cleandb(update, context):
    if update.effective_user.id != OWNER_ID: return
    await ask(update, "<b>WIPE DATABASE?</b> 🗑️", "cleandb", "0")

# --- UTILS ---
def parse_amount_and_target(args):
    amount = next((int(a) for a in args if a.isdigit()), None)
    target = next((a for a in args if not a.isdigit()), None)
    return amount, target

async def ask(update, text, act, arg):
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Yes", callback_data=f"cnf|{act}|{arg}"), 
        InlineKeyboardButton("❌ No", callback_data="cnf|cancel|0")
    ]])
    await update.message.reply_text(f"⚠️ <b>Wait!</b> {text}\nAre you sure?", parse_mode=ParseMode.HTML, reply_markup=kb)

# --- CALLBACK CONFIRMATION ---
async def confirm_handler(update, context):
    q = update.callback_query
    if q.from_user.id not in SUDO_USERS: return await q.answer("❌ Not for you!", show_alert=True)
    
    data = q.data.split("|")
    act = data[1]
    if act == "cancel": return await q.message.edit_text("❌ <b>Cancelled.</b>", parse_mode=ParseMode.HTML)

    try:
        if act == "addsudo":
            uid = int(data[2])
            sudoers_collection.update_one({"user_id": uid}, {"$set": {"user_id": uid}}, upsert=True)
            reload_sudoers()
            await q.message.edit_text(f"✅ User <code>{uid}</code> promoted.")
        elif act == "rmsudo":
            uid = int(data[2])
            sudoers_collection.delete_one({"user_id": uid})
            reload_sudoers()
            await q.message.edit_text(f"🗑️ User <code>{uid}</code> demoted.")
        elif act == "addcoins":
            uid, amt = int(data[2]), int(data[3])
            users_collection.update_one({"user_id": uid}, {"$inc": {"balance": amt}})
            await q.message.edit_text(f"✅ Added <b>{format_money(amt)}</b> to <code>{uid}</code>.", parse_mode=ParseMode.HTML)
        elif act == "rmcoins":
            uid, amt = int(data[2]), int(data[3])
            users_collection.update_one({"user_id": uid}, {"$inc": {"balance": -amt}})
            await q.message.edit_text(f"✅ Removed <b>{format_money(amt)}</b> from <code>{uid}</code>.", parse_mode=ParseMode.HTML)
        elif act == "freerevive":
            uid = int(data[2])
            users_collection.update_one({"user_id": uid}, {"$set": {"status": "alive", "death_time": None}})
            await q.message.edit_text(f"✅ User <code>{uid}</code> revived.")
        elif act == "unprotect":
            uid = int(data[2])
            users_collection.update_one({"user_id": uid}, {"$set": {"protection": None}}) 
            await q.message.edit_text(f"🛡️ Protection <b>REMOVED</b> from <code>{uid}</code>.", parse_mode=ParseMode.HTML)
        elif act == "cleandb":
            users_collection.delete_many({}); groups_collection.delete_many({})
            await q.message.edit_text("🗑️ <b>DATABASE WIPED!</b>")
    except Exception as e:
        await q.message.edit_text(f"❌ <b>Error:</b> <code>{e}</code>", parse_mode=ParseMode.HTML)
