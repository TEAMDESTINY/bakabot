async def stock_market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    group = groups_collection.find_one({"chat_id": chat.id}) or {"shares": 10.0}
    
    # Activity ke basis par price badhana (Logic)
    active_users = users_collection.count_documents({"last_chat_id": chat.id})
    current_price = group.get("shares", 10.0) + (active_users * 0.5)

    msg = (
        f"📈 <b>{stylize_text('STOCK MARKET')}</b>\n\n"
        f"🏢 <b>Group:</b> {chat.title}\n"
        f"💎 <b>Share Price:</b> <code>₹{current_price}</code>\n"
        f"📊 <b>Status:</b> {'Bullish 🚀' if active_users > 5 else 'Stable ⚖️'}\n\n"
        f"<i>Tip: Group mein baatein karo price badhane ke liye!</i>"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
