import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv
from brave_api import fetch_articles_from_brave
from openai_api import generate_twitter_drafts
from supabase_utils import log_message_to_supabase


# Load environment variables from .env file
load_dotenv()

# Fetch credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Ensure Supabase credentials are available
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase URL or API Key in environment variables!")

# Initialize Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    raise ValueError(f"Failed to initialize Supabase client: {e}")

# Initialize FastAPI app
app = FastAPI()


# Models
class MessageRequest(BaseModel):
    session_id: str
    content: str


# Endpoints
@app.get("/")
async def root():
    return {"message": "AI Agent is running with environment variables!"}


@app.get("/test-env")
async def test_env():
    return {
        "supabase_url": SUPABASE_URL,
        "supabase_key": "Loaded" if SUPABASE_KEY else "Not Loaded",
        "openai_api_key": "Loaded" if os.getenv("OPENAI_API_KEY") else "Not Loaded",
        "brave_api_key": "Loaded" if os.getenv("BRAVE_API_KEY") else "Not Loaded",
    }


@app.get("/test-supabase")
async def test_supabase():
    try:
        # Test fetching data from Supabase (assuming the "messages" table exists)
        response = supabase.table("messages").select("*").limit(1).execute()
        return {"status": "Connected to Supabase", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Supabase: {e}")


@app.post("/store-message")
async def store_message(request: MessageRequest):
    """
    Store a message in the Supabase `messages` table.
    """
    try:
        message_data = {
            "type": "human",  # Indicating this is a user message
            "content": request.content,
        }
        # Insert into Supabase
        supabase.table("messages").insert({
            "session_id": request.session_id,
            "message": json.dumps(message_data),
        }).execute()
        return {"status": "Message stored successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing message: {e}")


@app.get("/fetch-messages/{session_id}")
async def fetch_messages(session_id: str):
    """
    Fetch all messages for a given session_id.
    """
    try:
        # Query Supabase for messages with the given session_id
        response = supabase.table("messages").select("*").eq("session_id", session_id).order("created_at").execute()
        return {"status": "Messages fetched successfully!", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching messages: {e}")

@app.get("/search-articles")
async def search_articles(query: str = "default search"):
    """
    Search for articles using the Brave API.

    Args:
        query (str): The search query.

    Returns:
        dict: A list of articles related to the query.
    """
    try:
        articles = fetch_articles_from_brave(query)
        
        # Ensure we have a list of articles
        if not isinstance(articles, list):
            articles = [articles] if articles else []
            
        # Return the response
        if not articles:
            return {
                "status": "No results found",
                "data": []
            }
            
        return {
            "status": "Articles fetched successfully!",
            "data": articles
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error in search_articles: {str(e)}")  # Debug log
        raise HTTPException(status_code=500, detail=f"Failed to fetch articles: {str(e)}")

@app.get("/generate-twitter-drafts")
async def generate_twitter_drafts_endpoint(query: str):
    """
    Fetch articles and generate Twitter drafts based on them.

    Args:
        query (str): The search query for articles.

    Returns:
        dict: A list of three Twitter drafts.
    """
    try:
        # Fetch articles with content
        articles = fetch_articles_from_brave(query)

        # Generate Twitter drafts
        drafts = generate_twitter_drafts(articles)

        return {"status": "Drafts generated successfully!", "drafts": drafts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
    

@app.post("/process-request")
async def process_request(session_id: str, user_input: str):
    """
    Main endpoint for processing user requests.
    """
    try:
        # Log the user's input
        log_message_to_supabase(
            session_id=session_id,
            message_type="human",
            content=user_input,
            metadata={"source": "voice_input"}
        )

        # Call Brave API and OpenAI logic
        articles = fetch_articles_from_brave(user_input)
        log_message_to_supabase(
            session_id=session_id,
            message_type="ai",
            content=f"Fetched {len(articles)} articles",
            metadata={"source": "Brave API", "query": user_input}
        )

        # Generate Twitter drafts using OpenAI
        drafts = generate_twitter_drafts(articles)
        log_message_to_supabase(
            session_id=session_id,
            message_type="ai",
            content="Generated Twitter drafts",
            metadata={"source": "OpenAI", "drafts": drafts}
        )

        return {"status": "success", "drafts": drafts}
    except Exception as e:
        log_message_to_supabase(
            session_id=session_id,
            message_type="error",
            content=f"Error processing request: {str(e)}",
            metadata={"source": "process_request"}
        )
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")
    
    