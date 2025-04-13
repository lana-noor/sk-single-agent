import os
import requests
from dotenv import load_dotenv
from semantic_kernel.functions import kernel_function

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

class GoogleWebSearch:
    @kernel_function(
        name="web_search",
        description="Search the public internet using Google Search API to retrieve recent or real-time information."
    )
    def web_search(self, query: str) -> str:
        """Search the internet using Google Programmable Search Engine."""
        base_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_SEARCH_ENGINE_ID,
            "q": query,
            "num": 3
        }

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])

            if not items:
                return "No search results found."

            results = []
            for item in items:
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                link = item.get("link", "")
                results.append(f"{title}\n{snippet}\n{link}")

            return "\n\n---\n\n".join(results)

        except Exception as e:
            return f"Error during Google web search: {e}"
