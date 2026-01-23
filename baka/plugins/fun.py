from telegram import Update
from telegram.ext import ContextTypes
import random

# ---------------- BASIC ---------------- #

async def brain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 Brain activated.")

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"👤 Your ID: `{user.id}`", parse_mode="Markdown")

# ---------------- GAMES ---------------- #

async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_dice()

async def slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_dice(emoji="🎰")

# ---------------- ACTIONS ---------------- #

async def slap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤚 Slap!")

async def punch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👊 Punch!")

async def hug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤗 Hug!")

async def kiss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("😘 Kiss!")

# ---------------- FUN ---------------- #

async def roast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    roasts = [
        "Tu smart hota agar dimaag optional hota.",
        "Tu background character bhi nahi lagta.",
        "Confidence strong hai, talent missing."
    ]
    await update.message.reply_text(random.choice(roasts))

async def shayari(update: Update, context: ContextTypes.DEFAULT_TYPE):
    shayari_list = [
        "Dil se padho to baat samajh aati hai ❤️",
        "Zindagi ek exam hai, pass hona zaruri hai ✨",
        "Waqt badalta hai, bas rukna mat ⏳"
    ]
    await update.message.reply_text(random.choice(shayari_list))

# ---------------- ANIME REACTIONS ---------------- #

async def anime_react(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✨ Anime reaction!")
