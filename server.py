from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
from google.generativeai import types
import json
import logging
from chat_agent import get_agent_response
import asyncio
import os
import traceback
from functools import wraps
from pathlib import Path
import subprocess
import html
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'), # Log server events
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configure Flask app
app = Flask(__name__, static_folder='.', static_url_path='')

# Configure CORS properly
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:8000", 
            "http://127.0.0.1:8000",
            "https://andrewankenobi.github.io",
            "https://andrewankenobi.github.io/GFSA"
        ],
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

# --- Define Lock File Path (must match research.py) --- START
LOCK_FILE_PATH = Path('data') / '.research.lock'
# --- Define Lock File Path --- END

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
    """Format the response text with HTML escaping for chat-like appearance."""
    lines = text.split('\n')
    result = []
    in_list = False

    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:  # Handle blank lines
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append('<br>')
            continue

        # Escape the content BEFORE wrapping in tags
        escaped_content = html.escape(stripped_line)

        if stripped_line.startswith('- '):
            if not in_list:
                result.append('<ul class="chat-list">')
                in_list = True
            # Escape the content after the list marker
            list_content = html.escape(stripped_line[2:])
            # Allow <strong> tags through
            list_content = list_content.replace('&lt;strong&gt;', '<strong>').replace('&lt;/strong&gt;', '</strong>')
            result.append(f'<li>{list_content}</li>')
        else:
            if in_list:
                result.append('</ul>')
                in_list = False
            # Allow <strong> tags through
            escaped_content = escaped_content.replace('&lt;strong&gt;', '<strong>').replace('&lt;/strong&gt;', '</strong>')
            result.append(f'<p>{escaped_content}</p>')

    if in_list:
        result.append('</ul>')

    # Return only the joined inner HTML elements
    return '\n'.join(result)

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
def chat():
    try:
        data = request.get_json()
        logger.info("Received chat request")

        if 'user_input' not in data:
            logger.error("Missing 'user_input' key in chat request data: %s", data)
            return jsonify({'error': 'Missing user_input in request'}), 400

        user_message = data['user_input']
        startup_context = data.get('startup_context')

        logger.info(f"Chat request for startup: {startup_context.get('metadata', {}).get('startup_name', 'Unknown')} with input: {user_message[:50]}...")

        if not startup_context:
            logger.warning("Chat request received without startup_context.")

        # Call the agent function directly (no await)
        response_text = get_agent_response(
            user_query=user_message,
            startup_context=startup_context
        )

        # Format the response with HTML escaping
        formatted_response = format_response(response_text)

        return jsonify({
            'response': formatted_response, # Return the formatted HTML
            # 'raw_response': response_text # Optionally keep raw for debugging
        })

    except Exception as e:
        logger.error("Error in chat endpoint: %s", str(e), exc_info=True)
        return jsonify({'error': f'An internal server error occurred: {str(e)}'}), 500

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/api/run-research', methods=['POST'])
def run_research():
    """
    Endpoint to trigger the research.py script for a specific startup.
    Runs the script as a background process.
    """
    try:
        data = request.get_json()
        startup_name = data.get('startup_name')
        workers = data.get('workers', 1) # Default to 1 worker if not provided

        if not startup_name:
            logger.error("Missing 'startup_name' in /api/run-research request")
            return jsonify({'error': "Missing 'startup_name' parameter"}), 400

        # Validate workers to be an integer
        try:
            workers = int(workers)
        except (ValueError, TypeError):
            logger.error(f"Invalid 'workers' value received: {workers}")
            return jsonify({'error': "Invalid 'workers' parameter, must be an integer"}), 400

        # --- Check for existing lock file --- START
        if LOCK_FILE_PATH.exists():
            logger.warning(f"Research lock file {LOCK_FILE_PATH} exists. Preventing concurrent run.")
            # Return 409 Conflict status code
            return jsonify({'error': 'Another research process is already running. Please wait.'}), 409
        # --- Check for existing lock file --- END

        # Construct the command
        # Use sys.executable to ensure the correct Python interpreter is used
        command = [
            sys.executable, # Use the same python that's running the server
            'research.py',
            '--startup', startup_name,
            '--workers', str(workers)
        ]
        
        logger.info(f"Executing command: {' '.join(command)}")

        # Run the command as a background process
        # Use Popen for non-blocking execution
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # We don't wait for completion here (process.wait())
        # Return immediately to the client
        logger.info(f"Started background research process for {startup_name} with PID: {process.pid}")
        
        # Return 202 Accepted: The request has been accepted for processing,
        # but the processing has not been completed.
        return jsonify({
            'message': f'Research process started successfully for {startup_name}.',
            'pid': process.pid 
        }), 202

    except FileNotFoundError as e:
        logger.error(f"Error starting research process: {e}. Is research.py in the correct path? Is Python installed?", exc_info=True)
        return jsonify({'error': 'Failed to start research process. Script or interpreter not found.', 'details': str(e)}), 500
    except Exception as e:
        logger.error(f"Error in /api/run-research endpoint: {str(e)}", exc_info=True)
        return jsonify({'error': f'An internal server error occurred: {str(e)}'}), 500

