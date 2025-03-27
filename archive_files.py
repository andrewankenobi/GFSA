import os
import shutil
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('archive.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def archive_old_files():
    # Define directories
    data_dir = Path('data')
    archive_dir = data_dir / 'archive'
    results_dir = data_dir / 'results'
    raw_dir = data_dir / 'raw'
    
    # Create archive directory if it doesn't exist
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # Archive results files
    results_files = sorted(results_dir.glob('analysis_*.json'))
    if len(results_files) > 1:  # Keep the most recent file
        for file in results_files[:-1]:
            try:
                shutil.move(str(file), str(archive_dir / file.name))
                logger.info(f"Archived results file: {file.name}")
            except Exception as e:
                logger.error(f"Error archiving {file.name}: {e}")
    
    # Archive raw files
    raw_files = sorted(raw_dir.glob('*_raw.json'))
    if len(raw_files) > 15:  # Keep the 15 most recent files (one per startup)
        for file in raw_files[:-15]:
            try:
                shutil.move(str(file), str(archive_dir / file.name))
                logger.info(f"Archived raw file: {file.name}")
            except Exception as e:
                logger.error(f"Error archiving {file.name}: {e}")

if __name__ == "__main__":
    archive_old_files() 