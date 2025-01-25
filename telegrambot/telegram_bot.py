from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import logging
import os
import requests
from telegram.request import HTTPXRequest
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Proxy Configuration (Optional)
# -------------------------------------------------------------------
# If you have a SOCKS proxy on your host at 127.0.0.1:9090, from inside Docker
# you'll need "host.docker.internal:9090" + 'extra_hosts' in docker-compose.
PROXY = "socks5h://host.docker.internal:9090"

os.environ["HTTP_PROXY"] = PROXY
os.environ["HTTPS_PROXY"] = PROXY

# telegram-ptb uses HTTPX. Use `proxy=` (not proxy_url=).
httpx_request = HTTPXRequest(
    http_version="1.1",
    proxy=PROXY
)

# -------------------------------------------------------------------
# Environment Variables
# -------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# If this container is in the same docker-compose network as 'convsearch',
# use the service name "convsearch" + port 8000
FASTAPI_CHAT_URL = "http://convsearch:8000/api/chat"

# -------------------------------------------------------------------
# Conversation Storage
# -------------------------------------------------------------------
user_conversations = {}

# -------------------------------------------------------------------
# Handlers
# -------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user_conversations[chat_id] = []
    await update.message.reply_text("Hi! I'm your product search assistant. How can I help you today?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user_message = update.message.text

    if chat_id not in user_conversations:
        user_conversations[chat_id] = []

    user_conversations[chat_id].append({"role": "user", "content": user_message})

    try:
        # Post to the FastAPI backend
        response = requests.post(
            FASTAPI_CHAT_URL,
            json={"conversation": user_conversations[chat_id]},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            bot_response = data.get("response", "Sorry, I didn't understand that.")
            filtered_results = data.get("filteredResults", [])[:5]

            user_conversations[chat_id].append({"role": "assistant", "content": bot_response})
            await update.message.reply_text(bot_response)

            # If there's product data, send images or text
            if filtered_results:
                for product in filtered_results:
                    name = product.get("name", "No Name")
                    price = product.get("current_price", "Unknown Price")
                    currency = product.get("currency", "Unknown Currency")
                    description = product.get("description", "No description available.")
                    images = product.get("images", [])

                    caption = f"*{name}*\nPrice: {price} {currency}\n{description}"
                    if len(caption) > 1024:
                        caption = caption[:1020] + "..."

                    if images:
                        try:
                            await context.bot.send_photo(
                                chat_id=chat_id,
                                photo=images[0],
                                caption=caption,
                                parse_mode="Markdown"
                            )
                        except Exception as e:
                            logger.error("Error sending photo: %s", e)
                            await update.message.reply_text(
                                f"{name}\nPrice: {price} {currency}\n{description}"
                            )
                    else:
                        await update.message.reply_text(
                            f"{name}\nPrice: {price} {currency}\n{description}"
                        )
        else:
            logger.error("Backend error: %s", response.text)
            await update.message.reply_text("Sorry, something went wrong on the server.")
    except Exception as e:
        logger.error("Error sending message to backend: %s", e)
        await update.message.reply_text("Sorry, something went wrong.")

def main():
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found. Please set it in .env or environment.")
        return

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).request(httpx_request).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == "__main__":
    main()

