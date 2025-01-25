# Conversational Search Project

This is a **Conversational Search** application that combines:

- A **FastAPI** backend with OpenAI GPT-based conversational intelligence.
- **Meilisearch** for product search indexing.
- A **React** frontend that interacts with the backend for product queries and chat.
- A **Telegram Bot** for interacting with the search engine via Telegram.

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
   - A Telegram bot that routes user messages to your FastAPI backend for chat and product queries.
   - The bot can return search results (including images) directly in Telegram.

---

## Prerequisites

- Docker & Docker Compose (for running the backend, frontend, and Meilisearch).
- Optional: A Telegram Bot token (if you want to enable the Telegram bot).

---

## Getting Started

### Clone the Repository

git clone https://github.com/yourusername/conversational-search.git  
cd conversational-search

---

### Environment Variables

Create a `.env` file in the root directory (alongside `docker-compose.yml`) with the following:

OPENAI_API_KEY=<Your OpenAI API Key>  
MEILISEARCH_API_KEY=<Your Meilisearch Master Key>  
TELEGRAM_BOT_TOKEN=<Your Telegram Bot Token> (Only needed if using the Telegram bot)

Make sure not to commit your real `.env` to GitHub by adding it to `.gitignore`.

---

### Build and Run with Docker Compose

Build and start all services (FastAPI backend, Meilisearch, Telegram bot, and React frontend):

docker-compose build  
docker-compose up -d  

This will spin up:

- Meilisearch on port 7700
- FastAPI backend on port 8000
- React frontend on port 3000
- Telegram bot (if enabled) running in the container

To check the logs:

docker-compose logs -f convsearch  
docker-compose logs -f meilisearch  
docker-compose logs -f frontend  
docker-compose logs -f telegram-bot  

Once the services are running, you can access them at:

- Backend: http://127.0.0.1:8000
- Frontend: http://localhost:3000

---

### Telegram Bot (Optional)

If you want to enable the Telegram bot:

1. Make sure your `.env` file has `TELEGRAM_BOT_TOKEN` set.  
2. Edit `telegram_bot/telegram_bot.py` to ensure `FASTAPI_CHAT_URL` points to your FastAPI backend (e.g., http://127.0.0.1:8000/api/chat).  
3. The bot runs automatically as part of `docker-compose`.  

Open Telegram, search for your bot, and start chatting!

---

## How It Works

1. FastAPI Backend:
   - Loads product data from `products.json` into Meilisearch on startup.
   - Handles chat messages via POST `/api/chat` and integrates AI + Meilisearch.

2. React Frontend:
   - Sends chat messages to the backend and displays responses.
   - Fetches and displays search results when a query implies a product search.

3. Telegram Bot:
   - Relays messages from Telegram to `/api/chat` in the FastAPI backend.
   - Displays search results (including images) directly in Telegram.

---

## Configuration and Customization

1. Proxy Settings: In `docker-compose.yml`, HTTP_PROXY/HTTPS_PROXY can be configured if using a SOCKS proxy for the OpenAI API. Remove or adjust these if not needed.
2. CORS: The backend includes CORSMiddleware to allow requests from http://localhost:3000. Change or add domains in the `allow_origins` if you deploy your frontend elsewhere.

---

## Deploying

### Deploying the Backend

- Deploy the Dockerized backend on services like Fly.io, Railway, Render, or Google Cloud Run.
- Ensure you either host Meilisearch externally or use a managed Meilisearch instance if your hosting platform doesn’t allow multiple containers.

### Deploying the Frontend

- Host the React build on Vercel, Netlify, GitHub Pages, or another static hosting provider.
- Update the API endpoint URLs in your React app to point to your deployed FastAPI backend.

### Telegram Bot in Production

- If using the Telegram bot, you’ll need your backend to be publicly accessible so Telegram can send updates to it.
- Alternatively, use long polling if you keep the bot running on a server that can access your backend.
