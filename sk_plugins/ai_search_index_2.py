import os
from dotenv import load_dotenv
from semantic_kernel.functions import kernel_function
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.models import VectorizableTextQuery

load_dotenv()

AZURE_SEARCH_ENDPOINT_2 = os.getenv("AZURE_SEARCH_ENDPOINT_2")
AZURE_SEARCH_KEY_2 = os.getenv("AZURE_SEARCH_API_KEY_2")
SEARCH_INDEX_NAME_2 = os.getenv("AZURE_SEARCH_INDEX_2")

class AiSearch2:
    @kernel_function(name="ai_search", description="")
    def ai_search(self, query: str) -> str:
        """Search Seaworld MAP data when a user asks for directions around SeaWorld or for specific locations around the park."""
        credential = AzureKeyCredential(AZURE_SEARCH_KEY_2)
        client = SearchClient(
            endpoint=AZURE_SEARCH_ENDPOINT_2,
            index_name=SEARCH_INDEX_NAME_2,
            credential=credential,
        )
        results = client.search(
            search_text=query,
            vector_queries=[
                VectorizableTextQuery(
                    text=query, k_nearest_neighbors=50, fields="text_vector"
                )
            ],
            query_type="semantic",
            semantic_configuration_name="my-semantic-config",
            search_fields=["text"],
            top=3,
            include_total_count=True,
        )
        retrieved_texts = [result.get("text") for result in results]
        context_str = (
            "\n".join(retrieved_texts) if retrieved_texts else "No documents found."
        )
        return context_str
    