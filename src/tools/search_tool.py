from ddgs import DDGS


def web_search(query: str) -> str:
    """
    Searches the web using DuckDuckGo and returns a summary of the top results.
    
    Args:
        query: The search query.
        
    Returns:
        A list of search result snippets and links.
    """
    print(f"Searching the web for: '{query}'")
    try:
        with DDGS() as ddgs:
            # text search
            results = list(ddgs.text(query, max_results=3))
            
            if not results:
                return f"No search results found for '{query}'."
                
            summary = f"Here is what I found for '{query}':\n"
            for r in results:
                title = r.get('title', 'No Title')
                body = r.get('body', '')
                href = r.get('href', '')
                summary += f"- {title}: {body} (Link: {href})\n"
            return summary
    except Exception as e:
        print(f"DuckDuckGo search error: {e}")
        return f"Sorry, I encountered an error searching the web: {e}"
