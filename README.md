# Startup Analyzer Suite

A comprehensive suite for startup analysis, including a research pipeline for data gathering and a web application for visualization and interaction.

## Overview

This solution consists of two main components:

1. **Research Pipeline**: Extracts and analyzes startup data using AI-powered analysis with Google Search integration
2. **Web Application**: Visualizes startup data and provides an interactive chat interface for data exploration

## Features

### Research Pipeline

- **Comprehensive Web Scraping**: Intelligent extraction of key pages and information
- **AI-Powered Analysis**: Structured analysis of business model, market position, SWOT, investment potential, and technology
- **Required Google Search Grounding**: Enhances analysis with real-time web search data using Google's official API
- **Efficient Data Processing**: Asynchronous operations for optimized performance
- **Smart File Management**: Automatic archiving of old data and generation of reference files

### Web Application

- **Dashboard with clickable startup cards**: Quick access to all analyzed startups
- **Detailed startup analysis pages**: Comprehensive view of all analysis data
- **AI chat assistant using Gemini 2.0**: Interactive query functionality with search grounding
- **Cross-reference information between startups**: Compare and analyze multiple startups

## Directory Structure

```
├── data                                # Data storage
│   ├── raw                             # Raw startup analysis files
│   ├── archive                         # Archived older files
│   └── refined                         # Processed reference and enriched files
└── app                                 # Application code
    ├── __init__.py                     # Application initialization
    ├── run_research.py                 # Entry point for research pipeline
    ├── run_webapp.py                   # Entry point for web application
    ├── web_app.py                      # Main web application implementation
    ├── templates/                      # Web templates
    │   ├── base.html                   # Base template with layout and styling
    │   ├── index.html                  # Dashboard template
    │   └── detail.html                 # Startup detail template with chat
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

## Requirements

- Python 3.8+
- Google Gemini API key

## Installation

1. Clone this repository
2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Set your Gemini API key as an environment variable:

```bash
export GEMINI_API_KEY='your-api-key'
```

## Usage

### Running the Web Application

Execute the web application:

```bash
./app/run_webapp.py
```

Then open your browser and navigate to `http://localhost:5000`

### Running the Research Pipeline

1. Prepare your startup data in one of two formats:

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

2. Run the research pipeline:

```bash
# Run with default startups.txt
./app/run_research.py

# Run with custom input file
./app/run_research.py path/to/your/startups.txt
# OR
./app/run_research.py path/to/your/startups.json
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

## Web App Navigation

1. **Home Page**: Displays cards for all startups in the database.
2. **Startup Detail Page**: Shows comprehensive analysis of a selected startup.
3. **Chat Interface**: Available on the detail page, allowing you to:
   - Ask questions about the current startup
   - Compare with other startups in the database
   - Get insights grounded in the startup data