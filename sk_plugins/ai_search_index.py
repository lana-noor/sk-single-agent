import os
from dotenv import load_dotenv
from semantic_kernel.functions import kernel_function
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.models import VectorizableTextQuery

load_dotenv()

AZURE_SEARCH_ENDPOINT= os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_API_KEY")
SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX")


class AiSearch:
    @kernel_function(name="ai_search", description="")
    def ai_search(self, query: str) -> str:
        """Search Water Theme Park data on encounters and experiences at the park. Use for general information about the Water Park."""
        credential = AzureKeyCredential(AZURE_SEARCH_KEY)
        client = SearchClient(
            endpoint=AZURE_SEARCH_ENDPOINT,
            index_name=SEARCH_INDEX_NAME,
            credential=credential,
        )
        results = client.search(
            search_text=query,
            vector_queries=[
                VectorizableTextQuery(
                    text=query, k_nearest_neighbors=50, fields="vector"
                )
            ],
            query_type="semantic",
            semantic_configuration_name="my-semantic-config",
            search_fields=["chunk"],
            top=3,
            include_total_count=True,
        )
        retrieved_texts = [result.get("chunk") for result in results]
        context_str = (
            "\n".join(retrieved_texts) if retrieved_texts else "No documents found."
        )
        return context_str
    