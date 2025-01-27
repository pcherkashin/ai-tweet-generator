import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from supabase_utils import log_message_to_supabase

def crawl_url(url: str, session_id: str) -> str:
    """
    Fetch and parse content from a URL.
    
    Args:
        url (str): URL to crawl
        session_id (str): Session ID for logging
    
    Returns:
        str: Extracted text content
    """
    try:
        # Add user agent to avoid blocks
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch URL content
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Extract text
        text = soup.get_text(separator='\n', strip=True)
        
        # Basic text cleaning
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        content = '\n'.join(lines)
        
        # Truncate if too long (e.g., for API limits)
        max_length = 4000
        if len(content) > max_length:
            content = content[:max_length] + "..."
            
        # Log successful crawl
        log_message_to_supabase(
            session_id=session_id,
            message_type="system",
            content=f"Successfully crawled {url}",
            metadata={"url": url, "content_length": len(content)}
        )
        
        return content
        
    except Exception as e:
        error_message = f"Error crawling {url}: {str(e)}"
        # Log error
        log_message_to_supabase(
            session_id=session_id,
            message_type="error",
            content=error_message,
            metadata={"url": url}
        )
        return f"Error fetching content: {str(e)}"

def crawl_articles(articles: list, session_id: str) -> list:
    """
    Crawl content from a list of articles.
    
    Args:
        articles (list): List of articles with URLs
        session_id (str): Session ID for logging
    
    Returns:
        list: Articles enriched with crawled content
    """
    enriched_articles = []
    
    for article in articles:
        url = article.get('url')
        if url and url != "No URL":
            content = crawl_url(url, session_id)
            enriched_articles.append({
                **article,
                'content': content
            })
        else:
            enriched_articles.append(article)
    
    return enriched_articles