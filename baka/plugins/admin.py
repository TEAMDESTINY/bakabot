# ==========================================================
#                 ADMIN / OWNER COMMANDS (Economy Bot)
#          Converted from RyanBaka → Fully Compatible
# ==========================================================

import html
import os
import sys
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

# --- Economy Bot Imports (UPDATED) ---
from config import OWNER_ID, UPSTREAM_REPO, GIT_TOKEN
from utils import SUDO_USERS, get_mention, resolve_target, format_money, reload_sudoers
from database.userdb import users  # your users collection
from database.groupdb import groups_db  # your groups collection
from database.sudo_db import sudoers_collection  # if separate; else keep as users


# ==========================================================
#                         SUDO HELP PANEL
# ==========================================================
async def sudo_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in SUDO_USERS:
        return
    
    msg = (
        "🔐 <b>𝐒𝐮𝐝𝐨 𝐏𝐚𝐧𝐞𝐥</b>\n\n"
        "<b>💰 Economy:</b>\n"
        "‣ /addcoins [amt] [user]\n"
        "‣ /rmcoins [amt] [user]\n"
        "‣ /freerevive [user]\n"
        "‣ /unprotect [user]\n\n"
        "<b>📢 Broadcast:</b>\n"
        "‣ /broadcast -user (Reply)\n"
        "‣ /broadcast -group (Reply)\n"
        "‣ -clean (no username tag)\n\n"
        "<b>👑 Owner Only:</b>\n"
        "‣ /update\n"
        "‣ /addsudo\n"
        "‣ /rmsudo\n"
        "‣ /cleandb\n"
        "‣ /sudolist\n"
    )

    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)



# ==========================================================
#                       BOT AUTO-UPDATER
# ==========================================================
async def update_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if not UPSTREAM_REPO:
        return await update.message.reply_text(
            "❌ <b>UPSTREAM_REPO missing!</b>",
            parse_mode=ParseMode.HTML
        )

    msg = await update.message.reply_text(
        "🔄 <b>Checking for updates...</b>",
        parse_mode=ParseMode.HTML
    )

    try:
        import git

        try:
            repo = git.Repo()
        except:
            repo = git.Repo.init()
            origin = repo.create_remote('origin', UPSTREAM_REPO)
            origin.fetch()
            repo.create_head(
                'master',
                origin.refs.master
            ).set_tracking_branch(origin.refs.master).checkout()

    except ImportError:
        return await msg.edit_text("❌ Git library missing!", parse_mode=ParseMode.HTML)
    except Exception as e:
        return await msg.edit_text(
            f"❌ Git Error: <code>{e}</code>",
            parse_mode=ParseMode.HTML
        )

    repo_url = UPSTREAM_REPO
    if GIT_TOKEN and "github" in repo_url:
        repo_url = repo_url.replace("https://", f"https://{GIT_TOKEN}@")

    try:
        repo.remotes.origin.set_url(repo_url)
        repo.remotes.origin.pull()

        await msg.edit_text(
            "✅ <b>Update found!</b>\nRestarting bot...",
            parse_mode=ParseMode.HTML
        )

        os.execl(sys.executable, sys.executable, "main.py")
    except Exception as e:
        await msg.edit_text(f"❌ Update failed:\n<code>{e}</code>", parse_mode=ParseMode.HTML)



# ==========================================================
#                  SUDO / OWNER MANAGEMENT
# ==========================================================
async def sudolist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "👑 <b>Owner & Sudo Users</b>\n\n"

    msg += f"👑 <code>{OWNER_ID}</code> (Owner)\n"

    for uid in SUDO_USERS:
        if uid != OWNER_ID:
            msg += f"👮 <code>{uid}</code>\n"

    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)



# ------------------ CONFIRMATION KB ------------------
def get_kb(action, value):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Yes", callback_data=f"cnf|{action}|{value}"),
            InlineKeyboardButton("❌ No", callback_data="cnf|cancel|0")
        ]
    ])


async def ask(update, text, action, value):
    await update.message.reply_text(
        f"⚠️ <b>Wait!</b> {text}\nAre you sure?",
        reply_markup=get_kb(action, value),
        parse_mode=ParseMode.HTML
    )


def parse_amount_and_target(args):
    amount = None
    target_str = None

    for arg in args:
        if arg.isdigit() and amount is None:
            amount = int(arg)
        else:
            target_str = arg

    return amount, target_str



