#!/usr/bin/env python3
"""
Simple entry point for running the startup research pipeline.
"""

import asyncio
import sys
from app.research.run_pipeline import run_pipeline

if __name__ == "__main__":
    # Check if input file was provided
    input_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Run the pipeline
    asyncio.run(run_pipeline(input_file)) 