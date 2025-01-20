# Conversational Search Project

This is a **Conversational Search** application that combines:

- A **FastAPI** backend with OpenAI GPT-based conversational intelligence.
- **Meilisearch** for product search indexing.
- A **React** frontend that interacts with the backend for product queries and chat.
- An optional **Telegram Bot** for interacting with the same search engine via Telegram.

---

## Features

1. **Conversational Interface**
   - Chat with an AI assistant that can understand your intent.
   - If the user’s request implies a product search, the AI can trigger a search in Meilisearch.

2. **Product Search**
   - Built on [Meilisearch](https://www.meilisearch.com/) to provide fast, relevant product search.
   - Dynamically loaded from a local JSON file into Meilisearch when the container starts.

3. **React Frontend**
   - A user interface that allows you to **search** for products via text input and apply **filters** (price, size, category, etc.).
   - Real-time “chat” component for conversing with the AI.

4. **Telegram Bot**
   - Optionally, a Telegram bot that routes user messages to your FastAPI backend for chat and product queries.
   - The bot can return search results (including images) directly in Telegram.

---

## Prerequisites

- **Docker & Docker Compose** (for running the backend + Meilisearch).
- **Node.js & npm** (for running/building the frontend).
- (Optional) A **Telegram Bot token** (if you want to enable the Telegram bot).

---

## Project Structure
.
├── backend
│   ├── main.py               # FastAPI entry point
│   ├── Dockerfile            # Dockerfile for FastAPI app
│   ├── requirements.txt      # Python dependencies
│   ├── products.json         # Example product data loaded into Meilisearch
│   └── ...
├── conversational-search
│   ├── src
│   │   ├── components
│   │   │   ├── Chat.js
│   │   │   ├── Filters.js
│   │   │   ├── ProductList.js
│   │   │   └── SearchBar.js
│   │   └── ...
│   ├── package.json
│   └── ...
├── telegram_bot.py               # Telegram bot that interacts with the FastAPI backend
├── docker-compose.yml
├── .env                      # Environment variables (excluded from git)
├── README.md

# Getting Started

## 1. Clone the Repository

git clone https://github.com/yourusername/conversational-search.git
cd conversational-search

## 2. Environment Variables

Create a .env file in the root directory (alongside docker-compose.yml) with the following (example):

OPENAI_API_KEY=<Your OpenAI API Key>
MEILISEARCH_API_KEY=<Your Meilisearch Master Key>
TELEGRAM_BOT_TOKEN=<Your Telegram Bot Token>  # Only needed if using the Telegram bot

Note: Make sure not to commit your real .env to GitHub! Add .env to your .gitignore.
## 3. Build & Run with Docker Compose

# Build images
docker-compose build

# Start services
docker-compose up -d

This will spin up:

    Meilisearch on port 7700
    FastAPI backend (convsearch container) on port 8000

Check the logs:

docker-compose logs -f convsearch
docker-compose logs -f meilisearch

Once the backend finishes loading, you can access it at http://127.0.0.1:8000.
## 4. Using the Frontend (React)

npm install
npm start

By default, it will run at http://localhost:3000. The frontend calls the backend at http://127.0.0.1:8000 (see axios.post('http://127.0.0.1:8000/api/chat', ...) in the components). Adjust that URL if needed (e.g., if you deploy the backend separately).

## 5. Telegram Bot (Optional)

If you want to enable the Telegram bot:

    Edit telegram_bot/bot.py to ensure FASTAPI_CHAT_URL points to your FastAPI backend (e.g., http://127.0.0.1:8000/api/chat).
    Make sure your .env file has TELEGRAM_BOT_TOKEN set.
    Run the bot script locally (or dockerize it):
python3 telegram_bot.py

Then, open Telegram and start chatting with your bot!
How It Works

    FastAPI loads product data from products.json into Meilisearch on startup.
    The React frontend sends chat messages to POST /api/chat.
    When a user query implies a product search, the backend triggers client.index("products").search(query) to fetch results from Meilisearch.
    The Telegram Bot does the same thing from within Telegram—user messages are posted to /api/chat.
    If a search query is detected in the AI’s response, the user interface fetches and displays relevant products.

Configuration & Customization

    Proxy Settings: In docker-compose.yml, you might see HTTP_PROXY/HTTPS_PROXY if you are using a SOCKS proxy for the OpenAI API. Remove or adjust these if not needed.
    CORS: The backend includes CORSMiddleware to allow requests from http://localhost:3000. Change or add domains in the allow_origins if you deploy your frontend elsewhere.

# Deploying
Deploying the Backend

    You can deploy the Dockerized backend on services like Fly.io, Railway, Render, or Google Cloud Run.
    Ensure you either host Meilisearch externally or use a managed Meilisearch instance if your hosting platform doesn’t allow multiple containers.

Deploying the Frontend

    You can host the React build on Vercel, Netlify, GitHub Pages, or another static hosting provider.
    Update the API endpoint URLs in your React app to point to your deployed FastAPI backend.

Telegram Bot in Production

    If using the Telegram bot, you’ll need your backend to be publicly accessible so Telegram can send updates to it.
    Alternatively, you can use long polling if you keep the bot running on a server that can access your backend.
