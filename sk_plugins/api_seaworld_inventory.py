import os
import requests
from dotenv import load_dotenv
from semantic_kernel.functions import kernel_function

load_dotenv()
URL = os.getenv("URL_retrieve_data")

class SeaworldInventory:
    @kernel_function(
        name="get_inventory",
        description="Retrieve the full SeaWorld Abu Dhabi shops inventory as a JSON object."
    )
    def get_inventory(self) -> list:
        """
        Calls the Azure Function API and returns the full inventory as a JSON list.
        """
        url = URL
        response = requests.get(url)
        response.raise_for_status()
        return response.json()  # <-- Returns a list of dicts
