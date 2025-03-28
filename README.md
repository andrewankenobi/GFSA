# GFSA AI First 2025 Berlin Cohort Analysis

A comprehensive analysis platform for the Google for Startups Accelerator AI First 2025 Berlin Cohort, featuring startup analysis, task management, and AI-powered insights.

![GFSA Logo](gfsa.png)
![Berlin Skyline](berlin.gif)

## Overview

This application provides a comprehensive analysis platform for the Google for Startups Accelerator AI First 2025 Berlin Cohort. It combines AI-powered analysis with an interactive web interface to provide detailed insights about participating startups.

## Application Flow

1. **Data Collection & Analysis**
   - Run `research.py` to analyze startup data
   - Generates detailed analysis in JSON format
   - Creates `analysis_YYYYMMDD_HHMMSS.json` in root directory

2. **Web Interface**
   - Frontend server serves static files (HTML, CSS, JS)
   - Backend server provides API endpoints for analysis and chat
   - Interactive startup cards with detailed information
   - Real-time search functionality

3. **AI Features**
   - AI-powered startup analysis
   - Interactive chat assistant (Ment-hoff)
   - Market opportunity assessment
   - Competitive analysis
   - Risk evaluation

## Features

### Startup Analysis
- 🔍 Detailed startup information analysis using AI
- 📊 Interactive web interface for viewing startup details
- 💡 AI-powered insights and recommendations
- 🤖 Interactive AI assistant (Ment-hoff) for startup-specific queries
- 📈 Comprehensive market and business analysis
- 🔄 Automatic data archiving and version control
- 🌍 Multi-country startup coverage (UK, Spain, Israel, Denmark, Germany, France, Ukraine)

### Task Management
- ✨ Beautiful dark theme UI matching the existing application
- 📝 Create, read, update, and delete tasks
- ✅ Mark tasks as completed
- 🔍 Filter tasks by status (All, Completed, Pending)
- 🎯 Task descriptions support
- 📱 Responsive design

## Getting Started

### Prerequisites

- Python 3.8 or later
- pip
- Google Cloud API key (for AI features)

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
cp .env.example .env
# Edit .env with your GEMINI_API_KEY
```

### Running the Application

1. **First Time Setup - Run Research Analysis**
```bash
python research.py
```
This will:
- Analyze startup data
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
├── server.py           # Flask backend server
├── research.py         # Startup analysis script
├── chat_agent.py       # AI chat assistant
├── startups.json       # Source startup data
├── analysis_*.json     # Generated analysis files
├── requirements.txt    # Python dependencies
├── start.sh           # Main startup script
├── start_backend.sh   # Backend server script
├── start_frontend.sh  # Frontend server script
└── README.md
```

## API Endpoints

### Analysis API
- `/api/analyze-startup` - Generate AI analysis for a startup
- `/api/chat` - Interactive AI assistant endpoint
- `/api/startups` - List all startups
- `/api/startup/<id>` - Get detailed startup information

### Task Management API
- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/<id>` - Update task
- `DELETE /api/tasks/<id>` - Delete task

## Data Flow

1. Raw startup data (`startups.json`)
2. Analysis processing (`research.py`)
3. Results storage (`analysis_*.json`)
4. Web interface presentation
5. AI-powered insights generation
6. Interactive user queries
7. Automatic data archiving

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