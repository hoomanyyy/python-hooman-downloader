import os
import asyncio
import threading

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

TOKEN = os.getenv("API_TOKEN")

if not TOKEN:
    raise ValueError("API_TOKEN is not set in .env")


def run_server():

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )


application = Application.builder().token(TOKEN).build()


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    print("CHAT ID:", update.effective_chat.id)

    keyboard = [
        ["Tools", "Help"]
    ]

    markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "Hello and welcome to 'hooman-downloader' bot 👋\n"
        "I will download videos for you from other platforms.",
        reply_markup=markup
    )


async def tools(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

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

    markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Choose a platform:",
        reply_markup=markup
    )


async def youtube_selected(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    context.user_data["waiting_for_youtube"] = True

    await query.message.reply_text(
        "🎥 Please send the YouTube video URL:"
    )


async def instagram_selected(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    context.user_data["waiting_for_instagram"] = True

    await query.message.reply_text(
        "📸 Please send the Instagram URL:"
    )

async def instagram_url_download(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    if not context.user_data.get("waiting_for_instagram"):
        return None
    
    url = update.message.text.strip()
    print(f"instagram video url: {url}")

    await update.message.reply_text(
        "Downloading ⏳⏳"
    )

    try:
    
        filename = download_instagram_video(url)
        print(f"filename: {filename}")

        if not os.path.exists(filename):
            return "file not found"
        
        size = os.path.getsize(filename) / (1024 * 1024)
        print(
            f"File size: {size:.2f} MB"
        )

        download_link = create_download_link(
            filename=filename,
            expire_seconds=300
        )

        print(f"download link: {download_link}")

        await update.message.reply_text(
            "✅ Download completed!\n\n"
            f"📦 Size: {size:.2f} MB\n\n"
            "🔗 Download link:\n"
            f"{download_link}\n\n"
            "⏳ This link will expire in 5 minutes."
        )

    except Exception as e:
        print(f"error: {e}")

async def youtube_url_download(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not context.user_data.get("waiting_for_youtube"):
        return

    url = update.message.text.strip()

    context.user_data["waiting_for_youtube"] = False

    print(f"YouTube URL: {url}")

    filename = None

    await update.message.reply_text(
        "⏳ Downloading..."
    )

    try:

        filename = await asyncio.to_thread(
            download_youtube_video,
            url
        )

        print(f"YouTube filename: {filename}")

        if not filename:
            raise Exception(
                "download_youtube_video returned None"
            )

        if not os.path.isfile(filename):
            raise FileNotFoundError(
                f"File not found: {filename}"
            )

        size_mb = (
            os.path.getsize(filename)
            / (1024 * 1024)
        )

        print(
            f"File size: {size_mb:.2f} MB"
        )

        download_url = create_download_link(
            filename,
            expire_seconds=300
        )

        print(
            f"Download URL: {download_url}"
        )

        await update.message.reply_text(
            "✅ Download completed!\n\n"
            f"📦 Size: {size_mb:.2f} MB\n\n"
            "🔗 Download link:\n"
            f"{download_url}\n\n"
            "⏳ This link will expire in 5 minutes."
        )

        filename = None

    except Exception as e:

        print(
            f"Error: {type(e).__name__}: {e}"
        )

        await update.message.reply_text(
            "❌ Error:\n"
            f"{type(e).__name__}: {e}"
        )

        if filename and os.path.isfile(filename):

            try:
                os.remove(filename)
            except Exception:
                pass


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "ℹ️ Send me a YouTube URL and I will download it."
    )


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
        youtube_url_download
    )
)
    
application.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        instagram_url_download
    )
)

application.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        youtube_url_download
    )
)

if __name__ == "__main__":

    server_thread = threading.Thread(
        target=run_server,
        daemon=True
    )

    server_thread.start()

    print("File server is running...")
    print("Bot is running...")

    application.run_polling()