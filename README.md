# GFSA AI First 2025 Berlin Cohort Analysis & Interaction Platform

A comprehensive analysis and interaction platform for the Google for Startups Accelerator AI First 2025 Berlin Cohort, featuring automated startup analysis, AI-powered insights, on-demand refresh capabilities, and an interactive chat assistant.

![GFSA Logo](gfsa.png)
![Berlin Skyline](berlin.gif)

## Overview

This application provides a dynamic platform for analyzing and interacting with information about the startups participating in the Google for Startups Accelerator AI First 2025 Berlin Cohort. It combines automated data gathering and analysis using Google's Gemini API with an interactive web interface. Key features include detailed startup profiles, AI-generated summaries and follow-up points, an AI chat assistant for specific queries, and the ability to trigger on-demand analysis refreshes with progress tracking.

## Features

- 🔍 **Automated Startup Analysis:** Runs `research.py` to analyze startup data from `startups.json` using the Gemini API, covering multiple facets like company overview, product, market, team, etc.
- 💾 **Structured Data Output:** Generates detailed analysis results stored in individual JSON files (`data/results/analysis_STARTUPNAME.json`).
- 🌐 **Interactive Web Interface:**
    - Main page (`index.html`) displaying a searchable list of startups.
    - Detailed view (`details.html`) for each startup, presenting the structured analysis in distinct, organized sections.
    - Custom layouts for key sections like "Company Overview" and "Team Analysis" for better readability.
- ✨ **AI-Powered Insights:**
    - An "AI Analysis" section on the details page providing an executive summary and actionable technical/business follow-up items generated by a separate AI call (`/api/analyze-startup`).
    - 🤖 An interactive AI chat assistant (`Ment-hoff`) allowing users to ask specific questions about the currently viewed startup (`/api/chat`).
- 🔄 **On-Demand Analysis Refresh:**
    - "Refresh Analysis" button on the details page triggers a background re-analysis of the specific startup using `research.py`.
    - 🔒 Prevents concurrent analysis runs for the same startup using a lock file mechanism (`.research.lock`).
    - 📊 Displays real-time progress updates (which analysis section is running, progress bar) while the refresh is active.
- 🧹 **Configurable Archiving:** Automatically archives previous analysis files (`data/archive/`) and implements version-based cleanup, keeping only the last N versions (configurable via `ARCHIVE_VERSIONS_TO_KEEP` in `research.py`).

## Getting Started

### Prerequisites

- Python 3.8 or later
- `pip` (Python package installer)
- `python3-venv` (Recommended for creating virtual environments)
- Google Gemini API key

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd GFSA
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    -   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    -   Edit the `.env` file and add your Google Gemini API key:
        ```
        GEMINI_API_KEY=your_api_key_here
        ```
    > **Important**: The `.env` file contains sensitive information. It is included in `.gitignore` and should *never* be committed to version control.

### Obtaining a Gemini API Key

