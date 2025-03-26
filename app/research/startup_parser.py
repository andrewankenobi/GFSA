import csv
from typing import List, Dict, Any

def parse_startups_file(file_path: str) -> List[Dict[str, Any]]:
    """Parse a tab-separated startups file into a list of startup dictionaries.
    
    Args:
        file_path: Path to the tab-separated startups file
        
    Returns:
        List of startup dictionaries with keys: name, industry, country, website
    """
    startups = []
    
    try:
        with open(file_path, 'r') as f:
            # Skip the header row
            next(f)
            
            # Parse TSV
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                if len(row) >= 4:
                    startup = {
                        "name": row[0].strip(),
                        "country": row[1].strip(),
                        "industry": row[2].strip(),
                        "website": row[3].strip()
                    }
                    startups.append(startup)
                    
        print(f"Successfully parsed {len(startups)} startups from {file_path}")
        return startups
        
    except Exception as e:
        print(f"Error parsing startups file: {str(e)}")
        return []

if __name__ == "__main__":
    # Test the parser
    startups = parse_startups_file("startups.txt")
    for startup in startups:
        print(f"{startup['name']} - {startup['industry']} - {startup['website']}") 