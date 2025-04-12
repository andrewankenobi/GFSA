import logging
import os

# ---> ADDED: Top-level log
print("--- app.py script execution started ---")
logging.info("--- app.py script execution started (logger) ---")

from flask import Flask, jsonify, request, Response, abort
from flask_cors import CORS
import threading
from research import StartupResearch, load_startups
from pathlib import Path
import glob
import json

# Configure logging more verbosely for debugging paths
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
logger = logging.getLogger(__name__)

logger.info("--- Imports complete, logger configured ---")

app = Flask(__name__)
# ---> ADDED: Log after Flask object creation
logger.info(f"--- Flask app object created: {app.name} ---")
CORS(app)

# --- Simple Ping Route for Debugging --- 
# ---> ADDED: Log before route definition
logger.info("--- Defining /ping route ---")
@app.route('/ping', methods=['GET'])
def ping():
    logger.info("--- /ping route hit --- ")
    return jsonify({"message": "pong"}), 200

# --- Error Handlers --- 
logger.info("Registering 404 handler")
@app.errorhandler(404)
def not_found_error(error):
    logger.info("--- 404 Handler triggered --- ") # Log entry into handler
    error_message = str(error.description) if hasattr(error, 'description') else "Resource not found."
    # More specific logging
    logger.warning(f"Handling 404: description='{error.description}', message='{error_message}'")
    if "No analysis files found" in error_message or "Startup not found" in error_message:
         return jsonify({"error": error_message}), 404
    else:
        # Log the generic case too
        logger.warning(f"Handling 404 with generic message for description: {error.description}")
        return jsonify({"error": "The requested resource was not found."}), 404

logger.info("Registering 500 handler")
@app.errorhandler(500)
def internal_error(error):
    logger.info("--- 500 Handler triggered --- ") # Log entry into handler
    logger.error(f"Server Error: {error}", exc_info=True)
    return jsonify({"error": "An internal server error occurred."}), 500

research_in_progress = False
research_thread = None

# Determine the directory containing app.py
APP_DIR = Path(__file__).parent.resolve() # Get absolute path
RESULTS_DIR = APP_DIR / 'data' / 'results'
logger.info(f"Script directory (APP_DIR): {APP_DIR}")
logger.info(f"Results directory (RESULTS_DIR) set to: {RESULTS_DIR}")

def run_research_task():
    """Function to run the research process in a separate thread."""
    global research_in_progress
    logger.info("Research task started.")
    research_in_progress = True
    try:
        if not load_startups():
             logger.error("startups.json not found or empty. Aborting research task.")
             research_in_progress = False
             return

        researcher = StartupResearch()
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        result_file = researcher.run_research()
        if result_file:
            logger.info(f"Research task completed successfully. Results saved to: {result_file}")
        else:
            logger.warning("Research task completed, but no results were saved (or an error occurred).")
    except Exception as e:
        logger.error(f"Exception during research task: {e}", exc_info=True)
    finally:
        research_in_progress = False
        logger.info("Research task finished.")

# --- Helper to get latest analysis file path --- 
def _find_latest_analysis_file():
    logger.debug(f"Helper: Searching in absolute path: {RESULTS_DIR.resolve()}")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    glob_pattern = str(RESULTS_DIR.resolve() / 'analysis_*.json')
    analysis_files = glob.glob(glob_pattern)
    logger.debug(f"Helper: Glob found {len(analysis_files)} files: {analysis_files}")
    if not analysis_files:
        return None
    latest_file_path = max(analysis_files, key=os.path.getmtime)
    logger.debug(f"Helper: Identified latest file: {latest_file_path}")
    return Path(latest_file_path)

@app.route('/api/latest-analysis-path', methods=['GET'])
def get_latest_analysis_path():
    """Finds the most recent analysis JSON file path."""
    logger.debug(f"--- Request received for latest analysis path --- ")
    try:
        latest_file = _find_latest_analysis_file()
        if not latest_file:
            error_message = "No analysis files found in expected directory. Run refresh first."
            logger.warning(error_message)
            abort(404, description=error_message)

        relative_path = latest_file.relative_to(APP_DIR)
        logger.info(f"Returning relative path to frontend: {relative_path}")
        return jsonify({"latest_file_path": str(relative_path)}), 200
    except Exception as e:
        logger.error(f"Error in get_latest_analysis_path: {e}", exc_info=True)
        abort(500)

# --- NEW ENDPOINT --- 
@app.route('/api/get-startup-data', methods=['POST'])
def get_startup_data():
    """Gets data for a specific startup from the latest analysis file."""
    logger.debug("--- Request received for single startup data --- ")
    data = request.get_json()
    if not data or 'startup_name' not in data:
        logger.warning("Request missing startup_name in JSON body")
        return jsonify({"error": "Missing 'startup_name' in request body"}), 400

    startup_name = data['startup_name']
    logger.info(f"Request for data for startup: {startup_name}")

    try:
        latest_file = _find_latest_analysis_file()
        if not latest_file:
            error_message = "No analysis files found. Run refresh first."
            logger.warning(error_message)
            abort(404, description=error_message)

        logger.debug(f"Loading data from latest file: {latest_file}")
        with open(latest_file, 'r') as f:
            all_data = json.load(f)

        startup_data = None
        if isinstance(all_data, list):
            for item in all_data:
                 if (isinstance(item, dict) and 
                     isinstance(item.get('metadata'), dict) and 
                     item['metadata'].get('startup_name') == startup_name):
                    startup_data = item
                    break # Found it
        
        if not startup_data:
            error_message = f"Startup '{startup_name}' not found in the latest analysis file ({latest_file.name})."
            logger.warning(error_message)
            abort(404, description=error_message)

        logger.info(f"Found data for startup '{startup_name}'. Returning data.")
        return jsonify(startup_data), 200

    except FileNotFoundError:
         error_message = "Latest analysis file not found (race condition?). Run refresh first."
         logger.error(error_message, exc_info=True)
         abort(404, description=error_message)
    except json.JSONDecodeError:
        error_message = f"Error decoding JSON from latest analysis file ({latest_file.name})."
        logger.error(error_message, exc_info=True)
        abort(500, description="Failed to read analysis data.")
    except Exception as e:
        logger.error(f"Error getting data for startup '{startup_name}': {e}", exc_info=True)
        abort(500)

@app.route('/api/rerun-research', methods=['POST'])
def rerun_research():
    """API endpoint to trigger the startup research process."""
    global research_in_progress
    global research_thread
    logger.info("Received request to /api/rerun-research")
    if research_in_progress and research_thread and research_thread.is_alive():
        logger.warning("Research is already in progress.")
        return jsonify({"message": "Research process is already running."}), 409
    logger.info("Starting new research process.")
    research_thread = threading.Thread(target=run_research_task, daemon=True)
    research_thread.start()
    return jsonify({"message": "Startup research process initiated."}), 202

@app.route('/api/research-status', methods=['GET'])
def research_status():
    """API endpoint to check the status of the research process."""
    global research_in_progress, research_thread
    status = "idle"
    if research_in_progress and research_thread and research_thread.is_alive():
        status = "running"
    logger.info(f"Reporting research status: {status}")
    return jsonify({"status": status}), 200

logger.info("App route definitions and handlers should be registered now.")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    # Aligning debug=True with observed logs, though the root cause is likely elsewhere
    logger.info(f"Starting Flask server on http://0.0.0.0:{port} with debug=True")
    app.run(host='0.0.0.0', port=port, debug=True) 