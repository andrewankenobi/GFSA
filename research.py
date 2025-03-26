import json
import os
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
import google.generativeai as genai
from google.generativeai import types
import backoff
from pathlib import Path
from dotenv import load_dotenv

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

class StartupResearch:
    def __init__(self):
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('startup_research.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing StartupResearch")

        # Load environment variables
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        # Configure the API
        genai.configure(api_key=api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Set up directories
        self.data_dir = Path('data')
        self.archive_dir = self.data_dir / 'archive'
        self.results_dir = self.data_dir / 'results'
        
        for directory in [self.data_dir, self.archive_dir, self.results_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created directory: {directory}")

    def analyze_startup(self, startup):
        self.logger.info(f"Starting analysis for startup: {startup['Startup Name']}")
        
        # Save raw response before processing
        raw_dir = self.data_dir / 'raw'
        raw_dir.mkdir(exist_ok=True)
        
        # Create the prompt with search context
        prompt = f"""
        Analyze the following startup and provide an extremely detailed report. Use web search extensively to gather comprehensive information.
        
        Startup Information:
        Name: {startup['Startup Name']}
        Industry: {startup['Industry']}
        Country: {startup['Country']}
        
        IMPORTANT INSTRUCTIONS:
        1. Your response must be a valid JSON object
        2. Provide extremely detailed information in each section
        3. For founders and team members, include:
           - Educational background
           - Previous work experience
           - Notable achievements
           - Areas of expertise
           - Social media presence (LinkedIn, Twitter)
        4. For market analysis:
           - Include specific market size figures with sources
           - Detailed competitor analysis with strengths/weaknesses
           - Regulatory environment
           - Market dynamics and drivers
        5. For financial information:
           - Detailed breakdown of funding rounds
           - Valuation metrics and comparables
           - Burn rate and runway estimates
           - Revenue projections if available
        6. Use web search to verify and enrich all information
        
        Please provide a comprehensive analysis in JSON format with the following structure:
        {{
            "metadata": {{
                "startup_name": "{startup['Startup Name']}",
                "industry": "{startup['Industry']}",
                "country": "{startup['Country']}",
                "analysis_timestamp": "<current_timestamp>",
                "model_used": "gemini-2.0-flash",
                "analysis_version": "2.0",
                "sources": []
            }},
            "analysis": {{
                "company_overview": {{
                    "description": "",
                    "founding_date": "",
                    "founders": [
                        {{
                            "name": "",
                            "title": "",
                            "education": [],
                            "work_experience": [],
                            "achievements": [],
                            "expertise": [],
                            "social_profiles": {{}}
                        }}
                    ],
                    "headquarters": "",
                    "company_stage": "",
                    "employee_count": "",
                    "key_milestones": []
                }},
                "product_analysis": {{
                    "main_products": [
                        {{
                            "name": "",
                            "description": "",
                            "key_features": [],
                            "target_users": "",
                            "pricing": "",
                            "competitive_position": ""
                        }}
                    ],
                    "unique_features": [],
                    "target_market": {{
                        "primary_segments": [],
                        "market_size": "",
                        "user_demographics": "",
                        "geographical_focus": ""
                    }},
                    "technology_stack": {{
                        "frontend": [],
                        "backend": [],
                        "infrastructure": [],
                        "third_party_services": [],
                        "notable_technical_achievements": []
                    }}
                }},
                "market_analysis": {{
                    "market_size": {{
                        "total_addressable_market": "",
                        "serviceable_addressable_market": "",
                        "serviceable_obtainable_market": "",
                        "growth_rate": "",
                        "key_drivers": []
                    }},
                    "competitors": [
                        {{
                            "name": "",
                            "description": "",
                            "strengths": [],
                            "weaknesses": [],
                            "market_share": "",
                            "competitive_advantage": ""
                        }}
                    ],
                    "market_trends": [],
                    "regulatory_environment": {{
                        "current_regulations": [],
                        "upcoming_changes": [],
                        "compliance_requirements": []
                    }},
                    "growth_potential": ""
                }},
                "business_model": {{
                    "revenue_streams": [
                        {{
                            "type": "",
                            "description": "",
                            "contribution": "",
                            "growth_potential": ""
                        }}
                    ],
                    "pricing_strategy": {{
                        "model": "",
                        "price_points": [],
                        "comparison_with_competitors": ""
                    }},
                    "customer_acquisition": {{
                        "channels": [],
                        "cac": "",
                        "ltv": "",
                        "conversion_rates": "",
                        "retention_metrics": ""
                    }},
                    "partnerships": [
                        {{
                            "partner": "",
                            "type": "",
                            "benefits": [],
                            "status": ""
                        }}
                    ]
                }},
                "financial_overview": {{
                    "funding_rounds": [
                        {{
                            "round": "",
                            "date": "",
                            "amount": "",
                            "lead_investors": [],
                            "valuation": "",
                            "key_terms": ""
                        }}
                    ],
                    "total_funding": "",
                    "key_investors": [
                        {{
                            "name": "",
                            "type": "",
                            "portfolio_focus": "",
                            "investment_thesis": ""
                        }}
                    ],
                    "valuation": {{
                        "current_valuation": "",
                        "valuation_metrics": [],
                        "comparable_companies": [],
                        "key_drivers": []
                    }},
                    "financial_metrics": {{
                        "revenue": "",
                        "burn_rate": "",
                        "runway": "",
                        "unit_economics": "",
                        "path_to_profitability": ""
                    }}
                }},
                "team_analysis": {{
                    "leadership_team": [
                        {{
                            "name": "",
                            "title": "",
                            "background": {{
                                "education": [],
                                "work_experience": [],
                                "achievements": []
                            }},
                            "expertise": [],
                            "responsibilities": []
                        }}
                    ],
                    "team_size": "",
                    "key_hires": [
                        {{
                            "role": "",
                            "requirements": [],
                            "impact": ""
                        }}
                    ],
                    "expertise": [],
                    "culture_and_values": [],
                    "recruitment_strategy": ""
                }},
                "competitive_advantage": {{
                    "unique_selling_points": [],
                    "barriers_to_entry": [],
                    "patents_ip": {{
                        "patents": [],
                        "trademarks": [],
                        "trade_secrets": [],
                        "licensing_agreements": []
                    }},
                    "network_effects": "",
                    "brand_value": ""
                }},
                "risk_assessment": {{
                    "market_risks": [
                        {{
                            "risk": "",
                            "likelihood": "",
                            "impact": "",
                            "mitigation": ""
                        }}
                    ],
                    "operational_risks": [
                        {{
                            "risk": "",
                            "likelihood": "",
                            "impact": "",
                            "mitigation": ""
                        }}
                    ],
                    "financial_risks": [
                        {{
                            "risk": "",
                            "likelihood": "",
                            "impact": "",
                            "mitigation": ""
                        }}
                    ],
                    "mitigation_strategies": []
                }},
                "growth_strategy": {{
                    "expansion_plans": {{
                        "geographic": [],
                        "product": [],
                        "market": [],
                        "timeline": ""
                    }},
                    "product_roadmap": {{
                        "short_term": [],
                        "medium_term": [],
                        "long_term": [],
                        "key_initiatives": []
                    }},
                    "market_expansion": {{
                        "target_markets": [],
                        "entry_strategy": "",
                        "success_metrics": [],
                        "resource_requirements": ""
                    }}
                }},
                "recommendations": {{
                    "investment_potential": {{
                        "recommendation": "",
                        "rationale": [],
                        "risk_factors": [],
                        "expected_returns": ""
                    }},
                    "key_opportunities": [],
                    "areas_of_concern": [],
                    "strategic_suggestions": []
                }}
            }}
        }}

        IMPORTANT: Your response must be a valid JSON object. Do not include any text before or after the JSON.
        Use web search extensively to gather accurate and up-to-date information about the startup.
        """

        try:
            # Generate response with search enabled
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 1,
                    'top_k': 32,
                    'max_output_tokens': 8192,
                },
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                ]
            )

            # Save raw response
            raw_filename = raw_dir / f"{startup['Startup Name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_raw.json"
            with open(raw_filename, 'w') as f:
                f.write(response.text)
            self.logger.info(f"Saved raw response to {raw_filename}")

            # Extract and parse the JSON response
            try:
                # Clean the response text
                response_text = response.text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                # Parse JSON
                analysis_data = json.loads(response_text)
                self.logger.info(f"Successfully analyzed startup: {startup['Startup Name']}")
                return analysis_data
                
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse JSON response for {startup['Startup Name']}: {e}")
                # Create a structured response from text
                sections = response_text.split('\n\n')
                structured_response = {
                    "metadata": {
                        "startup_name": startup['Startup Name'],
                        "industry": startup['Industry'],
                        "country": startup['Country'],
                        "analysis_timestamp": datetime.now().isoformat(),
                        "model_used": "gemini-2.0-flash",
                        "analysis_version": "2.0",
                        "note": "Fallback structured format due to JSON parsing error"
                    },
                    "analysis": {
                        "raw_sections": sections
                    }
                }
                return structured_response
                
        except Exception as e:
            self.logger.error(f"Error analyzing startup {startup['Startup Name']}: {e}")
            return None

    def process_batch(self, startups, batch_size=10):
        self.logger.info(f"Processing batch of {len(startups)} startups")
        results = []
        for i in range(0, len(startups), batch_size):
            batch = startups[i:i + batch_size]
            self.logger.info(f"Processing batch starting at index {i}")
            for startup in batch:
                result = self.analyze_startup(startup)
                if result:
                    results.append(result)
        return results

    def save_results(self, results):
        if not results:
            self.logger.warning("No results to save")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.results_dir / f"analysis_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            self.logger.info(f"Results saved to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")

    def archive_old_files(self, max_files=10):
        self.logger.info("Archiving old result files")
        result_files = sorted(self.results_dir.glob('analysis_*.json'))
        if len(result_files) > max_files:
            for file in result_files[:-max_files]:
                try:
                    file.rename(self.archive_dir / file.name)
                    self.logger.info(f"Archived {file.name}")
                except Exception as e:
                    self.logger.error(f"Error archiving {file.name}: {e}")

    def run_research(self, batch_size=10):
        self.logger.info("Starting research process")
        startups = load_startups()
        if not startups:
            self.logger.error("No startups loaded")
            return
        
        results = self.process_batch(startups, batch_size)
        self.save_results(results)
        self.archive_old_files()
        self.logger.info("Research process completed")

def load_startups():
    try:
        startups = []
        with open('startups.txt', 'r') as f:
            lines = f.readlines()
            # Skip header
            for line in lines[1:]:
                parts = line.strip().split('\t')
                if len(parts) >= 3:
                    startup = {
                        'Startup Name': parts[0].strip(),
                        'Country': parts[1].strip(),
                        'Industry': parts[2].strip()
                    }
                    startups.append(startup)
        logging.info(f"Loaded {len(startups)} startups")
        return startups
    except Exception as e:
        logging.error(f"Error loading startups: {e}")
        return None

if __name__ == "__main__":
    researcher = StartupResearch()
    researcher.run_research() 