import asyncio
import json
import sys
from app.research.startup_research_pipeline import StartupResearchPipeline
from app.research.startup_parser import parse_startups_file

async def run_pipeline(input_file=None):
    """Run the startup research pipeline.
    
    Args:
        input_file: Optional path to JSON or TXT file with startup data.
                   If not provided, uses default startups.txt.
    """
    startups = []
    
    # Define default file if none provided
    if not input_file:
        input_file = "app/research/startups.txt"
    
    # Load startups based on file type
    if input_file.endswith(".json"):
        # Load from JSON
        try:
            with open(input_file, 'r') as f:
                startups = json.load(f)
            print(f"Loaded {len(startups)} startups from JSON file: {input_file}")
        except Exception as e:
            print(f"Error loading JSON file: {str(e)}")
            return
    elif input_file.endswith(".txt"):
        # Parse tab-separated values
        startups = parse_startups_file(input_file)
        if not startups:
            print("No startups loaded. Exiting.")
            return
    else:
        print(f"Unsupported file format: {input_file}")
        print("Please provide a .json or .txt file")
        return
        
    # Run the pipeline
    print("Starting research pipeline...")
    async with StartupResearchPipeline() as pipeline:
        reference_file = await pipeline.process_startups(startups)
        print(f"Process complete! Reference file created: {reference_file}")

if __name__ == "__main__":
    # Check if input file was provided
    input_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Run the pipeline
    asyncio.run(run_pipeline(input_file)) 