# Startup Research Pipeline

A streamlined system for extracting, analyzing, and managing startup data through web scraping and AI-powered analysis with Google Search integration.

## Overview

This application provides an end-to-end solution for researching startups:

1. **Web Scraping**: Extracts content from startup websites including about pages, team information, social media links, and contact details
2. **AI Analysis**: Uses Google's Gemini 2.0 Flash with mandatory Google Search integration to generate comprehensive startup insights
3. **Data Management**: Creates structured JSON outputs for historical reference and consumption

## Features

- **Comprehensive Web Scraping**: Intelligent extraction of key pages and information
- **AI-Powered Analysis**: Structured analysis of business model, market position, SWOT, investment potential, and technology
- **Required Google Search Grounding**: Enhances analysis with real-time web search data using Google's official API
- **Efficient Data Processing**: Asynchronous operations for optimized performance
- **Smart File Management**: Automatic archiving of old data and generation of reference files

## Directory Structure

```
├── data                                # Data storage
│   ├── raw                             # Raw startup analysis files
│   ├── archive                         # Archived older files
│   └── refined                         # Processed reference and enriched files
└── app                                 # Application code
    ├── __init__.py                     # Application initialization
    ├── run_research.py                 # Entry point for research pipeline
    └── research/                       # Research module
        ├── __init__.py                 # Module initialization
        ├── __main__.py                 # Module entry point
        ├── startup_research_pipeline.py # Main pipeline implementation
        ├── run_pipeline.py             # Pipeline runner
        ├── startup_parser.py           # Parser for startup data files
        ├── convert_startups.py         # Utility to convert TXT to JSON
        ├── startups.json               # Converted startup data
        └── startups.txt                # Original startups list
```

## Google Search Integration

The pipeline requires Google's official Gemini API with Google Search grounding to enhance startup analysis with the latest web information. This provides:

- Up-to-date market positioning information
- Recent company developments
- Competitive landscape insights
- Funding and investment details

The implementation uses Google's recommended approach using the Client API:

```python
from google import genai
from google.genai import types

# Configure client
client = genai.Client(api_key=api_key)

# Set up Google Search tools
tools = [types.Tool(google_search=types.GoogleSearch())]
```

## Usage

1. Create a `.env` file with your Gemini API key (already provided):
```
GEMINI_API_KEY=your_api_key_here
```

2. Prepare your startup data in one of two formats:

   a. **Tab-separated text file** (like the provided `startups.txt`):
   ```
   Startup Name     Country     Industry    Website
   Example Corp     USA         Tech        example.com
   ```

   b. **JSON array**:
   ```json
   [
     {
       "name": "Example Corp",
       "industry": "Tech",
       "country": "USA", 
       "website": "example.com"
     }
   ]
   ```

3. Run the research pipeline:

```bash
# Run with default startups.txt
python app/run_research.py

# Run with custom input file
python app/run_research.py path/to/your/startups.txt
# OR
python app/run_research.py path/to/your/startups.json
```

4. Alternatively, you can use the Python module directly:

```bash
# Run with default startups.txt
python -m app.research

# Run with custom input file
python -m app.research path/to/your/startups.txt
```

5. To convert a startups.txt file to JSON format:

```bash
# Run the converter directly
python app/research/convert_startups.py input.txt output.json
```

## Output Files

The pipeline generates several types of files:

1. **Individual startup analysis files** in `data/raw/` with format: `startup_name_TIMESTAMP.json`
2. **Reference files** combining all analyses in `data/refined/` with format: `startup_reference_TIMESTAMP.json`

## Analysis Content

For each startup, the pipeline generates:

- **Executive Summary**: Core business description, value proposition, stage of development
- **Founder & Team Assessment**: Backgrounds, expertise, hiring needs
- **Market Analysis**: Market size, customer profiles, regulatory environment
- **Competitive Landscape**: Direct and indirect competitors, differentiation
- **Product & Technology**: Technical architecture, strengths, scalability
- **Business Model**: Revenue model, unit economics, pricing strategy
- **Financial Situation**: Funding status, burn rate, capital efficiency
- **Growth Strategy**: Go-to-market approach, expansion opportunities
- **Risk Assessment**: Market, technical, execution, and financial risks
- **SWOT Analysis**: Detailed strengths, weaknesses, opportunities, and threats
- **Mentoring Recommendations**: Strategic priorities, development focus areas

## Dependencies

- Python 3.8+
- aiohttp
- BeautifulSoup4
- google-generativeai
- python-dotenv
- requests

## Installation

```bash
pip install -r requirements.txt
```