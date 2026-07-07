import webbrowser
import urllib.parse
from ddgs import DDGS


def play_on_youtube(query: str) -> str:
    """
    Searches YouTube for a query and opens the top video in the default web browser.
    
    Args:
        query: The song or video to search for.
        
    Returns:
        A message describing what it did.
    """
    print(f"Searching YouTube for: '{query}'")
    try:
        # Attempt to search using DuckDuckGo Video search
        with DDGS() as ddgs:
            # We search specifically on youtube.com
            results = list(ddgs.videos(f"{query} site:youtube.com", max_results=3))
            
            if results:
                # Find the first result that is actually a youtube link
                for r in results:
                    video_url = r.get('content') or r.get('embed_url') or r.get('url')
                    if video_url and ('youtube.com' in video_url or 'youtu.be' in video_url):
                        webbrowser.open(video_url)
                        title = r.get('title', query)
                        return f"Found and opening '{title}' on YouTube in your browser."

    except Exception as e:
        print(f"DuckDuckGo video search failed: {e}. Falling back to search query URL.")
    
    # Fallback: open the direct YouTube search results page
    encoded_query = urllib.parse.quote(query)
    fallback_url = f"https://www.youtube.com/results?search_query={encoded_query}"
    webbrowser.open(fallback_url)
    return f"Opening YouTube search results for '{query}' in your browser."
