from flask import Flask, jsonify, request, redirect, url_for
import json
import requests
import os
import asyncio 
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import AzureChatPromptExecutionSettings
 
# Import your workflow plugins
from sk_plugins.web_search import GoogleWebSearch
from sk_plugins.ai_search import AiSearch
from sk_plugins.generate_plot import FundPlotPlugin

from dotenv import load_dotenv

app = Flask(__name__)
# Load environment variables from .env file
load_dotenv()
 
# Retrieve Azure OpenAI configuration from environment variables
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
AZURE_OPENAI_PROMPT = os.getenv("AZURE_OPENAI_PROMPT")
history = ChatHistory()

kernel = Kernel()

chat_completion = AzureChatCompletion(
            deployment_name=AZURE_OPENAI_DEPLOYMENT,
            api_key=AZURE_OPENAI_API_KEY,
            base_url=AZURE_OPENAI_ENDPOINT,
            api_version=AZURE_OPENAI_API_VERSION,
        )
kernel.add_service(chat_completion)

settings = AzureChatPromptExecutionSettings()
settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

system_prompt = AZURE_OPENAI_PROMPT
history.add_system_message(system_prompt)

kernel.add_plugin(AiSearch(), plugin_name="ai_search")
kernel.add_plugin(GoogleWebSearch(), plugin_name="web_search")
kernel.add_plugin(FundPlotPlugin(), plugin_name="fund_plot")




@app.route('/api', methods=['POST'])
async def index():
    data = request.get_json()
    message = data['message']
    if not message:
        return jsonify({"error": "The 'message' key cannot be empty."}), 400
    # Execute the workflow with the provided query
    try:
        history.add_user_message(message)
        response = await chat_completion.get_chat_message_content(
                chat_history=history,
                settings=settings,
                kernel=kernel,
            )
        history.add_assistant_message(str(response))
        print(f"Response: {str(response)}")
        return jsonify({"result": str(response)}) , 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    



if __name__ == '__main__':
    app.run(debug=True)