import json
import sys

def convert_json_to_text(json_file):
    """Convert JSON knowledge base to plain text format for Bedrock ingestion"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Process each category and its contents
    for category, contents in data.items():
        # Print category header
        print(f"\n### {category}\n")
        
        # Print each content item with proper spacing
        for content in contents:
            # Remove any markdown formatting
            clean_content = content.replace('**', '').replace('*', '')
            print(clean_content)
            print("\n---\n")  # Separator between entries

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convert_to_text.py input.json > output.txt")
        sys.exit(1)
    
    convert_json_to_text(sys.argv[1])
