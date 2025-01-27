import os
import json
import requests
from fastapi import HTTPException
from dotenv import load_dotenv
from supabase_utils import log_message_to_supabase

# Load environment variables
load_dotenv()

def fetch_articles_from_brave(query: str, session_id: str):
    """
    Fetch articles related to the query using the Brave API.

    Args:
        query (str): The search query.
        session_id (str): The session ID to log interactions.

    Returns:
        list: A list of articles with titles, URLs, and descriptions.
    """
    brave_api_url = "https://api.search.brave.com/res/v1/web/search"
    api_key = os.getenv("BRAVE_API_KEY")
    
    if not api_key:
        raise HTTPException(status_code=500, detail="Brave API key not found in environment variables")
    
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": api_key
    }
    
    params = {
        "q": query,
        "count": 5,  # Limit to 5 articles
        "text_decorations": False,  # Disable text decorations like bold
        "safesearch": "moderate"
    }

    try:
        print(f"Making request to Brave API with query: {query}")  # Debug log
        print(f"Request URL: {brave_api_url}")  # Debug log
        print(f"Request headers: {headers}")  # Debug log
        print(f"Request params: {params}")  # Debug log
        
        # Log the request to Supabase
        log_message_to_supabase(
            session_id=session_id,
            message_type="human",
            content=f"Brave API request: {query}",
            metadata={"query": query, "source": "Brave API"}
        )
        
        response = requests.get(brave_api_url, headers=headers, params=params)
        
        print(f"Response status: {response.status_code}")  # Debug log
        print(f"Response headers: {dict(response.headers)}")  # Debug log
        
        if response.status_code == 401:
            print("Authentication error - invalid API key")  # Debug log
            raise HTTPException(status_code=500, detail="Invalid or expired API key")
        elif response.status_code != 200:
            print(f"API error - status code: {response.status_code}")  # Debug log
            raise HTTPException(status_code=500, detail=f"API error: {response.text}")
        
        try:
            data = response.json()
            print(f"Raw API Response: {data}")  # Debug log
            
            # Extract results from the response
            articles = []
            
            # Handle the response data according to WebSearchApiResponse structure
            if isinstance(data, dict):
                # Check for error response
                if "error" in data:
                    error_msg = data["error"].get("message", "Unknown API error")
                    print(f"API returned error: {error_msg}")  # Debug log
                    raise HTTPException(status_code=500, detail=error_msg)
                
                # Get web search results from the 'web' field
                web_results = data.get("web", {}).get("results", [])
                
                for result in web_results:
                    # Clean up text by removing all HTML tags
                    title = result.get("title", "")
                    description = result.get("description", "")
                    url = result.get("url", "")
                    
                    # Remove all HTML tags
                    for tag in ["<strong>", "</strong>", "<b>", "</b>"]:
                        title = title.replace(tag, "")
                        description = description.replace(tag, "")
                    
                    articles.append({
                        "title": title or "No Title",
                        "url": url or "No URL",
                        "description": description or "No Description"
                    })
            
            print(f"Processed {len(articles)} articles")  # Debug log
            
            # Log the response to Supabase
            log_message_to_supabase(
                session_id=session_id,
                message_type="ai",
                content=f"Brave API response with {len(articles)} articles",
                metadata={"articles": articles, "source": "Brave API"}
            )
            
            return articles
            
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON response: {e}")  # Debug log
            print(f"Raw response content: {response.text}")  # Debug log
            raise HTTPException(status_code=500, detail="Invalid JSON response from API")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")  # Debug log
        
        # Log the error to Supabase
        log_message_to_supabase(
            session_id=session_id,
            message_type="error",
            content=f"Error fetching articles: {str(e)}",
            metadata={"source": "Brave API"}
        )
        raise HTTPException(status_code=500, detail=f"Error fetching articles: {str(e)}")