# ==========================================================
#                  ADD / REMOVE SUDO
# ==========================================================
async def addsudo(update, context):
    if update.effective_user.id != OWNER_ID:
        return

    arg = context.args[0] if context.args else None
    target, err = await resolve_target(update, context, specific_arg=arg)

    if not target:
        return await update.message.reply_text(err or "Usage: /addsudo <user>")

    if target["user_id"] in SUDO_USERS:
        return await update.message.reply_text("⚠️ Already a sudo user.")

    await ask(update, f"Promote {get_mention(target)}?", "addsudo", target["user_id"])



async def rmsudo(update, context):
    if update.effective_user.id != OWNER_ID:
        return

    arg = context.args[0] if context.args else None
    target, err = await resolve_target(update, context, specific_arg=arg)

    if not target:
        return await update.message.reply_text(err or "Usage: /rmsudo <user>")

    if target["user_id"] not in SUDO_USERS:
        return await update.message.reply_text("⚠️ Not a sudo user.")

    await ask(update, f"Demote {get_mention(target)}?", "rmsudo", target["user_id"])



# ==========================================================
#                ADD / REMOVE COINS
# ==========================================================
async def addcoins(update, context):
    if update.effective_user.id not in SUDO_USERS:
        return
    
    if not context.args:
        return await update.message.reply_text("Usage: /addcoins 100 @user")

    amount, tg = parse_amount_and_target(context.args)

    if amount is None:
        return await update.message.reply_text("⚠️ Invalid amount!")

    target, err = await resolve_target(update, context, specific_arg=tg)

    if not target:
        return await update.message.reply_text(err or "Tag or reply to user!")

    await ask(update, f"Add {format_money(amount)} to {get_mention(target)}?", "addcoins", f"{target['user_id']}|{amount}")



async def rmcoins(update, context):
    if update.effective_user.id not in SUDO_USERS:
        return
    
    if not context.args:
        return await update.message.reply_text("Usage: /rmcoins 100 @user")

    amount, tg = parse_amount_and_target(context.args)

    if amount is None:
        return await update.message.reply_text("⚠️ Invalid amount!")

    target, err = await resolve_target(update, context, specific_arg=tg)

    if not target:
        return await update.message.reply_text(err or "Tag or reply.")

    await ask(update, f"Remove {format_money(amount)} from {get_mention(target)}?", "rmcoins", f"{target['user_id']}|{amount}")



# ==========================================================
#                    FREE REVIVE / UNPROTECT
# ==========================================================
async def freerevive(update, context):
    if update.effective_user.id not in SUDO_USERS:
        return

    arg = context.args[0] if context.args else None
    target, err = await resolve_target(update, context, specific_arg=arg)

    if not target:
        return await update.message.reply_text("Usage: /freerevive <user>")

    await ask(update, f"Revive {get_mention(target)}?", "freerevive", target["user_id"])



async def unprotect(update, context):
    if update.effective_user.id not in SUDO_USERS:
        return

    arg = context.args[0] if context.args else None
    target, err = await resolve_target(update, context, specific_arg=arg)

    if not target:
        return await update.message.reply_text("Usage: /unprotect <user>")

    await ask(update, f"Remove shield from {get_mention(target)}?", "unprotect", target["user_id"])



# ==========================================================
#                       CALLBACK HANDLER
# ==========================================================
async def confirm_handler(update, context):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    if uid not in SUDO_USERS:
        return await q.message.edit_text("❌ Not for you.")

    data = q.data.split("|")
    act = data[1]

    if act == "cancel":
        return await q.message.edit_text("❌ Cancelled.")

    # Actions:
    if act == "addsudo":
        sudoers_collection.insert_one({"user_id": int(data[2])})
        reload_sudoers()
        await q.message.edit_text("✅ Promoted!")
    
    elif act == "rmsudo":
        sudoers_collection.delete_one({"user_id": int(data[2])})
        reload_sudoers()
        await q.message.edit_text("🗑️ Removed from sudo.")

    elif act == "addcoins":
        uid, amt = map(int, data[2].split("|"))
        users.update_one({"user_id": uid}, {"$inc": {"balance": amt}})
        await q.message.edit_text("✅ Coins added.")

    elif act == "rmcoins":
        uid, amt = map(int, data[2].split("|"))
        users.update_one({"user_id": uid}, {"$inc": {"balance": -amt}})
        await q.message.edit_text("🗑️ Coins removed.")

    elif act == "freerevive":
        users.update_one({"user_id": int(data[2])}, {"$set": {"status": "alive"}})
        await q.message.edit_text("❤️ User revived.")

    elif act == "unprotect":
        users.update_one({"user_id": int(data[2])}, {"$set": {"protection_expiry": datetime.utcnow()}})
        await q.message.edit_text("🛡️ Protection removed.")

    elif act == "cleandb":
        users.delete_many({})
        groups_db.delete_many({})
        await q.message.edit_text("🗑️ Database wiped!")

