import asyncio

from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.filters import FunctionInvocationContext
from dotenv import load_dotenv
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior, FunctionChoiceType
import os
import chainlit as cl

# Import your workflow plugins
from sk_plugins.web_search import GoogleWebSearch
from sk_plugins.ai_search_index import AiSearch
from sk_plugins.ai_search_index_2 import AiSearch2
from sk_plugins.api_inventory import Inventory

# Load environment variables from .env file (for API keys and endpoints)
load_dotenv()
 
# Retrieve Azure OpenAI configuration from environment variables
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
AZURE_OPENAI_PROMPT = os.getenv("AZURE_OPENAI_PROMPT")

"""
NEW: Single Agent Semantic Kernel 
Uses the new Semantic Kernel SDK with AzureChatCompletionAgent 
Added Function Invocation filter to log function calls initialized to kernel (without this service, you can create a single ChatCompletionAgent with NO kernel initialized)
Chainlit frontend 
"""

# Kernel function-invocation filter (unchanged)
async def function_invocation_filter(context: FunctionInvocationContext, next):
    if "messages" not in context.arguments:
        await next(context)
        return
    print(f"    Agent [{context.function.name}] called with messages: {context.arguments['messages']}")
    await next(context)
    print(f"    Response from agent [{context.function.name}]: {context.result.value}")

load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
deployment_name = "gpt-4.1"
openai_key = os.getenv("AZURE_OPENAI_API_KEY")
promptnew = os.getenv("AZURE_OPENAI_PROMPT_NEWAPP")

kernel = Kernel()
kernel.add_filter("function_invocation", function_invocation_filter)

single_agent = ChatCompletionAgent(
    service=AzureChatCompletion(
        deployment_name="gpt-4.1",
        api_key=openai_key,
        endpoint=endpoint,
        api_version=api_version,
    ),
    kernel=kernel,
    name="SingleAgent",
    instructions=promptnew, 
    plugins=[GoogleWebSearch(), AiSearch(), AiSearch2(), Inventory()],
)

# ---------- CLI loop (unchanged) ----------
thread: ChatHistoryAgentThread = None

async def chat() -> bool:
    try:
        user_input = input("User:> ")
    except (KeyboardInterrupt, EOFError):
        print("\n\nExiting chat...")
        return False

    if user_input.lower().strip() == "exit":
        print("\n\nExiting chat...")
        return False

    response = await single_agent.get_response(
        messages=user_input,
        thread=thread,
    )

    if response:
        print(f"Agent :> {response}")

    return True

async def main() -> None:
    print("Welcome to the chat bot!\n  Type 'exit' to exit.")
    chatting = True
    while chatting:
        chatting = await chat()

if __name__ == "__main__":
    asyncio.run(main())

# ============================
# Chainlit frontend (simple)
# ============================

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("agent", single_agent)
    cl.user_session.set("thread", ChatHistoryAgentThread())
    await cl.Message(content="Hi! Ask me about the Theme Park").send()

@cl.on_message
async def on_message(message: cl.Message):
    agent: ChatCompletionAgent = cl.user_session.get("agent")
    thread: ChatHistoryAgentThread = cl.user_session.get("thread")

    user_text = (message.content or "").strip()
    if not user_text:
        await cl.Message(content="Please enter a message.").send()
        return

    try:
        resp = await agent.get_response(messages=user_text, thread=thread)
        await cl.Message(content=str(resp) if resp else "(no response)").send()
    except Exception as e:
        await cl.Message(content=f"Error: {e}").send()
