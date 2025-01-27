import streamlit as st
import uuid
import os
from voice_utils import transcribe_audio_file
from brave_api import fetch_articles_from_brave
from crawler_utils import crawl_articles
from openai_api import generate_twitter_drafts
from supabase_utils import log_message_to_supabase

# Twitter import
try:
    from twitter_utils import post_tweet
    TWITTER_ENABLED = True
except ImportError as e:
    st.error(f"⚠️ Error importing Twitter module: {str(e)}")
    TWITTER_ENABLED = False

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'transcribed_text' not in st.session_state:
    st.session_state.transcribed_text = None
if 'articles' not in st.session_state:
    st.session_state.articles = None
if 'drafts' not in st.session_state:
    st.session_state.drafts = None
if 'selected_draft' not in st.session_state:
    st.session_state.selected_draft = None
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

def reset_state():
    """Reset all state and refresh the page"""
    # Generate new session ID
    new_session_id = str(uuid.uuid4())
    # Clear all session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    # Set new session ID
    st.session_state.session_id = new_session_id
    # Initialize other state variables
    st.session_state.transcribed_text = None
    st.session_state.articles = None
    st.session_state.drafts = None
    st.session_state.selected_draft = None
    st.session_state.processing_complete = False
    st.session_state.user_input = ""
    
    # Clear cache and reload the page
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()

# Streamlit App Title
st.title("AI-Driven Tweet Generator")

# Input Type Selection
input_type = st.radio("Choose input type:", ["Voice", "Text"])

# Voice Input Section
if input_type == "Voice":
    st.info("📝 Upload an audio file for transcription")
    audio_file = st.file_uploader("Choose an audio file", type=['wav', 'mp3', 'm4a'])
    
    if audio_file:
        try:
            with st.spinner("🎙️ Transcribing audio..."):
                transcribed_text = transcribe_audio_file(audio_file, st.session_state.session_id)
                if transcribed_text:
                    st.success(f"✅ Transcribed Text: {transcribed_text}")
                    st.session_state.transcribed_text = transcribed_text
        except Exception as e:
            st.error(f"❌ Error transcribing audio: {str(e)}")
            if st.button("🔄 Try Again", key="try_again_voice"):
                reset_state()

# Text Input Section
else:
    # Use session ID in the key to ensure it's unique after reset
    user_input = st.text_input(
        "Enter your request:", 
        value=st.session_state.user_input,
        placeholder="Example: Create a tweet about AI technology",
        key=f"text_input_{st.session_state.session_id}"
    )
    if user_input:
        st.session_state.user_input = user_input
        st.session_state.transcribed_text = user_input

# Process Input and Generate Drafts
if st.session_state.transcribed_text:
    try:
        if not st.session_state.drafts:
            with st.spinner("🔍 Fetching relevant articles..."):
                # Fetch articles
                articles = fetch_articles_from_brave(
                    st.session_state.transcribed_text, 
                    st.session_state.session_id
                )
                st.session_state.articles = articles
                st.success(f"✅ Found {len(articles)} relevant articles")
            
            with st.spinner("📚 Analyzing article content..."):
                # Crawl article content
                enriched_articles = crawl_articles(articles, st.session_state.session_id)
                st.success("✅ Article content analyzed")
            
            with st.spinner("✍️ Generating tweet drafts..."):
                # Generate drafts
                drafts = generate_twitter_drafts(enriched_articles, st.session_state.session_id)
                st.session_state.drafts = drafts
                st.success("✅ Tweet drafts generated")
                st.session_state.processing_complete = True
        
        # Display drafts
        st.subheader("📋 Available Tweet Drafts")
        st.write("Enter 0 to cancel, or 1-3 to select a draft:")
        
        # Display all drafts in a clean format
        for draft in st.session_state.drafts:
            st.write(f"\n🔹 Draft {draft['number']}:")
            st.info(draft["text"])
            st.write("---")
        
        # Simple numeric input for selection
        selected_draft = st.text_input(
            "Your choice (0 to cancel, 1-3 to select):", 
            key=f"draft_selection_{st.session_state.session_id}"
        )
        
        # Validate input
        if selected_draft:
            try:
                draft_num = int(selected_draft)
                if draft_num == 0:
                    st.warning("✋ Operation cancelled.")
                    # Log cancellation
                    log_message_to_supabase(
                        session_id=st.session_state.session_id,
                        message_type="user_action",
                        content="User cancelled tweet posting",
                        metadata={"action": "cancel"}
                    )
                    if st.button("🔄 Try Again", key="try_again_cancel"):
                        reset_state()
                        
                elif draft_num not in [1, 2, 3]:
                    st.error("❌ Please enter 0 to cancel, or 1, 2, 3 to select a draft")
                else:
                    # Get selected tweet
                    selected_tweet = next(
                        draft for draft in st.session_state.drafts 
                        if draft["number"] == draft_num
                    )
                    
                    # Show confirmation section
                    st.write("\n🔍 Selected Tweet:")
                    st.info(selected_tweet["text"])
                    
                    # Log selection
                    log_message_to_supabase(
                        session_id=st.session_state.session_id,
                        message_type="user_action",
                        content=f"Draft {draft_num} selected for review",
                        metadata={"selected_draft": selected_tweet}
                    )
                    
                    if TWITTER_ENABLED:
                        # Check for Twitter credentials
                        twitter_creds = all([
                            os.getenv("TWITTER_API_KEY"),
                            os.getenv("TWITTER_API_SECRET"),
                            os.getenv("TWITTER_ACCESS_TOKEN"),
                            os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
                        ])

                        if not twitter_creds:
                            missing_creds = []
                            if not os.getenv("TWITTER_API_KEY"): missing_creds.append("TWITTER_API_KEY")
                            if not os.getenv("TWITTER_API_SECRET"): missing_creds.append("TWITTER_API_SECRET")
                            if not os.getenv("TWITTER_ACCESS_TOKEN"): missing_creds.append("TWITTER_ACCESS_TOKEN")
                            if not os.getenv("TWITTER_ACCESS_TOKEN_SECRET"): missing_creds.append("TWITTER_ACCESS_TOKEN_SECRET")
                            st.error(f"❌ Missing Twitter credentials: {', '.join(missing_creds)}")
                            st.info("Please add these credentials to your .env file. See .env.example for instructions.")
                        else:
                            try:
                                with st.spinner("🐦 Posting to Twitter (X)..."):
                                    result = post_tweet(
                                        selected_tweet['text'],
                                        st.session_state.session_id
                                    )
                                    
                                    if result['success']:
                                        st.success("✅ Tweet published successfully!")
                                        st.write(f"🔗 Tweet URL: {result['tweet_url']}")
                            except Exception as e:
                                st.error(f"❌ Error posting tweet: {str(e)}")
                    else:
                        st.error("⚠️ Twitter integration is not enabled. Please check if tweepy is installed correctly.")
                        st.info("Selected tweet text (copy to post manually):")
                        st.code(selected_tweet["text"])
                    
                    if st.button("🔄 Try Again", key="try_again_after_post"):
                        reset_state()
                            
            except ValueError:
                st.error("❌ Please enter 0 to cancel, or 1, 2, 3 to select a draft")
                
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        # Log error
        log_message_to_supabase(
            session_id=st.session_state.session_id,
            message_type="error",
            content=f"Error in tweet generation process: {str(e)}"
        )
        if st.button("🔄 Try Again", key="try_again_error"):
            reset_state()
