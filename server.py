from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
from google.generativeai import types
import json
import logging
from chat_agent import agent, get_agent_response
import asyncio
import os
import traceback
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Flask app
app = Flask(__name__, static_folder='.')

# Configure CORS properly
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8000", "http://127.0.0.1:8000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"]
    }
})

# Configure Gemini
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

try:
    # Initialize Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    logger.info("Successfully configured Gemini API")
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {str(e)}")
    raise

def create_analysis_prompt(startup_data):
    # Convert complex objects to pretty-printed JSON strings
    product_info = json.dumps(startup_data.get('product_info', {}), indent=2, default=str)
    market_info = json.dumps(startup_data.get('market_info', {}), indent=2, default=str)
    business_model = json.dumps(startup_data.get('business_model', {}), indent=2, default=str)
    
    return f"""You are an AI analyst tasked with analyzing a startup. Provide a structured analysis in JSON format.

STARTUP INFORMATION:
Name: {startup_data.get('startup_name')}
Industry: {startup_data.get('industry')}
Country: {startup_data.get('country')}
Description: {startup_data.get('description')}

PRODUCT INFORMATION:
{product_info}

MARKET INFORMATION:
{market_info}

BUSINESS MODEL:
{business_model}

INSTRUCTIONS:
1. Analyze the data and provide insights in the following areas:
   - Market opportunity
   - Competitive advantages
   - Growth potential
   - Risk factors

2. Provide specific follow-up items in both technical and business categories.

RESPONSE FORMAT:
Return ONLY a valid JSON object with this exact structure:
{{
    "executive_summary": {{
        "market_opportunity": "Clear analysis of the market opportunity",
        "competitive_advantage": "Analysis of the company's competitive advantages",
        "growth_trajectory": "Assessment of growth potential",
        "risk_assessment": "Key risks and challenges"
    }},
    "follow_up_items": [
        {{
            "category": "Technical",
            "title": "Specific technical item to discuss",
            "description": "Detailed description of the technical item",
            "priority": "High or Medium",
            "key_points": ["Point 1", "Point 2", "Point 3"]
        }},
        {{
            "category": "Business",
            "title": "Specific business item to discuss",
            "description": "Detailed description of the business item",
            "priority": "High or Medium",
            "key_points": ["Point 1", "Point 2", "Point 3"]
        }}
    ]
}}

IMPORTANT: 
- Return ONLY the JSON object, no other text
- Ensure the JSON is properly formatted
- Do not include any markdown formatting"""

def format_response(text):
    """Format the response text with minimal HTML for chat-like appearance."""
    # Handle bullet points and paragraphs
    lines = text.split('\n')
    result = []
    in_list = False
    
    for line in lines:
        line = line.strip()
        if not line:  # Handle blank lines
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append('<br>')
            continue
            
        if line.startswith('- '):
            if not in_list:
                result.append('<ul class="chat-list">')
                in_list = True
            result.append(f'<li>{line[2:]}</li>')
        else:
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append(f'<p>{line}</p>')
    
    if in_list:
        result.append('</ul>')
    
    return '<div class="chat-message">' + '\n'.join(result) + '</div>'

def async_route(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()
    return wrapper

@app.route('/api/analyze-startup', methods=['POST'])
def analyze_startup():
    try:
        data = request.get_json()
        logger.info("Received analysis request for startup: %s", data.get('startup_name'))

        # Validate request data
        required_fields = ['startup_name', 'industry', 'description']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        # Create detailed analysis prompt
        prompt = create_analysis_prompt(data)

        # Generate response using Gemini
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.7,
                'top_p': 1,
                'top_k': 32,
                'max_output_tokens': 2048,
            },
            safety_settings={
                'HARM_CATEGORY_HARASSMENT': 'block_none',
                'HARM_CATEGORY_HATE_SPEECH': 'block_none',
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'block_none',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'block_none'
            }
        )

        try:
            # Clean the response text to handle markdown formatting
            response_text = response.text.strip()
            
            # Remove markdown code block markers if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parse the cleaned response as JSON
            analysis_result = json.loads(response_text)
            
            # Validate the response structure
            required_keys = ['executive_summary', 'follow_up_items']
            if not all(key in analysis_result for key in required_keys):
                raise ValueError("Invalid response structure from AI model")
            
            return jsonify(analysis_result)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {str(e)}")
            logger.error(f"Response text: {response.text}")
            return jsonify({
                'error': 'Failed to parse AI response',
                'details': str(e)
            }), 500

    except Exception as e:
        logger.error("Error analyzing startup: %s", str(e), exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
@async_route
async def chat():
    try:
        data = request.get_json()
        logger.info("Received chat request with query: %s", data.get('query'))

        # Validate request data
        if 'query' not in data:
            return jsonify({'error': 'Missing query in request'}), 400

        # Get response from the agent
        response = await get_agent_response(
            query=data['query'],
            startup_context=data.get('startup_context')
        )

        # Format the response with HTML
        formatted_response = format_response(response)

        return jsonify({
            'response': formatted_response,
            'raw_response': response  # Include raw response for debugging
        })

    except Exception as e:
        logger.error("Error in chat endpoint: %s", str(e), exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    try:
        port = int(os.getenv('PORT', 5000))
        logger.info(f"Starting server on port {port}")
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        logger.error(traceback.format_exc()) 