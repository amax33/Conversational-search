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

# ----------------------------
# Configure Logging
# ----------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ----------------------------
# Proxy Configuration
# ----------------------------
PROXY_URL = "socks5h://127.0.0.1:9090"

# Set proxy globally for Requests
os.environ["HTTP_PROXY"] = PROXY_URL
os.environ["HTTPS_PROXY"] = PROXY_URL

# ----------------------------
# Configure HTTPXRequest for Telegram Bot
# ----------------------------
httpx_request = HTTPXRequest(
    http_version="1.1",  # Ensure HTTP/1.1 is used
    proxy_url=PROXY_URL  # Use the proxy for all Telegram API calls
)

# ----------------------------
# Constants
# ----------------------------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
FASTAPI_CHAT_URL = "http://127.0.0.1:8000/api/chat"  # Update with your FastAPI chat endpoint

# ----------------------------
# Conversation Storage
# ----------------------------
# Dictionary to store conversation history per user
user_conversations = {}

# ----------------------------
# Handlers
# ----------------------------

# Start Command Handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for the /start command.
    Sends a welcome message to the user.
    """
    chat_id = update.message.chat_id
    user_conversations[chat_id] = []  # Initialize conversation history for the user
    await update.message.reply_text("Hi! I'm your product search assistant. How can I help you today?")

# Handle User Messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user_message = update.message.text

    # Initialize conversation history if not already done
    if chat_id not in user_conversations:
        user_conversations[chat_id] = []

    # Add the user's message to the conversation history
    user_conversations[chat_id].append({"role": "user", "content": user_message})

    # Send user message to FastAPI backend
    try:
        response = requests.post(
            FASTAPI_CHAT_URL,
            json={"conversation": user_conversations[chat_id]},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            bot_response = data.get("response", "Sorry, I didn't understand that.")
            filtered_results = data.get("filteredResults", [])
            # Limit to the first 5 results
            filtered_results = filtered_results[:5]

            # Add the assistant's message to the conversation history
            user_conversations[chat_id].append({"role": "assistant", "content": bot_response})

            # Send bot response
            await update.message.reply_text(bot_response)

            # Send product images with captions if available
            if filtered_results:
                for product in filtered_results:
                    name = product.get("name", "No Name")
                    price = product.get("current_price", "Unknown Price")
                    currency = product.get("currency", "Unknown Currency")
                    description = product.get("description", "No description available.")
                    images = product.get("images", [])
                    
                    # Caption for the image
                    caption = f"*{name}*\nPrice: {price} {currency}\n{description}"
                    
                    # Truncate caption if it exceeds 1024 characters
                    if len(caption) > 1024:
                        caption = caption[:1020] + "..."
                    
                    # Send the first image if available
                    if images:
                        try:
                            await context.bot.send_photo(
                                chat_id=chat_id,
                                photo=images[0],  # Send the first image
                                caption=caption,
                                parse_mode="Markdown"
                            )
                        except Exception as e:
                            logger.error("Error sending photo: %s", e)
                            await update.message.reply_text(
                                f"{name}\nPrice: {price} {currency}\n{description}"
                            )
                    else:
                        # Send text if no image is available
                        await update.message.reply_text(
                            f"{name}\nPrice: {price} {currency}\n{description}"
                        )
        else:
            logger.error("Backend error: %s", response.text)
            await update.message.reply_text("Sorry, something went wrong on the server.")
    except Exception as e:
        logger.error("Error sending message to backend: %s", e)
        await update.message.reply_text("Sorry, something went wrong.")

# ----------------------------
# Main Function
# ----------------------------
def main():
    """
    Main function to initialize and start the Telegram bot.
    """
    # Initialize the bot application
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).request(httpx_request).build()

    # Add command and message handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot
    application.run_polling()

# ----------------------------
# Entry Point
# ----------------------------
if __name__ == "__main__":
    main()

