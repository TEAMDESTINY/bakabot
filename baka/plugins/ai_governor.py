async def ai_governor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    # AI se group ki economy par comment karwana
    prompt = f"Write a short, funny economic report for the group '{chat.title}' as a strict Governor."
    report = await ask_mistral_raw("Governor", prompt)
    
    await update.message.reply_text(f"🏛️ <b>{stylize_text('GOVERNOR REPORT')}</b>\n\n{report}", parse_mode=ParseMode.HTML)
