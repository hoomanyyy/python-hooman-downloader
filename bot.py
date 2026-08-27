import os
import asyncio
import threading
import shutil

from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from tools.youtube import download_youtube_video
from tools.instagram import download_instagram_video
from server import app, create_download_link

import uvicorn


load_dotenv()


print("FFMPEG:", shutil.which("ffmpeg"))


TOKEN = os.getenv("API_TOKEN")

if not TOKEN:
    raise ValueError("API_TOKEN is not set")


# ---------------- SERVER ----------------

def run_server():

    port = int(os.environ.get("PORT", 8000))

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port
    )


# ---------------- BOT ----------------

application = Application.builder().token(TOKEN).build()



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["Tools", "Help"]
    ]

    markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "Hello and welcome to hooman-downloader 👋\n"
        "I can download videos from other platforms.",
        reply_markup=markup
    )



async def tools(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton(
                "🎥 Download YouTube",
                callback_data="youtube"
            ),

            InlineKeyboardButton(
                "📸 Download Instagram",
                callback_data="instagram"
            )
        ]
    ]

    await update.message.reply_text(
        "Choose a platform:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )



async def youtube_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    context.user_data["waiting_for_instagram"] = False
    context.user_data["waiting_for_youtube"] = True

    await query.message.reply_text(
        "🎥 Send YouTube URL:"
    )



async def instagram_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    context.user_data["waiting_for_youtube"] = False
    context.user_data["waiting_for_instagram"] = True

    await query.message.reply_text(
        "📸 Send Instagram URL:"
    )


async def download_url(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text.strip()

    if context.user_data.get("waiting_for_youtube"):

        context.user_data["waiting_for_youtube"] = False


        await update.message.reply_text(
            "⏳ Downloading YouTube..."
        )


        try:

            filename = await asyncio.to_thread(
                download_youtube_video,
                url
            )


            if not filename or not os.path.isfile(filename):
                raise Exception("File not created")


            size = os.path.getsize(filename) / (1024 * 1024)


            link = create_download_link(
                filename,
                expire_seconds=300
            )


            await update.message.reply_text(
                "✅ Download completed!\n\n"
                f"📦 Size: {size:.2f} MB\n\n"
                "🔗 Link:\n"
                f"{link}\n\n"
                "⏳ Expires in 5 minutes."
            )


        except Exception as e:

            await update.message.reply_text(
                f"❌ Error:\n{e}"
            )


    # -------- INSTAGRAM --------


    elif context.user_data.get("waiting_for_instagram"):

        context.user_data["waiting_for_instagram"] = False


        await update.message.reply_text(
            "⏳ Downloading Instagram..."
        )


        try:

            filename = await asyncio.to_thread(
                download_instagram_video,
                url
            )


            if not filename or not os.path.isfile(filename):
                raise Exception("File not created")


            size = os.path.getsize(filename) / (1024 * 1024)


            link = create_download_link(
                filename,
                expire_seconds=300
            )


            await update.message.reply_text(
                "✅ Download completed!\n\n"
                f"📦 Size: {size:.2f} MB\n\n"
                "🔗 Link:\n"
                f"{link}\n\n"
                "⏳ Expires in 5 minutes."
            )


        except Exception as e:

            await update.message.reply_text(
                f"❌ Error:\n{e}"
            )



async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Choose Tools and select a platform."
    )



# ---------------- HANDLERS ----------------


application.add_handler(
    CommandHandler(
        "start",
        start
    )
)


application.add_handler(
    MessageHandler(
        filters.Regex("^Tools$"),
        tools
    )
)


application.add_handler(
    MessageHandler(
        filters.Regex("^Help$"),
        help_command
    )
)


application.add_handler(
    CallbackQueryHandler(
        youtube_selected,
        pattern="^youtube$"
    )
)


application.add_handler(
    CallbackQueryHandler(
        instagram_selected,
        pattern="^instagram$"
    )
)


application.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        download_url
    )
)



# ---------------- RUN ----------------


if __name__ == "__main__":

    server_thread = threading.Thread(
        target=run_server,
        daemon=True
    )

    server_thread.start()


    print("File server is running...")
    print("Bot is running...")


    application.run_polling()