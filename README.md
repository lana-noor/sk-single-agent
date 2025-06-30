# Single Agent Semantic Kernel Demo 
---

## Overview

This repository demonstrates a modular, extensible AI agent built with Semantic Kernel, Azure OpenAI, and Chainlit to support advanced question-answering, search, and workflow automation for the Water Theme Park.  
It features a plugin-based architecture and real-time retrieval of data from both internal knowledge bases and external APIs.

The repo includes:
- **`appchainlit.py`**: The main agentic RAG app, leveraging Semantic Kernel, Chainlit, and Azure OpenAI.
- **`api_function_app/`**: A serverless Azure Function that exposes shop inventory as a live API (simulates real-world data retrieval).
- **`sk_plugins/`**: Skills or tools used by the main RAG app. Skills are exposed as plugins and include AI Search, Map Search, Web Search, and Inventory Retrieval. 
---

## 1. Semantic Kernel Agent App (`appchainlit.py`)

The core of this solution is a single-agent AI assistant that routes user queries to the most relevant data source using Semantic Kernel plugins.  
This includes:

- Azure AI Search for Water Theme Park Experience Guide (exhibits, attractions, rides, amenities, and more).
- Azure AI Search for map/location-based queries (using LLM-verbalized map data).
- Function app plugin for live shop inventory (retrieves data from an external JSON API).
- Web search plugin for public, real-time data.

**Architecture highlights:**
- User questions are ingested via Chainlit UI or CLI.
- The Skills Router Agent selects the right plugin based on user intent.
- Plugins call out to Azure AI Search, the function app, or web APIs.
- Results are combined and streamed back to the user with full chat history/context.

---

### Architecture - Full Agentic Pipeline & Retrieval Orchestration 
See the diagram below for a full overview of the app flow, including data pipelines, retrieval logic, and plugin orchestration.
![LinkedIn Semantic Kernel Single Agent REPO Aval (2)](https://github.com/user-attachments/assets/c237f641-a9de-4506-a7de-1adee279a540)

This demo showcases a modular Retrieval-Augmented Generation (RAG) application for a Water Theme Park, built with Semantic Kernel (pre-Agent Framework, [v0.8.x](https://github.com/microsoft/semantic-kernel/releases/tag/0.8.7)), Chainlit for the frontend, and a set of custom plugins for data retrieval and orchestration.
This architecture allows the agent to dynamically answer user questions by selecting the most relevant data source: combining real-time shop inventory, map and location details (from LLM-verbalized map data), park experience information, and public web data—all orchestrated seamlessly via plugins and Semantic Kernel.

### Key architectural details

- **Frontend:**  
  The user interface is built with Chainlit and runs locally for this demo (not deployed to Azure).

- **Backend Orchestration:**  
  The core logic, chat flow, and skills router agent are implemented in `appchainlit.py`. The skills router agent leverages Azure OpenAI (GPT-4.1) to select the appropriate retrieval plugin for each user question.

- **Plugins:**  
  Data source plugins (web search, shop inventory API, map index, and experience guide index) are implemented as Python classes in the `sk_plugins` folder. These plugins are registered and managed within the main app script.

- **API Plugin / Function App:**  
  The `api_inventory` plugin retrieves live shop inventory data by making an HTTPS call to a function app endpoint. The function app code and inventory data reside in the `api_function_app/` folder. The function is deployed to Azure Functions, providing a public URL for real-time data access.

- **Chat History:**  
  For this demo, Cosmos DB is not used. Chat history is managed out-of-the-box by Semantic Kernel's in-memory utilities.

- **Semantic Kernel Version:**  
  This project uses the older Semantic Kernel SDK (v0.8.x), not the new agent framework.

- **Diagram Reference (Purple Box):**  
  The purple box in the architecture diagram represents all components that are implemented in the Python application—specifically, the skills router agent in `appchainlit.py` and plugins in the `sk_plugins` folder.

- **Ingestion Pipelines:**  
  - **Push API for Multimodal Map Data:**  
    The Water Theme Park map, as a multimodal (image + text) asset, is processed using the [mm_doc_proc pipeline](https://github.com/samelhousseini/mm_doc_proc/tree/main). The PDF map is verbalized (image analysis and description) using GPT-4.1, converted to structured JSON, and indexed in Azure AI Search.
  - **Pull API (Indexer) for Text Data:**  
    Text-based data, such as the Water Theme Park Experience Guide, is ingested and indexed using the [integrated vectorization notebook](https://github.com/Azure/azure-search-vector-samples/tree/main/demo-python/code/integrated-vectorization). This automates chunking and indexing of PDFs from Azure Blob Storage.

---

### Deploy & Run the Semantic Kernel Agent App

```bash
# Clone the repository and move to the root
cd sk-single-agent

# Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1    # (on Windows PowerShell)

# Install required Python dependencies
pip install -r requirements.txt

# Log in to Azure with tenant ID 
az login --tenant "<tenant-id>"

# To run the app with CLI/terminal interface:
python appchainlit.py

# To launch the Chainlit web UI:
chainlit run appchainlit.py
```

## 2. Deploy Azure Function App for Inventory Retrieval (api_function_app/)
This serverless Azure Function exposes shop inventory data via a REST API.
It simulates retrieving real-time data from an external service or third-party API, allowing the agent to provide up-to-date information about available toys, souvenirs, prices, and stock in the themepark shops.

Why is this useful?
- Allows demos to showcase agent-driven external API orchestration.
- Mimics connecting to live inventory, ticketing, or external business systems.
- Decouples backend data source from agent logic—easily swappable for real APIs.

### Deploy Function Locally for testing (CLI Steps) 
``` bash
# Move to the function app directory
cd api_function_app

# Create and activate a virtual environment
uv venv
.venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Log in to Azure with Tenant ID 
az login --tenant "<tenant-id>"

# Install Azure Functions Core Tools if not already installed
npm install -g azure-functions-core-tools@4 --unsafe-perm true
$env:Path += ";C:\Users\$env:USERNAME\AppData\Roaming\npm"
func --version

# Initialize a new Python function app (if not already done)
func init --worker-runtime python

# Create a new HTTP-triggered function (if not already done)
func new --name <function-name> --template "HTTP trigger" --authlevel "anonymous"

# Start the function app locally for testing
func start
```
### Deploy the Function App to Azure (from CLI and Azure sidebar) 
1. Using the Azure sidebar in VS Code or Portal:
- Create a new Azure Functions App resource in Azure (Under subscription)  

2. Publish function to Azure Function App 
``` bash 
func azure functionapp publish <Function-app-name>
```

