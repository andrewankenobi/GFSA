# Task Manager

A simple task management feature integrated into the Startup Analysis Flask application. This allows you to manage tasks while analyzing startup data.

## Features

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

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/startup-analysis.git
cd startup-analysis
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

4. Run the application:
```bash
flask run
```

5. Open [http://localhost:5000](http://localhost:5000) with your browser to see the application.

## Project Structure

```
startup-analysis/
├── app/
│   ├── models.py        # Data models including Todo
│   ├── static/          # Static assets (CSS, JavaScript)
│   ├── templates/       # HTML templates
│   └── views/           # Flask route definitions
├── data/                # Data storage
├── requirements.txt     # Python dependencies
└── README.md
```

## Built With

- [Flask](https://flask.palletsprojects.com/) - The web framework used
- [Python](https://www.python.org/) - Backend language
- [Flask-Assets](https://flask-assets.readthedocs.io/) - Asset management 