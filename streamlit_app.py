import streamlit as st
import uuid
import os
from voice_utils import transcribe_audio_file
from brave_api import fetch_articles_from_brave
from crawler_utils import crawl_articles
from openai_api import generate_twitter_drafts
from supabase_utils import log_message_to_supabase

# Optional Twitter import
TWITTER_ENABLED = False
try:
    from twitter_utils import post_tweet
    TWITTER_ENABLED = True
except ImportError:
    pass

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

# Text Input Section
else:
    user_input = st.text_input("Enter your request:", 
                              placeholder="Example: Create a tweet about AI technology")
    if user_input:
        st.session_state.transcribed_text = user_input
        st.info(f"📝 Input received: {user_input}")

# Process Input and Generate Drafts
if st.session_state.transcribed_text and st.button("Generate Tweet Drafts"):
    try:
        with st.spinner("🔍 Fetching relevant articles..."):
            # Fetch articles
            articles = fetch_articles_from_brave(
                st.session_state.transcribed_text, 
                st.session_state.session_id
            )
            st.session_state.articles = articles
            st.success(f"✅ Found {len(articles)} relevant articles")
            
            # Crawl article content
            with st.spinner("📚 Analyzing article content..."):
                enriched_articles = crawl_articles(articles, st.session_state.session_id)
                st.success("✅ Article content analyzed")
            
            # Generate drafts
            with st.spinner("✍️ Generating tweet drafts..."):
                drafts = generate_twitter_drafts(enriched_articles, st.session_state.session_id)
                st.session_state.drafts = drafts
                st.success("✅ Tweet drafts generated")
            
            # Display drafts
            st.subheader("📋 Available Tweet Drafts")
            st.write("Select your preferred draft by entering its number (1, 2, or 3):")
            
            # Display all drafts in a clean format
            for draft in drafts:
                st.write(f"\n🔹 Draft {draft['number']}:")
                st.info(draft["text"])
            
            # Simple numeric input for selection
            selected_draft = st.text_input("Your choice (1, 2, or 3):")
            
            # Validate input
            if selected_draft:
                try:
                    draft_num = int(selected_draft)
                    if draft_num not in [1, 2, 3]:
                        st.error("❌ Please enter 1, 2, or 3 only")
                        st.session_state.selected_draft = None
                    else:
                        st.success(f"✅ Draft {draft_num} selected")
                        st.session_state.selected_draft = draft_num
                        
                        # Get selected tweet
                        selected_tweet = next(
                            draft for draft in drafts 
                            if draft["number"] == draft_num
                        )
                        
                        # Show confirmation section
                        st.write("\n🔍 Review Selected Tweet:")
                        st.info(selected_tweet["text"])
                        st.write("Do you want to post this tweet?")
                        
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
                                os.getenv("TWITTER_CONSUMER_KEY"),
                                os.getenv("TWITTER_CONSUMER_SECRET"),
                                os.getenv("TWITTER_ACCESS_TOKEN"),
                                os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
                            ])

                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("✅ Yes, Post Tweet", disabled=not twitter_creds):
                                    if not twitter_creds:
                                        st.error("❌ Twitter credentials missing. Check .env file.")
                                    else:
                                        try:
                                            with st.spinner("🐦 Posting tweet..."):
                                                result = post_tweet(
                                                    selected_tweet['text'], 
                                                    st.session_state.session_id
                                                )
                                                
                                                if result['success']:
                                                    st.success(f"✅ Tweet posted successfully!")
                                                    st.write(f"Tweet ID: {result['tweet_id']}")
                                                    
                                                    # Log success
                                                    log_message_to_supabase(
                                                        session_id=st.session_state.session_id,
                                                        message_type="system",
                                                        content="Tweet posted successfully",
                                                        metadata={
                                                            "tweet_id": result['tweet_id'],
                                                            "selected_tweet": selected_tweet
                                                        }
                                                    )
                                        except Exception as e:
                                            st.error(f"❌ Error posting tweet: {str(e)}")
                                            # Log error
                                            log_message_to_supabase(
                                                session_id=st.session_state.session_id,
                                                message_type="error",
                                                content=f"Error posting tweet: {str(e)}",
                                                metadata={"selected_tweet": selected_tweet}
                                            )
                            
                            with col2:
                                if st.button("🔄 Choose Different Draft"):
                                    st.session_state.selected_draft = None
                                    st.experimental_rerun()
                        else:
                            st.warning("⚠️ Twitter integration not enabled. Install tweepy to enable posting.")
                            st.info(f"Selected tweet text:\n{selected_tweet['text']}")
                            
                            # Log disabled Twitter
                            log_message_to_supabase(
                                session_id=st.session_state.session_id,
                                message_type="system",
                                content="Twitter posting attempted but disabled",
                                metadata={"selected_tweet": selected_tweet}
                            )
                except ValueError:
                    st.error("❌ Please enter 1, 2, or 3 only")
                    st.session_state.selected_draft = None
                
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        # Log error
        log_message_to_supabase(
            session_id=st.session_state.session_id,
            message_type="error",
            content=f"Error in tweet generation process: {str(e)}"
        )
