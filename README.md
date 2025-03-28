# GFSA AI First 2025 Berlin Cohort Analysis

A comprehensive analysis platform for the Google for Startups Accelerator AI First 2025 Berlin Cohort, featuring startup analysis and AI-powered insights.

![GFSA Logo](gfsa.png)
![Berlin Skyline](berlin.gif)

## Overview

This application provides a comprehensive analysis platform for the Google for Startups Accelerator AI First 2025 Berlin Cohort. It combines AI-powered analysis with an interactive web interface to provide detailed insights about participating startups.

## Application Flow

1. **Data Collection & Analysis**
   - Run `research.py` to analyze startup data from `startups.json`
   - Generates detailed analysis in JSON format
   - Creates `analysis_YYYYMMDD_HHMMSS.json` in root directory

2. **Web Interface**
   - Frontend server serves static files (HTML, CSS, JS)
   - Backend server provides API endpoints for analysis and chat
   - Interactive startup cards with detailed information
   - Real-time search functionality

3. **AI Features**
   - AI-powered startup analysis
   - Interactive chat assistant
   - Market opportunity assessment
   - Competitive analysis
   - Risk evaluation

## Features

### Startup Analysis
- 🔍 Detailed startup information analysis using Google's Gemini API
- 📊 Interactive web interface for viewing startup details
- 💡 AI-powered insights and recommendations
- 🤖 Interactive AI assistant for startup-specific queries
- 📈 Comprehensive market and business analysis
- 🔄 Automatic data archiving and version control

## Getting Started

### Prerequisites

- Python 3.8 or later
- pip
- Google Gemini API key (for AI features)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/GFSA.git
cd GFSA
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create a .env file in the root directory
# Add your Gemini API key in the following format:
# GEMINI_API_KEY=your_api_key_here

# You can use the example file as a template:
cp .env.example .env
# Then edit .env with your GEMINI_API_KEY
```

> **Important**: The `.env` file contains sensitive information and is excluded from version control. Never commit this file to your repository.

### Obtaining a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and add it to your `.env` file

### Running the Application

1. **First Time Setup - Run Research Analysis**
```bash
python research.py
```
This will:
- Analyze startup data from startups.json
- Generate analysis JSON files
- Create necessary directories

2. **Start the Application**
```bash
./start.sh
```
This will:
- Start the backend server (port 5000)
- Start the frontend server (port 8000)
- Open the application in your browser

3. **Access the Application**
- Frontend: http://localhost:8000
- Backend API: http://localhost:5000

## Project Structure

```
GFSA/
├── index.html           # Main startup listing interface
├── details.html         # Detailed startup view
├── server.py            # Flask backend server
├── research.py          # Startup analysis script
├── chat_agent.py        # AI chat assistant
├── startups.json        # Source startup data
├── analysis_*.json      # Generated analysis files
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not in version control)
├── .env.example         # Example environment variables file
├── start.sh             # Main startup script
├── start_backend.sh     # Backend server script
├── start_frontend.sh    # Frontend server script
└── README.md
```

## API Endpoints

The application provides the following API endpoints:

### Backend API
- `POST /api/analyze-startup` - Generate AI analysis for a startup
- `POST /api/chat` - Interactive AI assistant endpoint

### Static File Serving
- `/` - Serves the main index.html file
- `/<path:path>` - Serves other static files

## Data Flow

1. Raw startup data (`startups.json`)
2. Analysis processing (`research.py`)
3. Results storage (`analysis_*.json`)
4. Web interface presentation (index.html, details.html)
5. AI-powered insights generation (server.py)
6. Interactive user queries (chat_agent.py)

## Development

### Running Individual Components

1. **Backend Server Only**
```bash
./start_backend.sh
```

2. **Frontend Server Only**
```bash
./start_frontend.sh
```

### Debugging

- Backend logs are available in the terminal
- Frontend console logs are available in browser dev tools
- Check `startup_research.log` for research analysis logs

### Important Notes

1. **Environment Variables**: The `.env` file contains sensitive API keys and is not included in the repository. Always create this file locally.

2. **Research Output**: The research script outputs files to the root directory. Make sure these files are accessible to the web servers.

3. **Analysis Files**: The frontend looks for specific analysis files. If you're having trouble, check that the file name matches what the frontend is looking for.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details

## Acknowledgments

- Google for Startups Accelerator
- All participating startups in the AI First 2025 Berlin Cohort
- Contributors and maintainers
- The startup founders and teams for their valuable insights 