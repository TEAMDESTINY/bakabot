# Copyright (c) 2025 Telegram:- @WTF_Phantom <DevixOP>
# Final Riddle Plugin - AI Integrated & Ryan.py Sync Fixed

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatType
from baka.plugins.chatbot import ask_mistral_raw
from baka.database import riddles_collection, users_collection
from baka.utils import format_money, ensure_user_exists, get_mention
from baka.config import RIDDLE_REWARD

# --- 🧠 START RIDDLE ---
async def riddle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Attribute fix for Ryan.py.
    Starts a new AI riddle in groups.
    """
    chat = update.effective_chat
    if chat.type == ChatType.PRIVATE: 
        return await update.message.reply_text("❌ Group Only!", parse_mode=ParseMode.HTML)

    # Check if a riddle is already active for this group
    if riddles_collection.find_one({"chat_id": chat.id}):
        return await update.message.reply_text("⚠️ A riddle is already active! Guess it.", parse_mode=ParseMode.HTML)

    msg = await update.message.reply_text("🧠 <b>Generating AI Riddle...</b>", parse_mode=ParseMode.HTML)

    # AI Prompt generation
    prompt = "Generate a short, hard riddle. Format: 'Riddle: [Question] | Answer: [OneWordAnswer]'. Do not add anything else."
    response = await ask_mistral_raw(system_prompt="You are a Riddle Master.", user_input=prompt)
    
    if not response or "|" not in response:
        return await msg.edit_text("⚠️ AI Brain Freeze. Try again.", parse_mode=ParseMode.HTML)

    try:
        parts = response.split("|")
        question = parts[0].replace("Riddle:", "").strip()
        answer_text = parts[1].replace("Answer:", "").strip().lower()
    except Exception:
        return await msg.edit_text("⚠️ AI Error during parsing.", parse_mode=ParseMode.HTML)

    # Save active riddle to database
    riddles_collection.insert_one({"chat_id": chat.id, "answer": answer_text})

    await msg.edit_text(
        f"🧩 <b>𝐀𝐈 𝐑𝐢𝐝𝐝𝐥𝐞 𝐂𝐡𝐚𝐥𝐥𝐞𝐧𝐠𝐞!</b>\n\n"
        f"<i>{question}</i>\n\n"
        f"💡 <b>Reward:</b> <code>{format_money(RIDDLE_REWARD)}</code>\n"
        f"👇 <i>Reply with your answer!</i>",
        parse_mode=ParseMode.HTML
    )

# --- 💡 CHECK ANSWER ---
async def check_riddle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Checks user messages for the correct answer.
    Should be called via a MessageHandler in Ryan.py.
    """
    if not update.message or not update.message.text: return
    chat = update.effective_chat
    text = update.message.text.strip().lower()

    # Find active riddle in this chat
    riddle_data = riddles_collection.find_one({"chat_id": chat.id})
    if not riddle_data: return

    if text == riddle_data['answer']:
        user = update.effective_user
        ensure_user_exists(user)
        
        # Reward winner and delete riddle
        users_collection.update_one({"user_id": user.id}, {"$inc": {"balance": RIDDLE_REWARD}})
        riddles_collection.delete_one({"chat_id": chat.id})
        
        await update.message.reply_text(
            f"🎉 <b>𝐂𝐨𝐫𝐫𝐞𝐜𝐭!</b>\n\n"
            f"👤 <b>Winner:</b> {get_mention(user)}\n"
            f"💰 <b>Won:</b> <code>{format_money(RIDDLE_REWARD)}</code>\n"
            f"🔑 <b>Answer:</b> <i>{riddle_data['answer'].title()}</i>",
            parse_mode=ParseMode.HTML
        )
