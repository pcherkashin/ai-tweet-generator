import os
import tweepy
from dotenv import load_dotenv
from supabase_utils import log_message_to_supabase

# Load environment variables
load_dotenv()

def get_twitter_client():
    """
    Initialize and return a Twitter API client using OAuth 1.0a.
    """
    # Get credentials from environment variables
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    
    if not all([api_key, api_secret, access_token, access_token_secret]):
        raise ValueError("""Missing Twitter API credentials in environment variables. 
                       Make sure you have all required credentials in your .env file:
                       - TWITTER_API_KEY
                       - TWITTER_API_SECRET
                       - TWITTER_ACCESS_TOKEN
                       - TWITTER_ACCESS_TOKEN_SECRET""")
    
    try:
        # Initialize Twitter client with OAuth 1.0a
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        # Test the client
        me = client.get_me()
        print(f"Connected to Twitter as: {me.data.username}")
        
        return client
        
    except Exception as e:
        raise Exception(f"Failed to initialize Twitter client: {str(e)}")

def post_tweet(tweet_text: str, session_id: str) -> dict:
    """
    Post a tweet using the Twitter API with OAuth 1.0a.
    
    Args:
        tweet_text (str): The text to tweet
        session_id (str): Session ID for logging
    
    Returns:
        dict: Response from Twitter API containing tweet details
    """
    try:
        # Get Twitter client
        client = get_twitter_client()
        
        # Log attempt
        log_message_to_supabase(
            session_id=session_id,
            message_type="system",
            content="Attempting to post tweet",
            metadata={"tweet_text": tweet_text}
        )
        
        # Post tweet
        response = client.create_tweet(text=tweet_text)
        
        if response and response.data:
            tweet_id = response.data["id"]
            tweet_url = f"https://twitter.com/user/status/{tweet_id}"
            
            # Log successful tweet
            log_message_to_supabase(
                session_id=session_id,
                message_type="system",
                content="Tweet posted successfully",
                metadata={
                    "tweet_id": tweet_id,
                    "tweet_url": tweet_url,
                    "tweet_text": tweet_text
                }
            )
            
            return {
                "success": True,
                "tweet_id": tweet_id,
                "tweet_url": tweet_url,
                "tweet_text": tweet_text
            }
        else:
            raise Exception("No response data received from Twitter API")
            
    except Exception as e:
        error_message = f"Error posting tweet: {str(e)}"
        # Log error with detailed information
        log_message_to_supabase(
            session_id=session_id,
            message_type="error",
            content=error_message,
            metadata={
                "tweet_text": tweet_text,
                "error_type": type(e).__name__,
                "error_details": str(e)
            }
        )
        raise Exception(error_message)