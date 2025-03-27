from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
import traceback
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

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

@app.route('/api/analyze-startup', methods=['POST', 'OPTIONS'])
def analyze_startup():
    # Handle preflight requests
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        return response

    if not request.is_json:
        logger.error("Request Content-Type is not application/json")
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    try:
        startup_data = request.get_json()
        logger.info(f"Received request for startup: {startup_data.get('startup_name', 'unknown')}")
        logger.debug(f"Received data: {json.dumps(startup_data, indent=2)}")
        
        # Validate required fields
        required_fields = ['startup_name', 'industry', 'country']
        missing_fields = [field for field in required_fields if field not in startup_data]
        if missing_fields:
            error_msg = f'Missing required fields: {", ".join(missing_fields)}'
            logger.error(error_msg)
            return jsonify({'error': error_msg}), 400
        
        # Create the prompt
        prompt = create_analysis_prompt(startup_data)
        logger.debug(f"Generated prompt: {prompt}")
        
        try:
            # Generate response with Gemini
            logger.info("Sending request to Gemini API")
            response = model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 1,
                    'top_k': 32,
                    'max_output_tokens': 2048,
                }
            )
            
            # Get the response text and clean it
            analysis_text = response.text.strip()
            logger.debug(f"Raw Gemini response: {analysis_text}")
            
            # Remove any markdown formatting if present
            if analysis_text.startswith("```json"):
                analysis_text = analysis_text[7:]
            if analysis_text.endswith("```"):
                analysis_text = analysis_text[:-3]
            analysis_text = analysis_text.strip()
            
            try:
                # Parse the response as JSON
                analysis_data = json.loads(analysis_text)
                logger.debug(f"Parsed JSON response: {json.dumps(analysis_data, indent=2)}")
                
                # Validate the response structure
                required_keys = ['executive_summary', 'follow_up_items']
                if not all(key in analysis_data for key in required_keys):
                    raise ValueError("Invalid response structure from AI model")
                
                response = jsonify(analysis_data)
                response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
                logger.info("Successfully generated and returned analysis")
                return response
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response as JSON: {str(e)}")
                logger.error(f"Response text: {analysis_text}")
                return jsonify({
                    'error': 'Failed to parse AI response',
                    'details': str(e)
                }), 500
                
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'error': 'Error generating AI analysis',
                'details': str(e)
            }), 500
            
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

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