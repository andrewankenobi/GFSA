import sys
print("--- research.py sys.path ---")
print(sys.path)
print("---------------------------")

import json
import os
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
import sys
import google.generativeai as genai_main
from google.genai.types import GenerateContentConfig, Tool, GoogleSearch
import re
import backoff
from pathlib import Path
from dotenv import load_dotenv
import concurrent.futures
from tqdm import tqdm
import argparse
import shutil
from collections import defaultdict

# Define the analysis structure
ANALYSIS_STRUCTURE = {
    "analysis": {
        "company_overview": {
            "company_name": "",
            "industry": "",
            "country": "",
            "founding_date": "",
            "mission_statement": "",
            "key_milestones": [],
            "current_status": "",
            "unique_value_proposition": ""
        },
        "product_analysis": {
            "product_description": "",
            "core_features": [],
            "technology_stack": [],
            "development_stage": "",
            "user_feedback": "",
            "product_roadmap": []
        },
        "market_analysis": {
            "target_market": "",
            "market_size": "",
            "growth_potential": "",
            "market_trends": [],
            "customer_segments": [],
            "market_challenges": []
        },
        "business_model": {
            "revenue_streams": [],
            "pricing_strategy": "",
            "customer_acquisition": "",
            "partnerships": [],
            "scaling_strategy": ""
        },
        "financial_overview": {
            "funding_history": [],
            "revenue": "",
            "profitability": "",
            "burn_rate": "",
            "runway": "",
            "financial_metrics": {}
        },
        "team_analysis": {
            "founders": [],
            "key_team_members": [],
            "advisors": [],
            "hiring_plans": [],
            "organizational_structure": ""
        },
        "competitive_advantage": {
            "unique_selling_points": [],
            "barriers_to_entry": [],
            "intellectual_property": [],
            "competitive_landscape": []
        },
        "risk_assessment": {
            "market_risks": [],
            "operational_risks": [],
            "financial_risks": [],
            "mitigation_strategies": []
        },
        "growth_strategy": {
            "short_term_goals": [],
            "long_term_vision": "",
            "expansion_plans": [],
            "scaling_approach": ""
        },
        "recommendations": {
            "strategic_recommendations": [{
                "recommendation": "",
                "rationale": "",
                "actionable_steps": [],
                "priority": "High | Medium | Low",
                "impact": "High | Medium | Low",
                "effort": "High | Medium | Low"
            }],
            "operational_recommendations": [{
                "recommendation": "",
                "rationale": "",
                "actionable_steps": [],
                "priority": "High | Medium | Low",
                "impact": "High | Medium | Low",
                "effort": "High | Medium | Low"
            }],
            "growth_recommendations": [{
                "recommendation": "",
                "rationale": "",
                "actionable_steps": [],
                "priority": "High | Medium | Low",
                "impact": "High | Medium | Low",
                "effort": "High | Medium | Low"
            }],
            "risk_mitigation_recommendations": [{
                "recommendation": "",
                "rationale": "",
                "actionable_steps": [],
                "priority": "High | Medium | Low",
                "impact": "High | Medium | Low",
                "effort": "High | Medium | Low"
            }]
        }
    }
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('startup_research.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Configuration
# Set to True to use grounding with Vertex AI Search or Google Search
# Set to False to use the model without grounding (potentially less accurate but simpler)
USE_GROUNDING = True

# --- Configure GenAI Library --- START ---
# Import genai and configure API key at the module level
# from google import genai # <-- Keep this commented or remove # REMOVE
# from google.generativeai import configure # <-- Import configure directly # REMOVE

import sys
# print(f"DEBUG: sys.path = {sys.path}") # <-- Keep or remove debug print
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")
genai_main.configure(api_key=api_key) # Use the alias for the main module
# configure(api_key=api_key) # REMOVE
logger.info("Google Generative AI library configured.")
# --- Configure GenAI Library --- END ---

# --- Class Definition ---
# Need to make sure the model uses the correct genai reference now
# from google import generativeai as genai # <-- Import with alias for the class # REMOVE

# Define the number of versions to keep
ARCHIVE_VERSIONS_TO_KEEP = 5

# --- Define Lock File Path --- START
# Place the lock file in the data directory
LOCK_FILE_PATH = Path('data') / '.research.lock'
# --- Define Lock File Path --- END

# --- Define Status File Function --- START
def get_status_file_path(startup_dir_name):
    return Path('data') / f'.research_status_{startup_dir_name}.json'

def update_status_file(startup_dir_name, status_data):
    status_file = get_status_file_path(startup_dir_name)
    try:
        with open(status_file, 'w') as f:
            json.dump(status_data, f)
    except Exception as e:
        # Log error but don't necessarily stop the main process
        logging.error(f"Could not update status file {status_file}: {e}")

def remove_status_file(startup_dir_name):
    status_file = get_status_file_path(startup_dir_name)
    try:
        if status_file.exists():
            status_file.unlink()
            logging.info(f"Removed status file: {status_file}")
    except Exception as e:
        logging.error(f"Could not remove status file {status_file}: {e}")
# --- Define Status File Function --- END

class StartupResearch:
    def __init__(self):
        # Set up logging (ensure it's initialized if not done globally)
        # logging.basicConfig(...) # Might be redundant if configured globally
        self.logger = logging.getLogger(__name__) # Use the global logger
        self.logger.info("Initializing StartupResearch")

        # Define model ID
        self.model_id = 'gemini-2.0-flash'

        # Define safety settings
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ]

        # Define DEFAULT generation config PARAMS (as dict)
        self.default_generation_params = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2048,
        }

        # Get the model instance, passing base config dictionary
        self.model = genai_main.GenerativeModel(
            model_name=self.model_id,
            safety_settings=self.safety_settings
            # Removed: generation_config=self.default_generation_params
        )
        self.logger.info(f"Initialized model: {self.model_id}")
        
        # Configure the grounding tool instance once
        self.google_search_tool = None
        if USE_GROUNDING:
            try:
                self.google_search_tool = Tool(google_search=GoogleSearch())
                self.logger.info("Initialized Google Search grounding tool.")
            except Exception as tool_error:
                 self.logger.error(f"Failed to initialize Google Search tool: {tool_error}")
                 self.google_search_tool = None # Ensure it's None if initialization fails

        # Set up directories
        self.data_dir = Path('data')
        self.archive_dir = self.data_dir / 'archive'
        self.results_dir = self.data_dir / 'results'
        
        for directory in [self.data_dir, self.archive_dir, self.results_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Ensured directory exists: {directory}")

    def archive_existing_startup_data(self, startup_name):
        """Moves existing files from a startup's data directory to the archive."""
        startup_dir_name = startup_name.lower().replace(' ', '_')
        startup_path = self.data_dir / startup_dir_name
        archive_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if startup_path.exists() and startup_path.is_dir():
            self.logger.info(f"Archiving existing files for startup: {startup_name} from {startup_path}")
            files_to_archive = list(startup_path.iterdir()) # Get files before moving
            if not files_to_archive:
                self.logger.info(f"No files found in {startup_path} to archive.")
                return

            for file_path in files_to_archive:
                if file_path.is_file():
                    # Create a unique name for the archived file
                    archive_file_name = f"{startup_dir_name}_{file_path.stem}_{archive_timestamp}{file_path.suffix}"
                    destination_path = self.archive_dir / archive_file_name
                    try:
                        shutil.move(str(file_path), str(destination_path))
                        self.logger.info(f"Archived {file_path.name} to {destination_path}")
                    except Exception as e:
                        self.logger.error(f"Error archiving {file_path.name}: {e}")
            # Optionally remove the startup directory if it's now empty
            # try:
            #     if not any(startup_path.iterdir()): # Check if empty
            #         startup_path.rmdir()
            #         self.logger.info(f"Removed empty directory: {startup_path}")
            # except Exception as e:
            #     self.logger.error(f"Could not remove directory {startup_path}: {e}")
        else:
            self.logger.info(f"No existing data directory found for startup: {startup_name} at {startup_path}")

    def cleanup_archive_by_version(self):
        """Cleans the archive directory, keeping only the last N versions of each file type."""
        self.logger.info(f"Starting archive cleanup. Keeping last {ARCHIVE_VERSIONS_TO_KEEP} versions of each file type.")
        files_by_base = defaultdict(list)

        # Regex to capture the base name and the timestamp
        # Example: analysis_noxon_company_overview_20240726_123456.json
        # Base name: analysis_noxon_company_overview
        # Timestamp: 20240726_123456
        # Note: This regex might need adjustment if filenames have multiple timestamps or different structures
        # Pattern to capture the base filename and the *last* timestamp before the extension
        pattern = re.compile(r"^(.*?)_(\d{8}_\d{6})(\.[^.]+)$")

        if not self.archive_dir.exists():
            self.logger.warning(f"Archive directory {self.archive_dir} does not exist. Skipping cleanup.")
            return

        for file_path in self.archive_dir.iterdir():
            if file_path.is_file():
                match = pattern.match(file_path.name)
                if match:
                    base_name = match.group(1)
                    timestamp_str = match.group(2)
                    # Store the path and timestamp for sorting
                    files_by_base[base_name].append((timestamp_str, file_path))
                else:
                    self.logger.debug(f"Could not parse base name/timestamp from archive file: {file_path.name}")

        files_deleted = 0
        for base_name, file_list in files_by_base.items():
            # Sort files by timestamp (descending - newest first)
            file_list.sort(key=lambda x: x[0], reverse=True)

            # Identify files to delete (beyond the Nth newest)
            files_to_delete = file_list[ARCHIVE_VERSIONS_TO_KEEP:]

            for _timestamp, file_path in files_to_delete:
                try:
                    file_path.unlink() # Delete the file
                    self.logger.info(f"Deleted old archive file: {file_path.name}")
                    files_deleted += 1
                except Exception as e:
                    self.logger.error(f"Error deleting archive file {file_path.name}: {e}")

        self.logger.info(f"Archive cleanup complete. Deleted {files_deleted} old files.")

    def _extract_and_parse_json(self, response_text, area_name="aggregation"):
        """Extracts JSON from text, cleaning Markdown fences and common issues."""
        cleaned_text = ""
        json_str = ""
        try:
            # 1. Remove Markdown fences and trim whitespace
            cleaned_text = re.sub(r"^```json\\s*|\\s*```$", "", response_text.strip())

            # 2. Find the first '{' and last '}'
            start_idx = cleaned_text.find('{')
            end_idx = cleaned_text.rfind('}') + 1

            if start_idx != -1 and end_idx != -1:
                json_str = cleaned_text[start_idx:end_idx]

                # 3. Attempt to parse the JSON
                parsed_json = json.loads(json_str)
                return parsed_json
            else:
                logging.error(f"Could not find valid JSON structure in response for {area_name}")
                logging.debug(f"Cleaned text for {area_name}: {cleaned_text}")
                return None
        except json.JSONDecodeError as e:
            # Enhanced logging
            logging.error(f"JSON parsing error for {area_name}: {e.msg} at line {e.lineno} col {e.colno}")
            # Log the vicinity of the error in the potentially problematic string
            problematic_text = json_str if json_str else cleaned_text # Use json_str if available, else cleaned_text
            # Calculate start/end for vicinity log, ensuring bounds are valid
            vicinity_start = max(0, e.pos - 50)
            vicinity_end = min(len(problematic_text), e.pos + 50)
            logging.error(f"Problematic JSON text segment for {area_name} (approx vicinity of error): {problematic_text[vicinity_start:vicinity_end]}")
            # Log the full string that was attempted to be parsed
            logging.debug(f"Full cleaned JSON string attempted for {area_name}: {json_str if json_str else 'N/A'}")
            # Log the original raw response for deeper debugging if needed
            logging.debug(f"Original response text for {area_name}: {response_text}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error during JSON extraction for {area_name}: {str(e)}")
            logging.exception(f"Traceback for unexpected JSON extraction error for {area_name}:") # Log traceback
            return None

    def assemble_final_json(self, startup_data, analysis_files: List[str]):
        """Assemble the final JSON from individual analysis files found at the given paths."""
        self.logger.info(f"Assembling final JSON for {startup_data['startup_name']} from {len(analysis_files)} files.")
        
        # Start with the base structure including metadata placeholders
        final_json_output = {
            "metadata": {
                "startup_name": startup_data['startup_name'],
                "industry": startup_data.get('industry', ''),
                "country": startup_data.get('country', ''),
                "assembly_timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "model_used_for_areas": self.model_id, # Assuming same model for all areas
                "analysis_version": "2.0",
                "sources": [], # Could potentially aggregate sources later
                "missing_areas": sorted(list(ANALYSIS_STRUCTURE['analysis'].keys())), # Start assuming all are missing
                "assembly_status": "in_progress"
            },
            "analysis": {} # Initialize empty analysis dict
        }

        present_areas = set()
        aggregated_sources = set() # Use a set to avoid duplicate sources

        # Initialize analysis section with empty structures from ANALYSIS_STRUCTURE
        for area_key, structure in ANALYSIS_STRUCTURE['analysis'].items():
            final_json_output['analysis'][area_key] = structure

        for file_path_str in analysis_files:
            file_path = Path(file_path_str) # Convert string path to Path object
            try:
                if not file_path.exists():
                    self.logger.warning(f"Analysis file not found during assembly: {file_path}, skipping.")
                    continue

                with open(file_path, 'r') as f:
                    area_analysis = json.load(f)

                # Basic validation of the loaded JSON structure
                if not isinstance(area_analysis, dict) or "metadata" not in area_analysis or "analysis" not in area_analysis:
                    self.logger.warning(f"Invalid structure in analysis file {file_path}, skipping.")
                    continue

                analysis_area = area_analysis["metadata"].get("analysis_area")
                if not analysis_area or analysis_area not in ANALYSIS_STRUCTURE['analysis']:
                    self.logger.warning(f"Could not determine valid analysis area from metadata in {file_path}, skipping.")
                    continue
                
                # Add the area as present
                present_areas.add(analysis_area)
                
                # Merge the specific area's analysis data
                # Ensure the area key exists in the loaded analysis section
                if analysis_area in area_analysis["analysis"]:
                    # Overwrite the placeholder with the actual analysis data for this area
                    final_json_output['analysis'][analysis_area] = area_analysis["analysis"][analysis_area]
                    self.logger.debug(f"Merged analysis data for area '{analysis_area}' from {file_path}")
                else:
                     self.logger.warning(f"Analysis area '{analysis_area}' key not found within the 'analysis' section of {file_path}")


                # Aggregate sources (optional)
                sources = area_analysis["metadata"].get("sources", [])
                if isinstance(sources, list):
                    aggregated_sources.update(sources)

            except json.JSONDecodeError as e:
                self.logger.error(f"JSON decoding error processing {file_path}: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error processing {file_path}: {e}")

        # Update metadata based on processed files
        all_expected_areas = set(ANALYSIS_STRUCTURE['analysis'].keys())
        missing_areas = sorted(list(all_expected_areas - present_areas))
        final_json_output['metadata']['missing_areas'] = missing_areas
        final_json_output['metadata']['sources'] = sorted(list(aggregated_sources))
        
        if not missing_areas:
            final_json_output['metadata']['assembly_status'] = "completed_all_areas"
            self.logger.info(f"Successfully assembled final JSON for {startup_data['startup_name']} - All areas present.")
        else:
            final_json_output['metadata']['assembly_status'] = "completed_missing_areas"
            self.logger.warning(f"Assembled final JSON for {startup_data['startup_name']} - Missing areas: {missing_areas}")

        return final_json_output

    def analyze_startup(self, startup_data):
        """Analyze a single startup using Gemini API for areas, then assemble."""
        startup_dir_name = "" # Initialize for use in final saving and status updates
        completed_areas = [] # Track completed areas for status
        try:
            # Ensure startup_dir uses Path object and correct naming
            startup_dir_name = startup_data['startup_name'].lower().replace(' ', '_')
            startup_dir = self.data_dir / startup_dir_name # Use Path object
            startup_dir.mkdir(parents=True, exist_ok=True) # Changed from os.makedirs

            # Define analysis areas
            analysis_areas = [
                'company_overview',
                'product_analysis',
                'market_analysis',
                'business_model',
                'financial_overview',
                'team_analysis',
                'competitive_advantage',
                'risk_assessment',
                'growth_strategy',
                'recommendations'
            ]
            
            # Initialize the area analyses dictionary and list for file paths
            area_analyses_data = {} # Stores parsed JSON data (optional, if needed elsewhere)
            area_analysis_files = [] # Stores paths to the generated JSON files
            
            # --- Prepare GenerationConfig with tools --- START
            analysis_gen_config = None # Use None if no tools needed or tool init failed
            if USE_GROUNDING and self.google_search_tool:
                try:
                    # Create GenerateContentConfig with the tool AND default params
                    analysis_gen_config = GenerateContentConfig(
                        tools=[self.google_search_tool],
                        **self.default_generation_params # Unpack default params here
                    )
                    self.logger.info("Using Google Search grounding for startup area analysis.")
                except Exception as config_error:
                     self.logger.error(f"Failed to create GenerateContentConfig for area analysis: {config_error}")
                     analysis_gen_config = self.default_generation_params # Fallback to default dict
                else:
                    analysis_gen_config = self.default_generation_params # Use default dict if no grounding
            # --- Prepare GenerationConfig with tools --- END

            # --- Initial Status Update --- START
            update_status_file(startup_dir_name, {
                "status": "starting_analysis", 
                "startup_name": startup_data['startup_name'],
                "completed_areas": completed_areas,
                "total_areas": len(analysis_areas)
            })
            # --- Initial Status Update --- END

            # Analyze each area separately
            for area in analysis_areas:
                # --- Update Status: Starting Area --- START
                update_status_file(startup_dir_name, {
                    "status": f"analyzing_{area}",
                    "startup_name": startup_data['startup_name'],
                    "current_area": area,
                    "completed_areas": completed_areas,
                    "total_areas": len(analysis_areas)
                })
                # --- Update Status: Starting Area --- END
                try:
                    # Determine the expected structure for the prompt example
                    example_area_structure = ANALYSIS_STRUCTURE['analysis'].get(area, {})
                    
                    # Special handling for recommendations to show the detailed item structure
                    if area == 'recommendations':
                        # Show the structure of the first item in one of the recommendation lists as example
                        example_area_structure = {
                            "strategic_recommendations": [{
                                "recommendation": "", "rationale": "", "actionable_steps": [],
                                "priority": "High | Medium | Low", "impact": "High | Medium | Low", "effort": "High | Medium | Low"
                            }],
                            "operational_recommendations": [{
                                "recommendation": "", "rationale": "", "actionable_steps": [],
                                "priority": "High | Medium | Low", "impact": "High | Medium | Low", "effort": "High | Medium | Low"
                            }],
                            "growth_recommendations": [{
                                "recommendation": "", "rationale": "", "actionable_steps": [],
                                "priority": "High | Medium | Low", "impact": "High | Medium | Low", "effort": "High | Medium | Low"
                            }],
                            "risk_mitigation_recommendations": [{
                                "recommendation": "", "rationale": "", "actionable_steps": [],
                                "priority": "High | Medium | Low", "impact": "High | Medium | Low", "effort": "High | Medium | Low"
                            }]
                         }
                    
                    # Create area-specific prompt
                    area_prompt = f"""
                    Analyze the following startup focusing specifically on the **{area}** area. Use web search extensively to gather comprehensive information.

                    Startup Information:
                    Name: {startup_data['startup_name']}
                    Industry: {startup_data.get('industry', '')}
                    Country: {startup_data.get('country', '')}

                    Additional Information:
                    Founders: {', '.join(startup_data.get('founders', []))}
                    Founded: {startup_data.get('date_founded', '')}
                    Stage: {startup_data.get('stage', '')}
                    Website: {startup_data.get('website', '')}
                    Fundraising: {startup_data.get('fundraising', '')}
                    Product Stage: {startup_data.get('product_stage', '')}
                    Employees: {startup_data.get('no_of_employees', '')}

                    Overview:
                    {startup_data.get('overview', '')}

                    Program Expectations:
                    {startup_data.get('expectations_for_the_program', '')}

                    IMPORTANT INSTRUCTIONS:
                    1.  Your response **MUST** be only a single, valid JSON object. Do **NOT** include *any* text before the opening `{{` or after the final `}}`.
                    2.  Provide extremely detailed information specifically for the `{area}` section based on web search results.
                    3.  **Output Formatting:** Within the JSON string values, provide plain text suitable for direct rendering in HTML. **AVOID** using markdown formatting like bullet points (`*`, `-`), numbered lists, bolding (`** **`), or italics within the JSON string values. For lists of items (like core_features, actionable_steps, etc.), use JSON arrays of simple strings `["Item 1", "Item 2", "Item 3"]`.
                    4.  Use web search to verify and enrich all information. Only include specific details (like URLs, funding amounts, dates, etc.) if they are found and verified through web search. If a specific piece of information cannot be found or verified via search, explicitly state 'Not Found' or use an empty string/array/null in the JSON.
                    5.  **Team Analysis Specifics:** If analyzing the `team_analysis` area, search extensively for founder/team member details, including LinkedIn URLs, and include the full URL if found.
                    6.  **Recommendations Specifics:** If analyzing the `recommendations` area, **you MUST generate at least one actionable recommendation object** within each list (strategic_recommendations, operational_recommendations, etc.), even if based on limited data or extrapolation. Each recommendation object **MUST** include *all* the following keys, populated appropriately: `recommendation` (string), `rationale` (string), `actionable_steps` (array of strings), `priority` (string: "High", "Medium", or "Low"), `impact` (string: "High", "Medium", or "Low"), and `effort` (string: "High", "Medium", or "Low"). Do not leave values empty unless absolutely no information can be inferred; use "N/A" if necessary for string fields or an empty array `[]` for `actionable_steps`.

                    Please provide the comprehensive analysis for the `{area}` area in the specified JSON format below:
                    ```json
                    {{
                        "metadata": {{
                            "startup_name": "{startup_data['startup_name']}",
                            "analysis_area": "{area}",
                            "analysis_timestamp": "{datetime.now().strftime("%Y%m%d_%H%M%S")}",
                            "model_used": "{self.model_id}",
                            "analysis_version": "2.0",
                            "sources": []  // Populate this list with URLs used if possible
                        }},
                        "analysis": {{
                            "{area}": {json.dumps(example_area_structure, indent=4)}
                        }}
                    }}
                    ```

                    Remember to use web search extensively and output **ONLY** the single JSON object.
                    """
                    
                    # Generate content for this area using the model instance
                    response = self.model.generate_content(
                        contents=[area_prompt],
                        # Pass the config object (or dict) to override model's default config
                        generation_config=analysis_gen_config
                    )
                    
                    # Process the response
                    response_text = response.text

                    # Try to extract JSON from the response
                    try:
                        # 1. Remove Markdown fences and trim whitespace
                        cleaned_text = re.sub(r"^```json\s*|\s*```$", "", response_text.strip())

                        # 2. Find the first '{' and last '}'
                        start_idx = cleaned_text.find('{')
                        end_idx = cleaned_text.rfind('}') + 1

                        if start_idx != -1 and end_idx != -1:
                            json_str = cleaned_text[start_idx:end_idx]
                            # 3. Attempt to parse the JSON
                            area_analysis = json.loads(json_str)

                            # Store the area analysis data (optional)
                            area_analyses_data[area] = area_analysis
                            logging.info(f"Successfully processed {area} for {startup_data['startup_name']}")

                            # Save the parsed JSON to a file and store the path
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            json_file_path = startup_dir / f"{area}_analysis_{timestamp}.json" # Use Path object
                            try:
                                with open(json_file_path, 'w') as f:
                                    json.dump(area_analysis, f, indent=4)
                                logging.info(f"Saved parsed JSON for {area} to {json_file_path}")
                                area_analysis_files.append(str(json_file_path)) # Add the file path string to the list

                                # --- Update Status: Completed Area --- START
                                completed_areas.append(area)
                                update_status_file(startup_dir_name, {
                                    "status": f"completed_{area}",
                                    "startup_name": startup_data['startup_name'],
                                    "current_area": area, # Keep track of last completed
                                    "completed_areas": completed_areas,
                                    "total_areas": len(analysis_areas)
                                })
                                # --- Update Status: Completed Area --- END

                            except Exception as save_error:
                                logging.error(f"Failed to save JSON for {area} to {json_file_path}: {save_error}")

                        else:
                            logging.error(f"Could not find valid JSON structure in response for {area}")
                            logging.debug(f"Cleaned text for {area}: {cleaned_text}")
                    except json.JSONDecodeError as e:
                        logging.error(f"JSON parsing error for {area}: {str(e)}")
                        # Log the problematic segment if possible
                        problematic_segment = cleaned_text[start_idx:end_idx] if 'start_idx' in locals() and 'end_idx' in locals() and start_idx !=-1 and end_idx != -1 else "N/A"
                        logging.error(f"Problematic JSON string segment for {area}: {problematic_segment}")
                        logging.debug(f"Original response text for {area}: {response_text}")
                except Exception as e:
                    logging.error(f"Error analyzing {area} for {startup_data['startup_name']}: {str(e)}")
                    # Optionally update status to reflect area error?
                    continue # Continue to the next area if one fails
            
            # --- Update Status: Starting Assembly --- START
            update_status_file(startup_dir_name, {
                "status": "assembling_final_json",
                "startup_name": startup_data['startup_name'],
                "completed_areas": completed_areas,
                "total_areas": len(analysis_areas)
            })
            # --- Update Status: Starting Assembly --- END

            # Assemble the final JSON using the list of generated file paths
            final_result = self.assemble_final_json(startup_data, area_analysis_files) # Pass startup_data and the list of file paths

            if final_result and isinstance(final_result, dict): # Check if we got a dictionary back
                # --- Archive existing and save new result --- START
                if not startup_dir_name:
                     startup_dir_name = startup_data.get('startup_name', 'unknown').lower().replace(' ', '_')

                # Define the primary (non-timestamped) filename
                primary_file_name = f"analysis_{startup_dir_name}.json"
                primary_file_path = self.results_dir / primary_file_name

                # Check for existing file and archive it
                if primary_file_path.exists():
                    try:
                        archive_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        archive_file_name = f"analysis_{startup_dir_name}_{archive_timestamp}.json"
                        archive_destination = self.archive_dir / archive_file_name
                        shutil.move(str(primary_file_path), str(archive_destination))
                        self.logger.info(f"Archived existing result file {primary_file_name} to {archive_destination}")
                    except Exception as archive_err:
                        self.logger.error(f"Failed to archive existing result file {primary_file_name}: {archive_err}")
                        # Decide if you want to continue and overwrite, or fail here. Overwriting for now.

                # Save the new result to the primary filename
                try:
                    with open(primary_file_path, 'w') as f:
                        json.dump(final_result, f, indent=4)

                    # Log success/failure based on assembly status
                    assembly_status = final_result.get("metadata", {}).get("assembly_status")
                    if assembly_status == "failed_critical_assembly":
                         logging.error(f"Completed run for {startup_data['startup_name']} but with CRITICAL ASSEMBLY FAILURE, saved error data to {primary_file_path}")
                    else:
                        missing_areas_reported = final_result.get("metadata", {}).get("missing_areas", [])
                        if missing_areas_reported:
                            logging.info(f"Successfully completed analysis for {startup_data['startup_name']} (missing areas: {missing_areas_reported}), saved to {primary_file_path}")
                        else:
                             logging.info(f"Successfully completed analysis for {startup_data['startup_name']} (all areas present), saved to {primary_file_path}")

                    return True # Indicate success as a file was generated
                except Exception as save_error:
                    logging.error(f"Failed to save final assembled result for {startup_data['startup_name']} to {primary_file_path}: {save_error}")
                    return False # Indicate failure if saving failed
                # --- Archive existing and save new result --- END
            else:
                # This case means assemble_final_json failed badly and didn't return a dict
                logging.error(f"Failed to generate final assembled analysis for {startup_data['startup_name']} - assemble_final_json returned unexpected type or None: {type(final_result)}")
                return False # Indicate failure

        except Exception as e:
            logging.error(f"Critical error analyzing startup {startup_data['startup_name']}: {str(e)}")
            # raise # Re-raising might stop the whole batch process
            return False # Indicate failure
        finally:
            # Ensure the lock file is removed regardless of success or failure
            self.remove_lock_file()
            # --- Ensure status file is removed --- START
            if startup_dir_name: # Only remove status if running for a single startup
                 remove_status_file(startup_dir_name)
            else:
                 # If running for all, we might need a different status mechanism
                 # or remove all status files? For now, do nothing for batch runs.
                 self.logger.info("Batch run finished. Status file removal skipped (only active for single runs).")
            # --- Ensure status file is removed --- END
            self.logger.info("Research batch processing finished (or encountered error).")
        self.logger.info("Research process completed")

    def process_batch(self, startups_to_process, batch_size=2, max_workers=10): # Renamed arg
        self.logger.info(f"Processing batch of {len(startups_to_process)} startups with {max_workers} parallel workers")
        successful_analyses = 0
        failed_analyses = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Create a progress bar
            with tqdm(total=len(startups_to_process), desc="Analyzing startups") as pbar:
                # Submit all tasks
                future_to_startup = {
                    executor.submit(self.analyze_startup, startup): startup
                    for startup in startups_to_process
                }
                
                # Process completed tasks as they finish
                for future in concurrent.futures.as_completed(future_to_startup):
                    startup = future_to_startup[future]
                    try:
                        success = future.result() # analyze_startup now returns True/False
                        if success:
                            successful_analyses += 1
                        else:
                            failed_analyses += 1
                            # Error logged within analyze_startup or assemble_final_json
                    except Exception as e:
                        # This catches errors *outside* the analyze_startup try/except
                        self.logger.error(f"Unhandled error processing {startup['startup_name']}: {e}")
                        failed_analyses += 1
                    finally:
                        pbar.update(1)

        self.logger.info(f"Batch processing complete. Successful: {successful_analyses}, Failed: {failed_analyses}")
        # No longer returns results list, results are saved individually per startup

    def create_lock_file(self):
        """Attempts to create the lock file exclusively. Returns True if successful, False otherwise."""
        try:
            # x mode: open for exclusive creation, failing if the file already exists
            with open(LOCK_FILE_PATH, 'x') as f:
                f.write(f"Locked by PID: {os.getpid()} at {datetime.now()}\n")
            self.logger.info(f"Successfully created lock file: {LOCK_FILE_PATH}")
            return True
        except FileExistsError:
            self.logger.warning(f"Lock file {LOCK_FILE_PATH} already exists. Another process may be running.")
            return False
        except Exception as e:
            self.logger.error(f"Error creating lock file {LOCK_FILE_PATH}: {e}")
            return False # Treat other errors as failure to acquire lock

    def remove_lock_file(self):
        """Removes the lock file if it exists."""
        try:
            if LOCK_FILE_PATH.exists():
                LOCK_FILE_PATH.unlink()
                self.logger.info(f"Removed lock file: {LOCK_FILE_PATH}")
            else:
                self.logger.debug("Lock file did not exist, no need to remove.")
        except Exception as e:
            self.logger.error(f"Error removing lock file {LOCK_FILE_PATH}: {e}")

    def run_research(self, target_startup_name=None, batch_size=10, max_workers=10): # Added target_startup_name
        self.logger.info(f"Starting research process. Target: {target_startup_name or 'All Startups'}")
        
        # --- Attempt to acquire lock --- START
        if not self.create_lock_file():
            self.logger.error("Could not acquire lock. Exiting research process.")
            sys.exit(1) # Exit script if lock cannot be acquired
        # --- Attempt to acquire lock --- END
            
        all_startups = load_startups()
        if not all_startups:
            self.logger.error("No startups loaded, exiting.")
            self.remove_lock_file() # Ensure lock is removed on early exit
            return

        # Filter startups if a target name is provided
        startups_to_process = []
        if target_startup_name:
            found = False
            for startup in all_startups:
                if startup['startup_name'].lower() == target_startup_name.lower():
                    startups_to_process.append(startup)
                    found = True
                    break # Found the target startup
            if not found:
                self.logger.error(f"Startup '{target_startup_name}' not found in startups.json. Exiting.")
                self.remove_lock_file() # Ensure lock is removed on early exit
                return
            self.logger.info(f"Processing single startup: {target_startup_name}")
        else:
            startups_to_process = all_startups
            self.logger.info(f"Processing all {len(startups_to_process)} loaded startups.")

        if not startups_to_process:
            self.logger.warning("No startups selected for processing after filtering.")
            self.remove_lock_file() # Ensure lock is removed on early exit
            return

        # --- START: Cleanup and Pre-run Archiving ---
        # Cleanup archive *before* archiving current data
        self.cleanup_archive_by_version()

        self.logger.info("Starting pre-run archiving of existing startup data...")
        for startup in startups_to_process:
            self.archive_existing_startup_data(startup['startup_name'])
        self.logger.info("Pre-run archiving complete.")
        # --- END: Added Try/Finally for future lock file ---

        # --- START: Added Try/Finally for lock and status file ---
        try:
            self.process_batch(startups_to_process, batch_size, max_workers)
        finally:
            # Ensure the lock file is removed regardless of success or failure
            self.remove_lock_file()
            # --- Ensure status file is removed --- START
            if target_startup_name: # Only remove status if running for a single startup
                 startup_dir_name_for_status = target_startup_name.lower().replace(' ', '_')
                 remove_status_file(startup_dir_name_for_status)
            else:
                 # If running for all, we might need a different status mechanism
                 # or remove all status files? For now, do nothing for batch runs.
                 self.logger.info("Batch run finished. Status file removal skipped (only active for single runs).")
            # --- Ensure status file is removed --- END
            self.logger.info("Research batch processing finished (or encountered error).")
        # --- END: Added Try/Finally ---
        self.logger.info("Research process completed")

def load_startups():
    try:
        with open('startups.json', 'r') as f:
            startups_data = json.load(f)
            
        # Transform the data to match the expected format
        startups = []
        for startup in startups_data:
            # Basic check for required key
            if 'startup_name' not in startup or not startup['startup_name']:
                logging.warning(f"Skipping entry due to missing or empty 'startup_name': {startup}")
                continue

            transformed_startup = {
                'startup_name': startup['startup_name'],
                # Use .get() for optional fields
                'industry': startup.get('business_model', ''), # Assuming business_model maps to industry
                'country': startup.get('country', 'N/A'),
                'founders': startup.get('founders', []),
                'date_founded': startup.get('date_founded', ''),
                'stage': startup.get('stage', ''),
                'website': startup.get('website', ''),
                'fundraising': startup.get('fundraising', ''),
                'product_stage': startup.get('product_stage', ''),
                'no_of_employees': startup.get('no_of_employees', ''),
                'overview': startup.get('overview', ''),
                'expectations_for_the_program': startup.get('expectations_for_the_program', '')
            }
            startups.append(transformed_startup)
            
        logging.info(f"Loaded {len(startups)} startups from JSON")
        return startups
    except FileNotFoundError:
        logging.error("Error: startups.json not found.")
        return None
    except json.JSONDecodeError as e:
         logging.error(f"Error decoding startups.json: {e}")
         return None
    except Exception as e:
        logging.error(f"Unexpected error loading startups from JSON: {e}")
        return None

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Run startup research analysis.")
    parser.add_argument(
        "--startup",
        type=str,
        help="Optional: Specify the name of a single startup to analyze."
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Optional: Number of parallel workers (default: 10)."
    )
    parser.add_argument(
        "--batchsize",
        type=int,
        default=2, # Reduced default batch size
        help="Optional: Batch size for processing (default: 2)."
    )

    # Parse arguments
    args = parser.parse_args()

    # Run the researcher
    researcher = StartupResearch()
    researcher.run_research(
        target_startup_name=args.startup,
        max_workers=args.workers,
        batch_size=args.batchsize # Pass batch size
    ) 