@app.route('/api/research-status', methods=['GET'])
def get_research_status():
    """Checks the status of a specific research process."""
    startup_name = request.args.get('startup')
    if not startup_name:
        return jsonify({'error': 'Missing startup parameter'}), 400

    startup_dir_name = startup_name.lower().replace(' ', '_')
    status_file = Path('data') / f'.research_status_{startup_dir_name}.json'

    if status_file.exists():
        try:
            with open(status_file, 'r') as f:
                status_data = json.load(f)
            status_data['is_running'] = True
            return jsonify(status_data), 200
        except Exception as e:
            logger.error(f"Error reading status file {status_file}: {e}")
            # Return error but indicate it might still be running
            return jsonify({'error': 'Could not read status file', 'is_running': True}), 500
    else:
        # If status file doesn't exist, assume it's not running or completed
        return jsonify({'is_running': False, 'status': 'not_running_or_completed'}), 200

@app.route('/details.html')
def details():
    return send_from_directory('.', 'details.html')

@app.route('/data/results/<path:filename>')
def serve_analysis_file(filename):
    # Basic security: prevent directory traversal
    if '..' in filename or filename.startswith('/'):
        logger.warning(f"Attempted directory traversal: {filename}")
        return "Invalid path", 400
    safe_path = os.path.join('data', 'results', filename)
    logger.info(f"Serving analysis file: {safe_path}")
    # Use send_from_directory for safer file serving
    return send_from_directory(os.path.join('data', 'results'), filename)

@app.route('/startups.json')
def serve_startups_list():
    logger.info("Serving startups.json list")
    return send_from_directory('.', 'startups.json')

@app.route('/<path:filename>')
def serve_static(filename):
    # Basic security: prevent serving sensitive files
    if filename.endswith('.py') or filename.endswith('.env') or '..' in filename or filename.startswith('/'):
        logger.warning(f"Attempted access to restricted file: {filename}")
        return "Access denied", 403
    return send_from_directory('.', filename)

if __name__ == '__main__':
    # Make sure log directory exists relative to script location or CWD
    log_dir = Path('logs')
    try:
        log_dir.mkdir(exist_ok=True)
        # Update FileHandler paths if logging to a specific directory
        # Note: FileHandler paths need adjustment if logs are intended for 'logs/' folder
        # e.g., logging.FileHandler(log_dir / 'server.log')
    except OSError as e:
         logger.error(f"Could not create log directory {log_dir}: {e}")

    # Change the default port to 5002
    port = int(os.environ.get('PORT', 5002))
    logger.info(f"Starting Flask server on http://0.0.0.0:{port}")
    # Set debug=False for production if desired
    app.run(debug=True, host='0.0.0.0', port=port) 