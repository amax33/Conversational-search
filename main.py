from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from meilisearch import Client
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import os
import logging
import uvicorn
import json
from typing import List
from dotenv import load_dotenv
# Load environment variables from .env
load_dotenv()

def load_products_to_meilisearch():
    index_name = "products"
    try:
        # Step 1: Check if index already exists
        idx = client.get_index(index_name)
        logger.info(f"Index '{index_name}' already exists. Skipping import.")
    except Exception:
        # If get_index fails, index doesn't exist. Create it with the correct primary key
        logger.info(f"Index '{index_name}' does not exist. Creating it with primary key='id'.")
        client.create_index(uid=index_name, options={"primaryKey": "id"})
        logger.info(f"Index '{index_name}' created.")

        # Now add your products
        try:
            logger.info(f"Importing data into index '{index_name}'.")
            with open("/app/products.json", "r") as f:
                products = json.load(f)
            client.index(index_name).add_documents(products)
            logger.info(f"Successfully imported products into index '{index_name}'.")
        except Exception as e:
            logger.error(f"Failed to load products: {e}")
            raise RuntimeError("Failed to load products into Meilisearch.")


# ----------------------------
# Configure Logging
# ----------------------------
# Load keys from environment variables
# Set environment variables (placeholders)
OPENAI_API_KEY = "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"

MEILISEARCH_API_KEY = "C0hyZwiDt1nJGF9nF7V75LVXa4GG4C5kuWSSTi4_pg8"

# Ensure the keys are loaded
if not OPENAI_API_KEY or not MEILISEARCH_API_KEY:
    raise RuntimeError("Missing required API keys.")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
# ----------------------------
# Initialize FastAPI App
# ----------------------------
app = FastAPI()

# ----------------------------
# Configure CORS Middleware
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update with your React app's origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# ----------------------------
# Initialize Meilisearch Client
# ----------------------------
try:
    client = Client(
        "http://meilisearch:7700",
        api_key=MEILISEARCH_API_KEY
    )
    logger.info("Successfully connected to Meilisearch.")
    # Load products into Meilisearch
    load_products_to_meilisearch()
except Exception as e:
    logger.error("Failed to connect to Meilisearch: %s", e)
    raise RuntimeError("Meilisearch initialization failed.")

# ----------------------------
# Initialize OpenAI LLM
# ----------------------------

try:
    llm = ChatOpenAI(
        temperature=0.7,
        openai_api_key=OPENAI_API_KEY,
        openai_proxy="socks5h://host.docker.internal:9090"  # Remove or update if not using a proxy
    )
    logger.info("Successfully initialized OpenAI LLM.")
except Exception as e:
    logger.error("Failed to initialize OpenAI LLM: %s", e)
    raise RuntimeError("OpenAI LLM initialization failed.")

# ----------------------------
# Define Pydantic Models
# ----------------------------
class Message(BaseModel):
    role: str  # "system", "user", or "assistant"
    content: str

class ChatRequest(BaseModel):
    conversation: List[Message]


# ----------------------------
# Search Endpoint
# ----------------------------
@app.get("/api/search")
async def search(query: str = ""):
    """
    Search endpoint to fetch products from Meilisearch.
    """
    logger.debug("Received search query: %s", query)
    try:
        if not query:
            # If no query is provided, return all products
            results = client.index("products").search('')
        else:
            results = client.index("products").search(query)
        logger.debug("Search results: %s", results)
        return {"hits": results["hits"], "query": query}
    except Exception as e:
        logger.error("Search failed: %s", e)
        raise HTTPException(status_code=500, detail="Search operation failed.")

# ----------------------------
# Chat Endpoint
# ----------------------------
@app.post("/api/chat")
async def chat(request: ChatRequest):
    conversation = request.conversation
    logger.debug("Received conversation: %s", conversation)

    # Define the system prompt to guide the assistant's behavior
    system_instructions = [
        SystemMessage(content=(
            "You are a helpful assistant connected to a product search engine.\n"
            "If the user mentions searching for products, respond with normal text.\n"
            "If you need to trigger a product search, include a line in your response:\n"
            "'search: <your search query here>'.\n"
            "For example: 'search: swimwear under 50'\n"
            "Otherwise, do not include 'search:' in your response."
        ))
    ]

    # Combine system instructions with the user's conversation
    formatted_conversation = system_instructions + [
        HumanMessage(content=msg.content) if msg.role.lower() == "user" else AIMessage(content=msg.content)
        for msg in conversation
    ]

    try:
        # Generate a response using OpenAI
        response = llm.invoke(formatted_conversation)
        llm_text = response.content
        logger.debug("LLM response: %s", llm_text)

        # Check if the response contains a search trigger
        if "search:" in llm_text.lower():
            search_query = extract_search_query(llm_text)
            logger.debug("Extracted search query from LLM response: %s", search_query)
            if search_query:
                search_results = client.index("products").search(search_query)
                formatted_results = format_search_results(search_results)
                return {
                    "response": llm_text,
                    "query": search_query,
                    "filteredResults": search_results["hits"]
                }
        return {"response": llm_text, "query": "", "filteredResults": []}
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

# ----------------------------
# Helper Functions
# ----------------------------
def extract_search_query(llm_response: str) -> str:
    """
    Extracts the search query from the LLM response.
    Expects a line starting with 'search:'.

    Example:
        Input: "Sure, here are some options.\nsearch: swimwear under 50"
        Output: "swimwear under 50"
    """
    try:
        lower_text = llm_response.lower()
        index = lower_text.index("search:")
        # Extract everything after 'search:'
        query = llm_response[index + len("search:"):].strip()
        # Optionally, extract up to the first newline if multiple lines exist
        query = query.split("\n")[0]
        logger.debug("Parsed search query: %s", query)
        return query
    except ValueError:
        logger.error("Failed to find 'search:' in LLM response.")
        return ""

def format_search_results(results) -> str:
    """
    Formats search results into a user-friendly string.

    Example:
        Input: List of product dictionaries
        Output: Formatted string listing products and their prices
    """
    try:
        hits = results["hits"]
        if not hits:
            return "No matching products found."
        formatted_results = "\n".join(
            [f"- {r['name']}: ${r['current_price']} {r['currency']}" for r in hits]
        )
        logger.debug("Formatted search results: %s", formatted_results)
        return formatted_results
    except Exception as e:
        logger.error("Failed to format search results: %s", e)
        return "Error formatting search results."

# ----------------------------
# Run the App
# ----------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug")

