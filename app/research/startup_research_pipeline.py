import os
import json
import asyncio
import ssl
import re
import certifi
import aiohttp
import shutil
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin
import google.generativeai as genai
from dotenv import load_dotenv

class StartupResearchPipeline:
    def __init__(
        self, 
        raw_dir: str = "data/raw", 
        archive_dir: str = "data/archive",
        refined_dir: str = "data/refined",
        days_to_archive: int = 7
    ):
        # Load environment variables
        load_dotenv()
        
        # Initialize file paths
        self.raw_dir = Path(raw_dir)
        self.archive_dir = Path(archive_dir)
        self.refined_dir = Path(refined_dir)
        self.days_to_archive = days_to_archive
        
        # Create directories if they don't exist
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.refined_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        genai.configure(api_key=api_key)
        
        # Web scraper properties
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = None
        self.visited_urls = set()
        
    async def initialize(self):
        """Initialize aiohttp session"""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
        
    async def cleanup(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            
    async def __aenter__(self):
        return await self.initialize()
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
    
    #-------------------------------------------------------------------------
    # Main Pipeline Methods
    #-------------------------------------------------------------------------
    
    async def process_startup(self, startup_data: Dict[str, str]) -> Dict[str, Any]:
        """Process a single startup through the complete pipeline"""
        startup_name = startup_data.get("name", "Unknown")
        website = startup_data.get("website", "")
        
        print(f"\nProcessing startup: {startup_name}")
        
        try:
            # 1. Web scraping - this data can be large (sometimes several MB)
            website_data = await self._scrape_startup_website(website)
            
            # 2. AI analysis - uses the website data but produces a more concise result
            analysis = await self._analyze_startup(startup_data, website_data)
            
            # 3. Save results (excluding website_data to save space)
            # We don't save website_data to avoid creating huge JSON files
            result = {
                "startup": startup_data,
                "analysis": analysis,
                "processed_at": datetime.now().isoformat()
            }
            
            # 4. Only keep website_data in memory for potential further processing
            # But return the complete result to the caller
            full_result = {
                "startup": startup_data,
                "website_data": website_data,
                "analysis": analysis,
                "processed_at": datetime.now().isoformat()
            }
            
            await self._save_analysis(startup_name, result)
            print(f"Successfully processed {startup_name}")
            return full_result
            
        except Exception as e:
            print(f"Error processing {startup_name}: {str(e)}")
            return {
                "startup": startup_data,
                "error": str(e),
                "processed_at": datetime.now().isoformat()
            }
    
    async def process_startups(self, startups_data: List[Dict[str, str]]) -> str:
        """Process a list of startups and generate analysis for each.
        
        Args:
            startups_data: List of startup dictionaries with name, industry, country, website keys
            
        Returns:
            Path to the reference file with all analyses
        """
        # Archive old files if requested
        print("Archiving old analysis files...")
        await self._archive_old_files()
        print("Archiving complete\n")
        
        # Process startups in batches
        batch_size = 10
        batches = [startups_data[i:i+batch_size] 
                  for i in range(0, len(startups_data), batch_size)]
        
        # Track results
        results = []
        
        # Process each batch
        for i, batch in enumerate(batches, 1):
            print(f"\nProcessing batch {i} of {len(batches)}\n")
            
            # Process each startup in parallel
            tasks = [self.process_startup(startup) for startup in batch]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
        
        # Create reference file with all analyses
        reference_file = await self._create_reference_file()
        
        return reference_file
    
    #-------------------------------------------------------------------------
    # Web Scraping Methods
    #-------------------------------------------------------------------------
    
    async def _scrape_startup_website(self, url: str) -> Dict[str, Any]:
        """Scrape comprehensive information about a startup from their website.
        
        Note: This data is used for analysis but not stored in the output files
        to reduce file size. The data is only kept in memory during processing.
        """
        if not self.session:
            await self.initialize()
            
        try:
            # Normalize URL
            url = url.rstrip('/')
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            # Initialize result dictionary
            result = {
                "main_content": "",
                "about_page": "",
                "team_page": "",
                "product_pages": [],
                "blog_posts": [],
                "social_media": {},
                "contact_info": {},
                "meta_data": {},
                "scrape_date": datetime.now().isoformat()
            }

            # Scrape main page
            main_content = await self._scrape_page(url)
            result["main_content"] = main_content

            # Extract and scrape important pages
            soup = BeautifulSoup(main_content, 'html.parser')
            
            # Find and scrape about page
            about_url = self._find_page_url(soup, ['about', 'about-us', 'company', 'who-we-are'], url)
            if about_url:
                result["about_page"] = await self._scrape_page(about_url)

            # Find and scrape team page
            team_url = self._find_page_url(soup, ['team', 'people', 'leadership', 'about-team'], url)
            if team_url:
                result["team_page"] = await self._scrape_page(team_url)

            # Extract contact information
            result["contact_info"] = self._extract_contact_info(soup)

            # Extract social media links
            result["social_media"] = self._extract_social_media(soup)
            
            # Extract meta data
            result["meta_data"] = self._extract_meta_data(soup)

            return result

        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return {"error": str(e)}

    async def _scrape_page(self, url: str) -> str:
        """Scrape a single page and return its content."""
        if url in self.visited_urls:
            return ""
            
        try:
            async with self.session.get(url, ssl=self.ssl_context) as response:
                if response.status == 200:
                    self.visited_urls.add(url)
                    return await response.text()
                return ""
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return ""

    def _find_page_url(self, soup: BeautifulSoup, keywords: List[str], base_url: str) -> Optional[str]:
        """Find URL of a page based on keywords in links."""
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            if any(keyword in href for keyword in keywords):
                return urljoin(base_url, href)
        return None

    def _extract_contact_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract contact information from the page."""
        contact_info = {}
        
        # Look for email addresses
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, soup.get_text())
        if emails:
            contact_info['email'] = emails[0]

        # Look for phone numbers
        phone_pattern = r'\+?[\d\s\-\(\)]{10,}'
        phones = re.findall(phone_pattern, soup.get_text())
        if phones:
            contact_info['phone'] = phones[0]

        return contact_info

    def _extract_social_media(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract social media links."""
        social_media = {}
        social_patterns = {
            'linkedin': r'linkedin\.com',
            'twitter': r'twitter\.com|x\.com',
            'facebook': r'facebook\.com',
            'instagram': r'instagram\.com'
        }
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            for platform, pattern in social_patterns.items():
                if re.search(pattern, href):
                    social_media[platform] = href
                    break

        return social_media

    def _extract_meta_data(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract meta data from the page."""
        meta_data = {}
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            meta_data['description'] = meta_desc.get('content', '')

        # Extract meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            meta_data['keywords'] = meta_keywords.get('content', '')

        return meta_data
    
    #-------------------------------------------------------------------------
    # AI Analysis Methods
    #-------------------------------------------------------------------------
    
    async def _analyze_startup(self, startup: Dict[str, str], website_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a startup using AI with Google Search integration"""
        # Create prompt for the model
        prompt = self._create_analysis_prompt(startup, website_data)
        
        try:
            # Initialize the Gemini model with maximum parameters
            model = genai.GenerativeModel(
                'gemini-2.0-flash',
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 8192,  # Maximum available
                }
            )
            
            # Generate content
            response = await asyncio.to_thread(
                model.generate_content,
                prompt
            )
            
            # Parse and return the result
            return self._parse_analysis(response)
        except Exception as e:
            print(f"Error analyzing startup: {str(e)}")
            return {"error": str(e)}
    
    def _create_analysis_prompt(self, startup: Dict[str, str], website_data: Dict[str, Any]) -> str:
        """Create a comprehensive prompt for mentor/consultant-level startup analysis"""
        # Extract relevant data for the prompt
        name = startup.get("name", "Unknown")
        industry = startup.get("industry", "Unknown")
        country = startup.get("country", "Unknown")
        website = startup.get("website", "Unknown")
        
        main_content = website_data.get("main_content", "")[:10000]  # Increased limit
        about_page = website_data.get("about_page", "")[:10000]
        team_page = website_data.get("team_page", "")[:5000]
        
        # Create search queries for additional context
        search_queries = [
            f"{name} company overview funding",
            f"{name} founders background experience",
            f"{name} {industry} product technology",
            f"{name} customers clients case studies",
            f"{name} market position competitors",
            f"{name} team leadership executives",
            f"{name} funding investors investment rounds",
            f"{name} technology stack architecture",
            f"{name} recent news press releases",
            f"{name} growth metrics revenue"
        ]
        
        # Create an in-depth analysis prompt for mentoring/consulting purposes
        return f"""You are an elite-level startup mentor and management consultant with deep technical expertise. Conduct an extremely comprehensive analysis of {name}, a startup in the {industry} sector based in {country}.

Use all available information, including the website content provided and your up-to-date knowledge. 

STARTUP INFORMATION:
- Name: {name}
- Industry: {industry}
- Location: {country}
- Website: {website}

WEBSITE CONTENT OVERVIEW:
{main_content[:1000]}...

ABOUT PAGE CONTENT:
{about_page[:1000]}...

TEAM INFORMATION:
{team_page[:1000]}...

KEY SEARCH AREAS TO CONSIDER:
{chr(10).join(f"- {q}" for q in search_queries)}

PROVIDE AN EXTREMELY DETAILED ANALYSIS WITH ACTIONABLE INSIGHTS IN THE FOLLOWING STRUCTURE:

1. EXECUTIVE SUMMARY
   - Core Business Description
   - Key Value Proposition
   - Current Stage of Development
   - Market Opportunity Overview
   - Most Critical Success Factors

2. FOUNDER & TEAM ASSESSMENT
   - Founder Background and Strengths/Weaknesses
   - Team Composition Analysis
   - Technical Expertise Assessment
   - Leadership Capabilities
   - Key Management Gaps
   - Hiring Priorities
   - Team Dynamics and Culture Observations

3. MARKET ANALYSIS
   - Total Addressable Market Size and Growth Rate
   - Serviceable Obtainable Market
   - Market Segment Analysis
   - Target Customer Profiles
   - Customer Pain Points
   - Regional Market Variations
   - Market Timing Considerations
   - Regulatory Environment

4. COMPETITIVE LANDSCAPE
   - Direct Competitors Analysis
   - Indirect Competitors
   - Comparative Advantages and Disadvantages
   - Defensibility Assessment
   - Differentiation Factors
   - Potential Future Competitors
   - Competitive Response Strategies

5. PRODUCT & TECHNOLOGY ASSESSMENT
   - Product Maturity Evaluation
   - Core Technology Strengths
   - Technical Debt Assessment
   - Architecture Scalability
   - Security Posture
   - Development Roadmap Analysis
   - Technical Risks and Mitigations
   - IP and Proprietary Technology Value
   - Engineering Team Capabilities
   - Technology Stack Evaluation
   - API and Integration Strategy
   - Data Strategy

6. BUSINESS MODEL ANALYSIS
   - Revenue Model Assessment
   - Unit Economics Breakdown
   - Customer Acquisition Strategy
   - Customer Lifetime Value
   - Pricing Strategy Analysis
   - Sales Cycle Dynamics
   - Distribution Channels
   - Partnerships and Ecosystem
   - Operational Scalability

7. FINANCIAL SITUATION
   - Current Funding Status
   - Burn Rate Assessment
   - Runway Estimation
   - Capital Efficiency
   - Revenue Projections Realism
   - Fundraising Strategy Recommendations
   - Potential Investor Types
   - Valuation Considerations

8. GROWTH STRATEGY ASSESSMENT
   - Go-to-Market Strategy Evaluation
   - Growth Levers Identification
   - International Expansion Potential
   - Marketing Effectiveness
   - Customer Retention Strategies
   - Product Expansion Opportunities
   - Strategic Partnership Opportunities
   - M&A Considerations

9. RISK ASSESSMENT
   - Market Risks
   - Technology Risks
   - Execution Risks
   - Competitive Risks
   - Financial Risks
   - Regulatory/Legal Risks
   - Team Risks
   - Prioritized Risk Mitigation Strategies

10. SWOT ANALYSIS
    - Core Strengths (5-7 detailed points)
    - Primary Weaknesses (5-7 detailed points)
    - Key Opportunities (5-7 detailed points)
    - Critical Threats (5-7 detailed points)

11. MENTORING RECOMMENDATIONS
    - Strategic Priorities (next 3-6 months)
    - Product Development Focus Areas
    - Technical Architecture Recommendations
    - Team Building Priorities
    - Business Model Optimization
    - Fundraising Strategy
    - Growth Acceleration Tactics
    - Marketing and Sales Improvements
    - Operational Efficiency Opportunities
    - Key Performance Metrics to Track
    - Most Important Immediate Actions

Return your extremely comprehensive analysis in a well-structured JSON format. Focus on providing deep technical insights, business strategy recommendations, and highly specific mentoring advice that would be valuable to the founders. This should be as detailed and comprehensive as possible within the token limits.
"""
    
    def _parse_analysis(self, text: str) -> Dict[str, Any]:
        """Parse the analysis from AI response into structured data"""
        try:
            # Handle response object vs string
            if not isinstance(text, str):
                # If it's a response object, get the text
                if hasattr(text, 'text'):
                    text = text.text
                elif hasattr(text, 'parts') and len(text.parts) > 0:
                    text = text.parts[0].text
                else:
                    # Try to convert to string
                    text = str(text)
            
            # Try to extract JSON
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = text[start_idx:end_idx]
                return json.loads(json_str)
            
            # Fall back to section parsing if JSON extraction fails
            sections = {}
            current_section = None
            current_content = []
            
            for line in text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                # Check for section headers (e.g., "1. Company Overview")
                if any(f"{i}." in line for i in range(1, 7)):
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content)
                    current_section = line.split('.', 1)[1].strip().lower().replace(' ', '_')
                    current_content = []
                else:
                    current_content.append(line)
            
            # Add the last section
            if current_section and current_content:
                sections[current_section] = '\n'.join(current_content)
            
            return sections
            
        except Exception as e:
            print(f"Error parsing analysis: {str(e)}")
            print(f"Raw text: {str(text)[:200]}...")
            return {"error": f"Failed to parse analysis: {str(e)}"}
    
    #-------------------------------------------------------------------------
    # File Management Methods
    #-------------------------------------------------------------------------
    
    async def _save_analysis(self, startup_name: str, data: Dict[str, Any]) -> Path:
        """Save analysis data to a new JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{startup_name.lower().replace(' ', '_')}_{timestamp}.json"
        filepath = self.raw_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
            
        return filepath
    
    async def _create_reference_file(self) -> Path:
        """Combine all startup analyses into a single reference file."""
        # Get all JSON files in the raw directory
        json_files = list(self.raw_dir.glob("*.json"))
        
        # Skip reference files and files with known patterns that aren't startup analyses
        json_files = [
            f for f in json_files 
            if "startup_reference" not in f.name 
            and "enriched_startups" not in f.name
        ]
        
        # Initialize the reference data structure
        reference_data = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "total_startups": len(json_files)
            },
            "startups": {}
        }
        
        # Process each startup file
        for file_path in json_files:
            try:
                with open(file_path, 'r') as f:
                    startup_data = json.load(f)
                    
                # Validate expected structure - skip if not a valid startup analysis file
                if not isinstance(startup_data, dict) or "startup" not in startup_data:
                    print(f"Skipping {file_path.name}: Not a valid startup analysis file")
                    continue
                    
                # Extract startup name from the data
                startup_name = startup_data.get("startup", {}).get("name", "unknown")
                if not startup_name or startup_name == "unknown":
                    # Try to extract from filename
                    startup_name = file_path.stem.split('_')[0]
                
                # Make sure website_data is not included
                if "website_data" in startup_data:
                    del startup_data["website_data"]
                
                # Add to reference data
                reference_data["startups"][startup_name] = startup_data
                
            except Exception as e:
                print(f"Error processing {file_path.name}: {str(e)}")
        
        # Save the reference file to the refined directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reference_file = self.refined_dir / f"startup_reference_{timestamp}.json"
        
        with open(reference_file, 'w') as f:
            json.dump(reference_data, f, indent=2)
            
        return reference_file
    
    async def _archive_old_files(self) -> None:
        """Move files older than the threshold to the archive directory."""
        current_time = datetime.now()
        threshold = current_time - timedelta(days=self.days_to_archive)
        
        # Create date-based subdirectories in archive
        archive_date_dir = self.archive_dir / current_time.strftime("%Y%m")
        archive_date_dir.mkdir(exist_ok=True)
        
        # Process all JSON files in raw directory
        for file_path in self.raw_dir.glob("*.json"):
            # Skip reference files
            if "startup_reference" in file_path.name:
                continue
                
            file_stat = file_path.stat()
            file_time = datetime.fromtimestamp(file_stat.st_mtime)
            
            # Archive if file is older than threshold
            if file_time < threshold:
                # Create a new filename with archive date
                new_filename = f"{file_path.stem}_archived_{current_time.strftime('%Y%m%d')}{file_path.suffix}"
                new_path = archive_date_dir / new_filename
                
                # Move the file
                shutil.move(str(file_path), str(new_path))
                print(f"Archived: {file_path.name} -> {new_path.name}")

# Example usage
async def main():
    # Sample startup data
    startups = [
        {
            "name": "TechStartup1",
            "industry": "AI",
            "country": "USA",
            "website": "techstartup1.com"
        },
        {
            "name": "GreenEnergy2",
            "industry": "Renewable Energy",
            "country": "Germany",
            "website": "greenenergy2.de"
        }
    ]
    
    # Initialize and run the pipeline
    async with StartupResearchPipeline() as pipeline:
        reference_file = await pipeline.process_startups(startups)
        print(f"Process complete. Reference file: {reference_file}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 