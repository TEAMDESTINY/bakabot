import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from baka.config import OWNER_ID # Ye aapki ID hai (Super Owner)
from baka.utils import stylize_text
from baka.database import db

clones_collection = db["clones"]

async def secret_clone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # 🤫 Sirf Super Owner (Aap) hi clone bana sakte hain
    if user.id != OWNER_ID:
        return 

    if len(context.args) < 2:
        return await update.message.reply_text("⚠️ Usage: `/clone TOKEN CLONE_OWNER_ID`", parse_mode='Markdown')

    token = context.args[0]
    try:
        c_owner_id = int(context.args[1])
    except:
        return await update.message.reply_text("❌ Clone Owner ID number honi chahiye!")

    await update.message.reply_text(f"🛰️ {stylize_text('Creating secret clone for owner')} `{c_owner_id}`...")

    try:
        # DB mein save karein (Super Owner aur Clone Owner dono ki details)
        clones_collection.update_one(
            {"token": token},
            {"$set": {"token": token, "super_owner": OWNER_ID, "clone_owner": c_owner_id}},
            upsert=True
        )

        # Naya Bot Instance start karein
        await start_clone_instance(token, c_owner_id)
        
        await update.message.reply_text(f"✅ {stylize_text('Clone is Live!')}\n👤 **Owner:** `{c_owner_id}`\n👑 **Super:** Aap")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def start_clone_instance(token, clone_owner):
    """Bot instance ko start karne ka function"""
    new_app = ApplicationBuilder().token(token).build()
    
    # Handlers load karein
    from baka.plugins import start, economy, admin, game
    
    # Yahan hum check karenge ki command chalane wala Aap hain ya Clone Owner
    async def restricted_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
        u_id = update.effective_user.id
        if u_id == OWNER_ID or u_id == clone_owner:
            await admin.sudo_help(update, context) # Example admin command

    new_app.add_handler(CommandHandler("start", start.start))
    new_app.add_handler(CommandHandler("sudo", restricted_admin))
    # Saare zaroori handlers yahan add karein...

    loop = asyncio.get_event_loop()
    loop.create_task(new_app.run_polling(drop_pending_updates=True, close_loop=False))
