import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI()

def generate_twitter_drafts(articles):
    """
    Generate three engaging Twitter drafts based on article content.

    Args:
        articles (list): A list of articles with titles, URLs, and descriptions.

    Returns:
        list: A list of three Twitter drafts in JSON format.
    """
    try:
        # Combine article details into context
        context = "\n\n".join([
            f"Title: {article['title']}\nURL: {article['url']}\nDescription: {article['description']}"
            for article in articles
        ])

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
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a social media expert. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )

        # Parse JSON response
        text = response.choices[0].message.content.strip()
        drafts_data = json.loads(text)

        return drafts_data["drafts"]
    except json.JSONDecodeError as e:
        raise Exception(f"Error parsing JSON response: {str(e)}")
    except Exception as e:
        raise Exception(f"Error generating Twitter drafts: {str(e)}")


if __name__ == "__main__":
    # Mockup data
    articles = [
        {"title": "AI and the Future", "url": "https://example.com/ai-future", "description": "How AI is reshaping industries."},
        {"title": "AI Tools Revolution", "url": "https://example.com/ai-tools", "description": "Discover cutting-edge AI tools."},
        {"title": "Ethics of AI", "url": "https://example.com/ethics-ai", "description": "Exploring the moral challenges of AI."}
    ]

    # Generate drafts
    try:
        drafts = generate_twitter_drafts(articles)
        print("Generated Twitter Drafts:\n")
        print(json.dumps(drafts, indent=2))
    except Exception as e:
        print(f"Failed to generate drafts: {e}")
