import os
import json
import glob
from flask import Flask, render_template, request, jsonify
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import types

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Constants
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
REFINED_DATA_DIR = os.path.join(DATA_DIR, "refined")

# Get the latest reference file
def get_latest_reference_file():
    files = glob.glob(os.path.join(REFINED_DATA_DIR, "startup_reference_*.json"))
    if not files:
        return None
    return max(files, key=os.path.getctime)

# Load the startup data
def load_startup_data():
    try:
        reference_file = get_latest_reference_file()
        if not reference_file:
            print("No reference file found")
            return {}
        
        print(f"Loading startup data from: {reference_file}")
        with open(reference_file, 'r') as f:
            data = json.load(f)
            # Handle the nested 'startups' key in the reference file
            if 'startups' in data:
                startups = data['startups']
                print(f"Loaded {len(startups)} startups")
                return startups
            else:
                print("No 'startups' key found in the reference file")
                return {}
    except Exception as e:
        print(f"Error loading startup data: {str(e)}")
        return {}

# Process chat query with Gemini
def process_chat_query(query, startup_name=None):
    # Configure the API key
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    
    # Load the startup data to use as context
    startup_data = load_startup_data()
    
    # Create a context with all startups or focused on a specific one
    if startup_name and startup_name in startup_data:
        context = f"Information about {startup_name}:\n"
        context += json.dumps(startup_data[startup_name], indent=2)
        
        # Add a bit of info about other startups for cross-referencing
        context += "\n\nOther startups in the database:\n"
        for name, data in startup_data.items():
            if name != startup_name:
                context += f"- {name}: {data['startup']['name']} ({data['startup']['industry']})\n"
    else:
        # Summarize all startups
        context = "Information about all startups in the database:\n"
        for name, data in startup_data.items():
            context += f"\n--- {data['startup']['name']} ---\n"
            context += f"Industry: {data['startup']['industry']}\n"
            context += f"Country: {data['startup']['country']}\n"
            if data['startup'].get('website'):
                context += f"Website: {data['startup']['website']}\n"
            
            # Add a brief summary
            if "1. EXECUTIVE SUMMARY" in data['analysis']['analysis']:
                summary = data['analysis']['analysis']["1. EXECUTIVE SUMMARY"]
                context += f"Core Business: {summary.get('Core Business Description', 'Not available')[:100]}...\n"
    
    # Prepare the prompt
    prompt = f"""You are a startup analysis assistant. Use the following information to answer the question.
    
Context:
{context}

Question: {query}

Answer in a concise, professional manner. If comparing startups, focus on objective criteria. 
If information isn't available in the context, say so rather than making it up.
"""

    # Initialize the Gemini model following research pipeline pattern
    model = genai.GenerativeModel(
        'gemini-2.0-flash',
        generation_config={
            "temperature": 0.2,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,  # Maximum available
        }
    )
    
    # Generate content
    response = model.generate_content(prompt)
    
    return response.text

# Routes
@app.route('/')
def index():
    startups = load_startup_data()
    return render_template('index.html', startups=startups)

@app.route('/startup/<name>')
def startup_detail(name):
    startups = load_startup_data()
    if name not in startups:
        return "Startup not found", 404
    
    startup_data = startups[name]
    print(f"Startup data structure: {startup_data.keys()}")
    return render_template('detail.html', name=name, data=startup_data)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    query = data.get('query', '')
    startup_name = data.get('startup_name', None)
    
    try:
        response = process_chat_query(query, startup_name)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Ensure the templates directory exists
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"), exist_ok=True)
    app.run(debug=True) 