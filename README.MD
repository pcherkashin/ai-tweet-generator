# AI-Driven Tweet Generator

## Overview

This repository hosts an **AI-driven Tweet Generator** designed to streamline the process of generating engaging Twitter drafts. The application integrates **voice input**, **search results from Brave API**, **content analysis using Crawl4AI**, and **OpenAI GPT-4** to create concise, impactful tweets. Users can choose their preferred draft and optionally post it directly to Twitter.

---

## Features

- **Voice Input with Speech Recognition**: Transcribe user voice commands into text.
- **Text Input Option**: For users who prefer manual text entry.
- **Article Search**: Fetch relevant articles using Brave API based on user queries.
- **Content Crawling**: Analyze and extract textual content from article URLs.
- **AI-Powered Draft Generation**: Use OpenAI GPT-4 to generate three engaging tweet drafts.
- **Draft Selection**: Let users choose their preferred draft and optionally post it to Twitter.
- **Logging with Supabase**: Save all interactions, API responses, and selected drafts in Supabase for tracking.

---

## Tech Stack

### Backend:

- **FastAPI**: RESTful API backend.
- **Supabase**: Real-time database for logging and user interaction storage.

### Frontend:

- **Streamlit**: User-friendly interface for managing inputs, processing, and results.

### Libraries & APIs:

- **OpenAI Whisper**: For audio-to-text transcription.
- **SpeechRecognition**: For capturing voice input via microphone.
- **Brave API**: For web article searches.
- **Crawl4AI**: For extracting content from article URLs.
- **Tweepy**: For posting tweets on Twitter.

---

## Installation

### Prerequisites

- Python 3.12 or higher
- Access to required API keys:
  - OpenAI API Key
  - Brave API Key
  - Twitter API Keys
  - Supabase credentials

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/pcherkashin/ai-tweet-generator.git
   cd ai-tweet-generator
   ```
````

2. Set up a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file and configure API keys. Use `.env.example` as a template:
   ```bash
   cp .env.example .env
   ```

---

## Usage

### Running the App

1. Start the FastAPI backend:

   ```bash
   uvicorn main:app --reload
   ```

2. Launch the Streamlit frontend:

   ```bash
   source venv/bin/activate && streamlit run streamlit_app.py
   ```

3. Open the Streamlit interface in your browser:
   ```
   http://localhost:8501
   ```

### Workflow

1. Select **voice** or **text** input.
2. Enter or record your query (e.g., "Create a tweet about AI technology").
3. Generate drafts:
   - The app searches articles related to your query via the Brave API.
   - Content is crawled and analyzed for relevance.
   - Three drafts are generated using OpenAI GPT-4.
4. Choose a draft:
   - Select your preferred draft by entering its number (1, 2, or 3).
5. Post to Twitter (optional).

---

## File Structure

```
.
├── .env.example          # Environment variable template
├── main.py               # FastAPI backend
├── streamlit_app.py      # Streamlit frontend
├── brave_api.py          # Brave API integration
├── openai_api.py         # OpenAI GPT-4 integration
├── crawler_utils.py      # Crawl4AI content extraction
├── supabase_utils.py     # Supabase interaction
├── voice_input.py        # SpeechRecognition integration
├── voice_utils.py        # OpenAI Whisper transcription
├── twitter_utils.py      # Twitter posting
├── requirements.txt      # Dependencies
```

---

## Environment Variables

Configure these variables in the `.env` file:

```plaintext
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Brave Search API Configuration
BRAVE_API_KEY=your_brave_api_key_here

# Twitter API Configuration
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret

# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

---

## Agent0 Studio Integration

### API Endpoint

The application provides an Agent0 Studio compatible endpoint at `/api/tweet-gen` that accepts POST requests with the following structure:

```json
{
  "query": "User's input text",
  "user_id": "Unique user identifier",
  "request_id": "Unique request identifier",
  "session_id": "Conversation session identifier",
  "files": []
}
```

The endpoint returns a simple success/failure response:
```json
{
  "success": true
}
```

All conversation history and generated content is stored in the Supabase messages table.

### Database Setup

1. Create the required database table and enable realtime updates by running the SQL commands in `setup_database.sql`:
   ```sql
   -- Enable pgcrypto for UUID generation
   CREATE EXTENSION IF NOT EXISTS pgcrypto;

   -- Create messages table
   CREATE TABLE messages (
       id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
       created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
       session_id TEXT NOT NULL,
       message JSONB NOT NULL
   );

   -- Create indexes
   CREATE INDEX idx_messages_session_id ON messages(session_id);
   CREATE INDEX idx_messages_created_at ON messages(created_at);

   -- Enable realtime updates
   alter publication supabase_realtime add table messages;
   ```

2. The messages table stores all interactions with the following structure:
   - For user messages:
     ```json
     {
       "type": "human",
       "content": "User's input text"
     }
     ```
   - For agent responses:
     ```json
     {
       "type": "ai",
       "content": "Agent's response text",
       "data": {
         "drafts": [...],
         "articles": [...]
       }
     }
     ```

## Key Components

### 1. **Brave API**

Fetches up to 5 articles based on the user query. Results include:

- Article titles
- URLs
- Summaries

### 2. **Crawl4AI**

Crawls the URLs returned by the Brave API to extract and clean the main content.

### 3. **OpenAI GPT-4**

Generates three Twitter drafts based on the content crawled. Each draft contains:

- Catchy hook
- Insight or question
- Call-to-action (CTA)

### 4. **Supabase Logging**

Logs all user requests, responses, and interactions into the `messages` table for analysis.

### 5. **Streamlit Frontend**

Provides a simple interface for:

- Managing input (voice or text)
- Displaying drafts
- Selecting and posting tweets

---

## Testing

- **Unit Testing**: Use test scripts like `test_openai_generation.py` to validate OpenAI integrations.
- **Twitter Integration**: Test posting functionality with `test_twitter_post.py`.

---

## Future Enhancements

- Add more personalization to drafts using user profile data.
- Extend to other social media platforms like LinkedIn and Instagram.
- Improve UI for better accessibility and aesthetics.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Support

If you encounter any issues, feel free to open an issue or contact the contributors.

Happy Tweeting! 🚀

```

```
