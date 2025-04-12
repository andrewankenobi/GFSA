from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import StringPromptTemplate
from langchain.chains import LLMChain
from langchain.schema import AgentAction, AgentFinish
import google.generativeai as genai
from google.generativeai import types
from typing import List, Union, Tuple
import re
import json
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chat_agent.log'), # Log to a separate file
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Configure Gemini
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    logger.error("GEMINI_API_KEY not found in environment variables")
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Initialize Gemini
genai.configure(api_key=api_key)

# Initialize the generative model directly (needed by get_agent_response)
try:
    model = genai.GenerativeModel('gemini-2.0-flash')
    logger.info(f"Chat agent model initialized: {model.model_name}")
except Exception as e:
    logger.error(f"Failed to initialize generative model: {e}")
    model = None # Handle inability to create model

def get_agent_response(user_query: str, startup_context: dict):
    """Generates a response from the chatbot based on the user query and startup context."""
    logger.info(f"Received query: '{user_query}' for startup: {startup_context.get('metadata', {}).get('startup_name', 'Unknown')}")

    if not model:
        logger.error("Chat model not initialized. Cannot generate response.")
        return "Error: The chat model is currently unavailable."

    if not startup_context or not isinstance(startup_context, dict):
        logger.error("Invalid or missing startup_context provided.")
        return "Error: Could not load the context for this startup to answer the question."

    # Define the system prompt (moved inside function for clarity or keep global if preferred)
    SYSTEM_PROMPT = (
        "You are Ment-hoff, a helpful AI assistant specialized in analyzing startup information "
        "based on provided context data from the Google for Startups AI First 2025 Berlin Cohort analysis. "
        "Your goal is to answer questions accurately and concisely about the specific startup context you are given. "
        "If the answer is not available in the provided context, clearly state that the information is not available in the analysis data. "
        "Do not hallucinate or make up information. Stick strictly to the provided JSON context for the startup."
    )

    # Construct the prompt with context
    context_str = json.dumps(startup_context, indent=2)
    prompt = f"{SYSTEM_PROMPT}\n\nStartup Context Data:\n```json\n{context_str}\n```\n\nUser Query: {user_query}\n\nMent-hoff Response:"

    try:
        # Generate content using the model
        response = model.generate_content(prompt)

        # Extract the text response
        agent_response = response.text

        logger.info(f"Generated response: '{agent_response[:100]}...'")
        return agent_response

    except Exception as e:
        logger.error(f"Error generating content from model: {e}")
        logger.exception("Traceback for model generation error:")
        # Check for specific API errors if needed
        try:
             if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                  logger.error(f"Content blocked: {response.prompt_feedback.block_reason}")
                  return f"Sorry, my response was blocked due to: {response.prompt_feedback.block_reason}"
        except Exception as feedback_error:
             logger.error(f"Error accessing prompt feedback: {feedback_error}")

        return f"Sorry, I encountered an error while processing your request: {e}"

if __name__ == "__main__":
    print("Chat Agent module loaded. Use server.py to interact or run local tests.")
    # Example of how to test locally:
    # try:
    #     sample_file_path = 'data/results/analysis_hybr.json' # Choose a file
    #     with open(sample_file_path, 'r') as f:
    #         test_context = json.load(f)
    #     if model and test_context:
    #          print(f"\n--- Local Test (using {sample_file_path}) ---")
    #          while True:
    #              query = input("\nYou (type 'quit' to exit test): ")
    #              if query.lower() == 'quit':
    #                  break
    #              response = get_agent_response(query, test_context)
    #              print("\nMent-hoff:", response)
    #     else:
    #          print("Model not initialized or test context not loaded.")
    # except FileNotFoundError:
    #     print(f"Test context file not found: {sample_file_path}")
    # except Exception as e:
    #     print(f"Error in local test setup: {e}") 