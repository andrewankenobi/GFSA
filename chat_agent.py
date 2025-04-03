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

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Initialize Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash')

# Load startup data
def get_latest_analysis_file():
    import glob
    import os
    import shutil
    pattern = 'data/results/analysis_*.json'
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError(f'No analysis files found matching pattern: {pattern}')
    latest_file = max(files, key=os.path.getctime)
    root_copy = 'analysis_20250327_084704.json'
    shutil.copy2(latest_file, root_copy)
    return latest_file

with open(get_latest_analysis_file(), 'r') as f:
    STARTUP_DATA = json.load(f)

# Create a dictionary for quick startup lookups
STARTUP_DICT = {startup['metadata']['startup_name']: startup for startup in STARTUP_DATA}

class StartupSearchTool(Tool):
    def __init__(self):
        super().__init__(
            name="Startup Search",
            func=self.search_startups,
            description="Search for information about startups in our database"
        )
    
    def search_startups(self, query: str) -> str:
        results = []
        query = query.lower()
        for startup in STARTUP_DATA:
            if (query in startup['metadata']['startup_name'].lower() or 
                query in startup['analysis']['company_overview'].get('description', '').lower() or
                query in startup['metadata'].get('industry', '').lower()):
                results.append(startup)
        
        if not results:
            return "No startups found matching your query."
        
        return json.dumps(results, indent=2)

class GeminiAgent:
    def __init__(self):
        self.model = model
        self.startup_search = StartupSearchTool()
        self.memory = []

    def _create_prompt(self, query: str, startup_context: dict = None) -> str:
        context = ""
        if startup_context:
            context = f"""
Current startup context:
Name: {startup_context['metadata']['startup_name']}
Industry: {startup_context['metadata']['industry']}
Description: {startup_context['analysis']['company_overview']['description']}
"""

        # Base system prompt that guides the agent's behavior
        system_prompt = """You are an expert startup analyst assistant having a natural conversation with the user. Follow these guidelines:

1. Keep responses conversational and concise (2-3 short paragraphs max)

2. Structure your responses naturally:
   - Brief introduction or acknowledgment
   - 2-3 main points or suggestions
   - One follow-up question to continue the conversation

3. Use minimal formatting:
   - Only use plain text (no bold or italic)
   - Use - for bullet point lists (keep lists to 3 items max)
   - Add a blank line between main points

4. When making suggestions:
   - Keep them focused and specific
   - Briefly explain why each suggestion matters
   - Connect them to the startup's context

5. Be conversational:
   - Use natural language
   - Avoid technical jargon unless necessary
   - Ask engaging follow-up questions

Remember: Write as if you're having a friendly chat with a colleague - clear, helpful, and engaging."""

        # Combine system prompt with context and conversation history
        prompt = f"""{system_prompt}

{context}

Previous conversation:
{self._format_memory()}

User query: {query}

Provide a natural, conversational response that keeps the discussion going."""

        return prompt

    def _format_memory(self) -> str:
        if not self.memory:
            return "No previous conversation."
        # Only keep last 3 exchanges for context
        return "\n".join([f"User: {q}\nAssistant: {a}" for q, a in self.memory[-3:]])

    async def get_response(self, query: str, startup_context: dict = None) -> str:
        try:
            prompt = self._create_prompt(query, startup_context)
            
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 1,
                    'top_k': 32,
                    'max_output_tokens': 1000,  # Reduced for more focused responses
                },
                safety_settings={
                    'HARM_CATEGORY_HARASSMENT': 'block_none',
                    'HARM_CATEGORY_HATE_SPEECH': 'block_none',
                    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'block_none',
                    'HARM_CATEGORY_DANGEROUS_CONTENT': 'block_none'
                }
            )

            # Store in memory
            self.memory.append((query, response.text))
            
            return response.text

        except Exception as e:
            return f"Error generating response: {str(e)}"

    def search_startup(self, query: str) -> dict:
        """Search for a startup in the database."""
        return self.startup_search.search_startups(query)

# Create a singleton instance
agent = GeminiAgent()

async def get_agent_response(query: str, startup_context: dict = None) -> str:
    """Get a response from the agent."""
    return await agent.get_response(query, startup_context)

if __name__ == "__main__":
    print("Startup Analysis Assistant initialized! Ask me anything about the startups or related topics.")
    print("Type 'quit' to exit.")
    
    while True:
        query = input("\nYou: ")
        if query.lower() == 'quit':
            break
        
        response = get_agent_response(query)
        print("\nAssistant:", response) 