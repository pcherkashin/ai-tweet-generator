import os
from dotenv import load_dotenv
import tweepy

def test_twitter_posting():
    """
    Test Twitter posting functionality with OAuth 1.0a.
    Prints detailed information about the process and any errors.
    """
    print("\n=== Testing Twitter Posting (OAuth 1.0a) ===")
    
    # Load environment variables
    load_dotenv()
    print("\nChecking Twitter credentials...")
    
    # Check for required credentials
    required_vars = [
        "TWITTER_API_KEY",
        "TWITTER_API_SECRET",
        "TWITTER_ACCESS_TOKEN",
        "TWITTER_ACCESS_TOKEN_SECRET"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("\n❌ Error: Missing required Twitter credentials:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease follow these steps to set up your Twitter API credentials:")
        print("1. Go to https://developer.twitter.com/en/portal/dashboard")
        print("2. Select your project and app")
        print("3. Go to 'Keys and tokens'")
        print("4. Under 'Consumer Keys', find your API Key and Secret")
        print("5. Under 'Authentication Tokens', generate Access Token & Secret")
        print("6. Make sure your App has 'Read and Write' permissions")
        print("7. Update your .env file with the credentials")
        return
    
    print("✅ All required Twitter credentials found")
    
    try:
        # Initialize Twitter client
        client = tweepy.Client(
            consumer_key=os.getenv("TWITTER_API_KEY"),
            consumer_secret=os.getenv("TWITTER_API_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )
        
        # Test authentication
        print("\nTesting authentication...")
        me = client.get_me()
        print(f"✅ Connected to Twitter as: @{me.data.username}")
        
        # Test tweet content
        test_tweet = "This is a test tweet from AI Tweet Generator 🤖 #TestTweet"
        print(f"\nAttempting to post test tweet:\n{test_tweet}")
        
        # Post tweet
        response = client.create_tweet(text=test_tweet)
        
        if response and response.data:
            tweet_id = response.data["id"]
            tweet_url = f"https://twitter.com/user/status/{tweet_id}"
            print("\n✅ Tweet posted successfully!")
            print(f"Tweet ID: {tweet_id}")
            print(f"Tweet URL: {tweet_url}")
            print(f"Tweet text: {test_tweet}")
        else:
            print("\n❌ Failed to post tweet: No response data received")
            
    except tweepy.errors.Forbidden as e:
        print("\n❌ Error: Twitter API Permission Error")
        print("Make sure your App has 'Read and Write' permissions.")
        print("\nPlease verify:")
        print("1. App permissions are set to 'Read and Write'")
        print("2. Access Token & Secret have write permissions")
        print("3. Regenerate Access Token & Secret if needed")
        print(f"\nOriginal error: {str(e)}")
            
    except Exception as e:
        print("\n❌ Error occurred while posting tweet:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        
        # Additional error details for debugging
        print("\nDebug information:")
        print("Twitter API credentials present:")
        for var in required_vars:
            masked_value = "✅ Set" if os.getenv(var) else "❌ Missing"
            print(f"  - {var}: {masked_value}")

if __name__ == "__main__":
    test_twitter_posting()