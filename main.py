from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from meilisearch import Client
import os
import logging
import uvicorn

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Allow CORS from React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update with the React app's origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Set proxy for OpenAI requests
os.environ["HTTP_PROXY"] = "socks5h://127.0.0.1:9090"
os.environ["HTTPS_PROXY"] = "socks5h://127.0.0.1:9090"

# Initialize Meilisearch client
try:
    client = Client("http://127.0.0.1:7700", api_key="lC6iJId0aC0CGKAFUEPDejWcs6Khy-YzoXDxqLpm8R4")
    logger.info("Successfully connected to Meilisearch.")
except Exception as e:
    logger.error("Failed to connect to Meilisearch: %s", e)
    raise RuntimeError("Meilisearch initialization failed.")

# Search endpoint
@app.get("/api/search")
async def search(query: str = ""):
    """
    Search endpoint to fetch products from Meilisearch.
    """
    logger.debug("Received search query: %s", query)
    try:
        results = client.index("products").search(query)
        logger.debug("Search results: %s", results)
        return {"hits": results["hits"], "query": query}
    except Exception as e:
        logger.error("Search failed: %s", e)
        raise HTTPException(status_code=500, detail="Search operation failed.")

# Run the app (debugging enabled)
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug")

