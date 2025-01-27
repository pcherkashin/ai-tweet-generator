import os
import json
from fastapi import HTTPException
from dotenv import load_dotenv
from openai import OpenAI
from supabase_utils import log_message_to_supabase

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI()
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("OpenAI API key not found in environment variables")

# Function to generate Twitter drafts
def generate_twitter_drafts(articles, session_id: str):
    """
    Generate three engaging Twitter drafts based on article content.

    Args:
        articles (list): A list of articles with titles, URLs, and descriptions.
        session_id (str): Session ID for logging interactions.

    Returns:
        list: A list of three Twitter drafts in JSON format.
    """
    try:
        # Combine article details into context
        context = "\n\n".join([
            f"Title: {article['title']}\nURL: {article['url']}\nDescription: {article['description']}"
            for article in articles
        ])

        # Log the request to Supabase
        log_message_to_supabase(
            session_id=session_id,
            message_type="human",
            content="Request to generate Twitter drafts.",
            metadata={"articles": articles}
        )

        # OpenAI prompt with JSON structure requirement
        prompt = f"""
        You are a social media expert. Using the following articles, generate 3 engaging and concise Twitter posts that encourage interaction and shares.

        Requirements for each post:
        - A catchy hook
        - A key insight or thought-provoking question
        - A call to action (e.g., "Read more", "Join the conversation", "What do you think?")
        - Ensure the tone is conversational, engaging, and professional

        Articles:
        {context}

        Return the drafts in the following JSON format:
        {{
            "drafts": [
                {{
                    "number": 1,
                    "text": "The complete tweet text",
                    "hook": "The hook used",
                    "insight": "The key insight or question",
                    "cta": "The call to action"
                }},
                {{
                    "number": 2,
                    "text": "The complete tweet text",
                    "hook": "The hook used",
                    "insight": "The key insight or question",
                    "cta": "The call to action"
                }},
                {{
                    "number": 3,
                    "text": "The complete tweet text",
                    "hook": "The hook used",
                    "insight": "The key insight or question",
                    "cta": "The call to action"
                }}
            ]
        }}

        Ensure each draft has a unique number from 1 to 3.
        """

        # Generate response using OpenAI GPT-4
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a social media expert. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ]
        )

        # Parse JSON response
        text = response.choices[0].message.content.strip()
        drafts_data = json.loads(text)

        # Log the response to Supabase
        log_message_to_supabase(
            session_id=session_id,
            message_type="ai",
            content="Generated Twitter drafts.",
            metadata={"drafts": drafts_data["drafts"]}
        )

        return drafts_data["drafts"]
    except json.JSONDecodeError as e:
        error_message = f"Error parsing JSON response: {str(e)}"
        # Log the error to Supabase
        log_message_to_supabase(
            session_id=session_id,
            message_type="error",
            content=error_message
        )
        raise HTTPException(status_code=500, detail=error_message)
    except Exception as e:
        error_message = f"Error generating Twitter drafts: {str(e)}"
        # Log the error to Supabase
        log_message_to_supabase(
            session_id=session_id,
            message_type="error",
            content=error_message
        )
        raise HTTPException(status_code=500, detail=error_message)
