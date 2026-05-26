from googlesearch import search

def live_web_search(query: str) -> str:
    """
    Queries the live web grid and extracts top search URL results 
    to feed real-time information back to Friday's core.
    """
    clean_query = query.lower().replace("search", "").replace("google", "").replace("look up", "").strip()
    print(f"[CRAWLER]: Initiating web grid search for: '{clean_query}'")
    
    try:
        # Fetch the top 3 live URLs from Google
        search_results = list(search(clean_query, num_results=3))
        
        if not search_results:
            return "Web grid query returned zero active data packets."
            
        # Format the links nicely for the AI to analyze
        compiled_results = "Live data packets retrieved from the web grid:\n"
        for i, url in enumerate(search_results, 1):
            compiled_results += f"Source {i}: {url}\n"
            
        return compiled_results
    except Exception as e:
        return f"Web crawler execution encountered a network exception: {str(e)}"