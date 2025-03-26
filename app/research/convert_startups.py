#!/usr/bin/env python3
import json
from app.research.startup_parser import parse_startups_file

def convert_startups_to_json(input_file="app/research/startups.txt", output_file="app/research/startups.json"):
    """Convert startups.txt to a JSON file.
    
    Args:
        input_file: Path to the startups.txt file
        output_file: Path to save the JSON output
    """
    # Parse the startups file
    startups = parse_startups_file(input_file)
    
    if not startups:
        print(f"No startups found in {input_file}")
        return
    
    # Save as JSON
    with open(output_file, 'w') as f:
        json.dump(startups, f, indent=2)
    
    print(f"Converted {len(startups)} startups to {output_file}")
    
if __name__ == "__main__":
    import sys
    
    # Get input and output files from command line arguments
    input_file = sys.argv[1] if len(sys.argv) > 1 else "app/research/startups.txt"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "app/research/startups.json"
    
    convert_startups_to_json(input_file, output_file) 