1.  Go to [Google AI Studio](https://makersuite.google.com/app/apikey).
2.  Sign in with your Google account.
3.  Create a new API key.
4.  Copy the key and paste it into your `.env` file.

### Running the Application

1.  **First Time Setup - Initial Research Analysis:**
    Run the research script to perform the initial analysis for all startups defined in `startups.json`.
    ```bash
    python research.py
    ```
    This script will:
    - Create the `data/`, `data/results/`, and `data/archive/` directories if they don't exist.
    - For each startup:
        - Call the Gemini API multiple times to analyze different sections (Company Overview, Product, Market, etc.).
        - Save the results for each section temporarily.
        - Archive any pre-existing analysis data.
        - Assemble the final analysis into `data/results/analysis_STARTUPNAME.json`.
    - Perform archive cleanup based on the configured version retention policy.

2.  **Start the Servers:**
    Use the provided shell script to start both the backend Flask server and the frontend development server.
    ```bash
    ./start.sh
    ```
    This script executes:
    - `start_backend.sh`: Runs `python server.py` (typically on port 5002).
    - `start_frontend.sh`: Runs `python -m http.server 8000` (or similar, on port 8000).
    - It should also attempt to open the application in your default browser.

3.  **Access the Application:**
    -   **Frontend:** Open your web browser and navigate to `http://localhost:8000` (or the port specified by `start_frontend.sh`).
    -   **Backend API (for reference):** The backend runs on `http://localhost:5002` (or the port specified in `server.py`).

## Workflow Details

1.  **Initial Load (`index.html`):** The main page fetches `startups.json` and displays a searchable list/grid of startups.
2.  **Viewing Details (`details.html`):**
    -   Clicking a startup card navigates to `details.html?startup=STARTUPNAME`.
    -   The page fetches the corresponding `data/results/analysis_STARTUPNAME.json` file.
    -   JavaScript (`displayStartupDetails`) parses the JSON and renders the different analysis sections into predefined areas using specific layouts (e.g., 4-column top row for Company Overview, vertical stack for Team Analysis Founders).
    -   Simultaneously, it calls the backend `/api/analyze-startup` endpoint, sending basic startup info. The backend uses Gemini to generate the Executive Summary and Follow-up Items displayed in the left-hand AI Analysis panel.
    -   The chat interface (`Ment-hoff`) is initialized, ready for user queries.
3.  **Chat Interaction:**
    -   User types a question and clicks "Send".
    -   Frontend sends the query and the *full context* (`startupData` from the loaded JSON) to the backend `/api/chat` endpoint.
    -   The backend (`chat_agent.py`) uses Gemini, informed by the provided context, to generate a response.
    -   The response is displayed in the chat window.
4.  **On-Demand Refresh Analysis:**
    -   User clicks the "↻ Refresh Analysis" button on `details.html`.
    -   Frontend JavaScript (`refreshButton` listener):
        -   Logs the click action.
        -   Disables the button.
        -   Sends a POST request to the backend `/api/run-research` endpoint, including the startup name.
    -   Backend (`server.py` - `/api/run-research`):
        -   Checks if the lock file (`data/.research.lock`) exists. If yes, returns an HTTP 409 Conflict error ("Another process is already running...").
        -   If no lock file, it constructs the command: `python research.py --startup STARTUPNAME --workers 1`.
        -   It uses `subprocess.Popen` to start `research.py` as a *background process*.
        -   It immediately returns an HTTP 202 Accepted response to the frontend, indicating the process has started.
    -   `research.py` (when run with `--startup`):
        -   Attempts to create the lock file (`data/.research.lock`). If it fails (already exists), it exits.
        -   Creates a status file (`data/.research_status_STARTUPNAME.json`) indicating "starting_analysis".
        -   Performs cleanup and archiving.
        -   Iterates through analysis areas:
            -   Updates the status file (e.g., "analyzing_market_analysis").
            -   Calls the Gemini API for the area.
            -   Saves the result.
            -   Updates the status file (e.g., "completed_market_analysis").
        -   Updates status file ("assembling_final_json").
        -   Assembles the final `analysis_STARTUPNAME.json`.
        -   In a `finally` block, it **removes** both the lock file and the status file.
    -   Frontend JavaScript (upon receiving 202 Accepted):
        -   Immediately displays the "Refresh Status" UI area ("Initiated...").
        -   Starts polling (`setInterval`) the backend `/api/research-status?startup=STARTUPNAME` endpoint every few seconds (e.g., 3s).
    -   Backend (`server.py` - `/api/research-status`):
        -   Checks if `data/.research_status_STARTUPNAME.json` exists.
        -   If yes, reads it and returns the status JSON (e.g., `{ "status": "analyzing_market_analysis", "completed_areas": [...], "is_running": true }`).
        -   If no, returns `{ "is_running": false, "status": "not_running_or_completed" }`.
    -   Frontend JavaScript (Polling Callback):
        -   Receives the status from `/api/research-status`.
        -   If `is_running` is true, updates the status text and progress bar based on the `status` and `completed_areas` fields.
        -   If `is_running` is false, it stops the polling interval (`clearInterval`).
    -   Frontend JavaScript (Separate `checkForNewFile` Interval):
        -   Independently, checks if the main `data/results/analysis_STARTUPNAME.json` file has been updated (by trying to fetch it).
        -   When the fetch succeeds (after the background `research.py` finishes and saves the file), it reloads the page (`window.location.reload()`) to display the fresh data.

## Project Structure

```
GFSA/
├── data/
│   ├── archive/             # Archived previous analysis files (cleaned periodically)
│   ├── results/             # Latest analysis JSON files (e.g., analysis_folio.json)
│   ├── .research.lock       # Temporary lock file (exists only during research run)
│   └── .research_status_*.json # Temporary status file (exists only during single refresh)
├── venv/                  # Python virtual environment (if created)
├── .env                   # Environment variables (API Key - NOT COMMITTED)
├── .env.example           # Example environment file
├── .gitignore             # Files/directories ignored by Git
├── index.html             # Main startup listing page
├── details.html           # Detailed startup view page
├── server.py              # Backend Flask API server
├── research.py            # Main script for running startup analysis
├── chat_agent.py          # Logic for the AI chat assistant
├── startups.json          # Source data for startups
├── requirements.txt       # Python dependencies
├── start.sh               # Main startup script (runs backend & frontend)
├── start_backend.sh       # Script to start only the backend
├── start_frontend.sh      # Script to start only the frontend HTTP server
├── gfsa.png               # Logo image
├── berlin.gif             # Header image
└── README.md              # This file
```

## API Endpoints (`server.py`)

-   `POST /api/analyze-startup`: Receives basic startup info, calls Gemini, and returns AI-generated Executive Summary and Follow-up Items. Used for the left-hand panel on `details.html`.
-   `POST /api/chat`: Receives user query and full startup context, calls `chat_agent.py` (which uses Gemini), and returns the formatted chat response.
-   `POST /api/run-research`: Receives startup name, checks for lock file, starts `research.py` in the background if no lock exists. Returns 202 Accepted or 409 Conflict.
-   `GET /api/research-status`: Receives startup name (query param), checks for the status file, and returns its contents or an indication that the process isn't running.
-   Static File Serving: Serves `index.html`, `details.html`, `.js`, `.css`, images, and analysis JSON files from `data/results/`.

## Development

### Running Individual Components

1.  **Backend Server Only:**
    ```bash
    source venv/bin/activate
    python server.py
    ```
    (Check `server.py` for the configured port, usually 5002)

2.  **Frontend Server Only:**
    ```bash
    python -m http.server 8000
    ```
    (Or use any simple HTTP server)

### Debugging

-   Backend logs: Check the terminal where `server.py` is running and the `server.log` file.
-   Research script logs: Check the terminal where `research.py` was run (if run manually) and the `startup_research.log` file. Background runs triggered by the API will have their stdout/stderr captured by the `Popen` object in `server.py` but aren't logged by default unless modified.
-   Frontend logs: Check the browser's Developer Console (F12). Extensive `console.log` statements have been added to `details.html` to track the refresh/polling logic.

## Deployment to Google App Engine

This application is configured for deployment to the Google App Engine Standard Environment for Python.

### Prerequisites

-   Google Cloud SDK installed ([Installation Guide](https://cloud.google.com/sdk/docs/install)).
-   A Google Cloud Project with the App Engine Admin API enabled.
-   Authenticated `gcloud` CLI: Run `gcloud auth login` and `gcloud auth application-default login`.
-   Your Google Cloud Project ID.
-   Your Gemini API Key.

### Configuration Files

-   `app.yaml`: Defines the App Engine service configuration, including runtime, entrypoint (`gunicorn`), static file handlers, and environment variables (like the `GEMINI_API_KEY` placeholder).
-   `.gcloudignore`: Specifies files and directories (like `venv/`, `.env`, `logs/`) that should *not* be uploaded during deployment.

### Deployment Steps

1.  **Ensure Code is Ready:** Make sure your code reflects the App Engine configuration:
    -   `server.py` and `chat_agent.py` should *not* load `.env` files (remove `load_dotenv()` calls).
    -   `server.py` should *not* attempt to write to local log files (`FileHandler`). Logging to `stdout`/`stderr` (`StreamHandler`) is automatically captured by Cloud Logging.
    -   `server.py` should have `app.run(debug=False)` in the `if __name__ == '__main__':` block (App Engine handles host/port).
    -   `details.html` should use relative paths (e.g., `/api/analyze-startup`) for `fetch` calls to the backend API.
    -   Ensure `gunicorn` is listed in `requirements.txt`.

2.  **Run Initial Research (optional):** The `data/results/*.json` files are *static assets* included in the deployment. Run the initial analysis locally first to generate these files before deploying:
    ```bash
    python3 research.py
    ```
    > **Note:** Analysis files generated by the *deployed* app's "Refresh Analysis" feature are **ephemeral** and will be lost when instances restart. For persistent storage of refreshed data, modify the application to use Google Cloud Storage (GCS).

3.  **Set Target Project:**
    ```bash
    gcloud config set project YOUR_PROJECT_ID
    ```
    Replace `YOUR_PROJECT_ID` with your actual Google Cloud project ID.

4.  **Deploy:** Navigate to the project's root directory (containing `app.yaml`) in your terminal.
    -   **Ensure your `GEMINI_API_KEY` is correctly set** within the `env_variables` section of `app.yaml`.
    -   Run the deployment command:
    ```bash
    gcloud app deploy
    ```
    > **Security Note:** Storing secrets like API keys directly in `app.yaml` is convenient for testing but **not recommended for production** or if the code will be shared or committed to version control (unless `app.yaml` itself is gitignored).
    > For better security, prefer using the `--set-env-vars` flag during deployment (as shown previously) or storing the key in Google Secret Manager and fetching it in your application code.

    -   You might be prompted to choose a region if deploying for the first time.
    -   The deployment will upload files, build a container image, and start the service (named `gfsa` as defined in `app.yaml`).

5.  **Access the Application:** Once deployment finishes, `gcloud` will provide the URL (e.g., `https://gfsa-dot-YOUR_PROJECT_ID.REGION_CODE.r.appspot.com`). You can also use:
    ```bash
    gcloud app browse -s gfsa
    ```

### Important Considerations for App Engine

-   **Statelessness:** App Engine instances are stateless. Files written to the local filesystem *after* deployment (like refreshed analysis JSONs or lock files) are temporary and will be lost.
-   **Background Tasks:** The `research.py` script is started via `subprocess.Popen`. This has limitations in App Engine Standard regarding execution time and reliability. For robust background tasks, consider using **Cloud Tasks** or **Cloud Run Jobs**.
-   **API Key Security:** While `--set-env-vars` is better than hardcoding, using **Secret Manager** to store the `GEMINI_API_KEY` and fetching it at runtime in `server.py`/`chat_agent.py` is the most secure approach.
-   **Filesystem:** The application filesystem is read-only, except for the `/tmp` directory (which is an in-memory filesystem).

## Contributing

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details (if one exists).

## Acknowledgments

-   Google for Startups Accelerator Team
-   The participating startups of the AI First 2025 Berlin Cohort
-   Contributors and maintainers 