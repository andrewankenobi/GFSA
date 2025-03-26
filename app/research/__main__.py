#!/usr/bin/env python3
"""
Entry point for the research module. This allows running the module as:
python -m app.research [args]
"""

import asyncio
import sys
from app.research.run_pipeline import run_pipeline

if __name__ == "__main__":
    # Check if input file was provided
    input_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Run the pipeline
    asyncio.run(run_pipeline(input_file)) 