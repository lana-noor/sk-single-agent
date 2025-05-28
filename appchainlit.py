import os
import asyncio
import logging
from typing import Optional, Tuple
import chainlit as cl
 
# Import Semantic Kernel and Azure OpenAI classes
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import AzureChatPromptExecutionSettings
 
# Import your workflow plugins
from sk_plugins.web_search import GoogleWebSearch
from sk_plugins.ai_search import AiSearch
from sk_plugins.ai_search_index2 import AiSearchIndex2
 
from dotenv import load_dotenv
 
# -------------------------------
# Configuration and Environment Setup
# -------------------------------
 
# Configure logging to output timestamps, level, and message
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
 
# Load environment variables from .env file (for API keys and endpoints)
load_dotenv()
 
# Retrieve Azure OpenAI configuration from environment variables
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
AZURE_OPENAI_PROMPT = os.getenv("AZURE_OPENAI_PROMPT")
 
history = ChatHistory()
# -------------------------------
# Kernel Initialization and Plugin Registration
# -------------------------------
 
def initialize_kernel() -> Tuple[Kernel, AzureChatCompletion]:
    """
    Initialize the Semantic Kernel with Azure OpenAI service and register workflow plugins.
   
    Returns:
        A tuple containing:
         - kernel: The initialized Semantic Kernel instance.
         - chat_completion: The AzureChatCompletion service instance.
    """
    kernel = Kernel()
 
    try:
        # Initialize and add the Azure Chat Completion service to the kernel
        chat_completion = AzureChatCompletion(
            deployment_name=AZURE_OPENAI_DEPLOYMENT,
            api_key=AZURE_OPENAI_API_KEY,
            base_url=AZURE_OPENAI_ENDPOINT,
            api_version=AZURE_OPENAI_API_VERSION
        )
        kernel.add_service(chat_completion)
        logging.info("Azure OpenAI chat completion service added.")
    except Exception as e:
        logging.error(f"Error initializing Azure OpenAI service: {e}")
        raise e
 
    try:
        # Register all workflow plugins with the kernel
        kernel.add_plugin(AiSearchIndex2(), plugin_name="ai_search_index2")
        kernel.add_plugin(AiSearch(), plugin_name="ai_search")
        kernel.add_plugin(GoogleWebSearch(), plugin_name="web_search")

        logging.info("All workflow plugins registered successfully.")
    except Exception as e:
        logging.error(f"Error registering plugins: {e}")
        raise e
 
    return kernel, chat_completion
 
# -------------------------------
# Execution Settings Setup
# -------------------------------
 
def setup_execution_settings() -> AzureChatPromptExecutionSettings:
    """
    Set up and return the execution settings for the Azure chat prompt.
   
    Returns:
        An AzureChatPromptExecutionSettings instance with auto function choice behavior.
    """
    settings = AzureChatPromptExecutionSettings()
    settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
    return settings
 
# -------------------------------
# Interactive Chat Loop with Streaming Response
# -------------------------------
 
 
async def interactive_chat(
    kernel: Kernel,
    execution_settings: AzureChatPromptExecutionSettings,
    chat_completion: AzureChatCompletion,
) -> None:
    """
    Main interactive chat loop that handles user input and outputs AI responses using streaming.
   
    Args:
        kernel: The initialized Semantic Kernel.
        execution_settings: The execution settings for Azure OpenAI.
        chat_completion: The AzureChatCompletion service instance.
    """
 
 
    # Define the system prompt to set context and guidelines for the AI assistant
    system_prompt = AZURE_OPENAI_PROMPT
    history.add_system_message(system_prompt)
 
    # Start the interactive chat loop
    while True:
        try:
            # Read user input from command line
            user_input: Optional[str] = input("User > ").strip()
        except Exception as e:
            logging.error(f"Error reading input: {e}")
            continue
 
        # Terminate loop if user types 'exit'
        if user_input.lower() == "exit":
            logging.info("User requested exit. Terminating chat.")
            break
 
        # Warn if input is empty and skip processing
        if not user_input:
            logging.warning("Empty input received. Please provide a valid request.")
            continue
 
        # Add the user's message to chat history
        history.add_user_message(user_input)
 
        try:
            # Request a streaming response from Azure OpenAI
            response = chat_completion.get_streaming_chat_message_content(
                chat_history=history,
                settings=execution_settings,
                kernel=kernel,
            )
            # Initialize a variable to accumulate the full response
            assistant_message = ""
            # Process and display response chunks as they are received
            async for chunk in response:
                text_chunk = str(chunk)  # Ensure chunk is a string
                print(text_chunk, end="", flush=True)
                assistant_message += text_chunk
        except Exception as e:
            logging.error(f"Error during streaming chat completion: {e}")
            assistant_message = "An error occurred while processing your request. Please try again."
 
        # Print a new line after streaming completes
        print()
        # Add the complete assistant message to the chat history
        history.add_message({"role": "assistant", "content": assistant_message})
 
# -------------------------------
# Main Function: Entry Point of the Application
# -------------------------------
 
async def main() -> None:
    """
    Main entry point of the application.
   
    It initializes the kernel, sets up execution settings, and starts the interactive chat loop.
    """
    logging.info("Starting ITSM AI-Powered Workflow Automation App.")
    # Initialize Semantic Kernel and chat completion service
    kernel, chat_completion = initialize_kernel()
    # Set up Azure chat prompt execution settings
    execution_settings = setup_execution_settings()
    # Start the interactive chat loop with streaming response
    await interactive_chat(kernel, execution_settings, chat_completion)
    logging.info("Chat session ended.")
 
# -------------------------------
# Application Runner
# -------------------------------
 
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"Application terminated with error: {e}")
 
history.add_system_message(AZURE_OPENAI_PROMPT)

@cl.on_chat_start
async def on_chat_start():    
    historychainlit = ChatHistory()
    historychainlit.add_system_message(AZURE_OPENAI_PROMPT)
    cl.user_session.set(cl.user_session.get("id"), historychainlit)
    print("========= on_chat_start ==========")
    
    print(cl.user_session.get("id"))
   
 
@cl.on_message
async def handle_message(message: cl.Message):
    """
    Handles incoming user messages using Chainlit.
    Calls Semantic Kernel with the user query and returns the response.
    """
    
    historychainlit = cl.user_session.get(cl.user_session.get("id"))
    print("========= on_message ==========")
    user_input = message.content.strip()
 
    # Initialize Semantic Kernel and Chat Service
    kernel, chat_completion = initialize_kernel()
    settings = setup_execution_settings()
   
    # Maintain chat history
    historychainlit.add_user_message(user_input)
   
 
    # Get AI response
    result = await chat_completion.get_chat_message_content(
        chat_history=historychainlit,
        settings=settings,
        kernel=kernel,
    )
 
    response_text = str(result)  # Convert response to string
    historychainlit.add_message({"role": "assistant", "content": response_text})
    #await cl.Message(content=response_text).send()
    # If response is a base64 image, show it as an image element
    if response_text.startswith("data:image/png;base64,"):
        await cl.Message(
            content="Here is the generated plot:",
            elements=[
                cl.Image(
                    name="Financial Plot",
                    display="inline",
                    image=response_text  # this is the base64 image string
                )
            ]
        ).send()
    else:
        # If it's a regular text response
        await cl.Message(content=response_text).send()
