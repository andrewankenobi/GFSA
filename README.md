# GFSA AI First 2025 Berlin Cohort Analysis

A comprehensive analysis platform for the Google for Startups Accelerator AI First 2025 Berlin Cohort, featuring startup analysis, task management, and AI-powered insights.

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
- Node.js (for web interface)
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
# Edit .env with your API keys and configuration
```

5. Run the analysis:
```bash
python research.py
```

6. Start the web server:
```bash
flask run
```

7. Open [http://localhost:5000](http://localhost:5000) with your browser to see the application.

## Project Structure

```
GFSA/
├── app/
│   ├── models.py          # Data models including Todo
│   ├── static/           # Static assets (CSS, JavaScript)
│   ├── templates/        # HTML templates
│   └── views/           # Flask route definitions
├── data/                # Data storage
│   ├── results/         # Analysis results
│   ├── raw/            # Raw analysis data
│   └── archive/        # Archived analysis files
├── research.py         # Main analysis script
├── startups.json       # Source startup data
├── requirements.txt    # Python dependencies
└── README.md
```

## Key Components

### Web Interface
- `index.html`: Main startup listing and search interface
- `details.html`: Detailed startup view with AI analysis
- Responsive design with modern UI/UX
- Real-time search functionality
- Dynamic data loading

### Analysis Features
- AI-powered startup analysis
- Market opportunity assessment
- Competitive analysis
- Risk evaluation
- Growth trajectory prediction
- Founder background analysis
- Funding stage assessment
- Product development stage tracking

### Data Management
- Automatic archiving of old analyses
- Version control of analysis results
- Raw data preservation
- Structured JSON data format
- Startup metadata tracking
- Historical analysis preservation

## Built With

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Python](https://www.python.org/) - Backend language
- [Google Cloud AI](https://cloud.google.com/ai-platform) - AI/ML capabilities
- [Flask-Assets](https://flask-assets.readthedocs.io/) - Asset management
- [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript) - Frontend interactivity

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
3. Results storage (`data/results/`)
4. Web interface presentation
5. AI-powered insights generation
6. Interactive user queries
7. Automatic data archiving

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