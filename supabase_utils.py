import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def log_message_to_supabase(session_id: str, message_type: str, content: str, metadata: dict = None):
    """
    Log a message to the Supabase 'messages' table.

    Args:
        session_id (str): Unique session identifier.
        message_type (str): 'human' for user input, 'ai' for AI response.
        content (str): The message content.
        metadata (dict, optional): Additional details (e.g., query params, AI model info).
    """
    try:
        message_data = {
            "type": message_type,
            "content": content,
            "metadata": metadata or {}
        }
        supabase.table("messages").insert({
            "session_id": session_id,
            "message": message_data
        }).execute()
    except Exception as e:
        print(f"Error logging message to Supabase: {e}")
