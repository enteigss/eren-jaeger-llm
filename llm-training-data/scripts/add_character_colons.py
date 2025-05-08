import os
import re

def is_character_line(line):
    """Check if a line represents a character speaking."""
    # Skip empty lines
    if not line.strip():
        return False
    
    # Skip scene and action descriptions
    if line.startswith(('[Scene:', '[Action:')):
        return False
    
    # Skip lines that already have colons
    if ':' in line:
        return False
    
    # Skip lines that are clearly not character names
    if line.startswith(('Do not ask for permission', 'For till then', 'Now, as thou seest', 'Title:', 'Character List:', 'Japanese script', 'English translation', 'Organized by')):
        return False
    
    # Skip lines that are too long to be character names
    if len(line.strip()) > 30:
        return False
    
    # Skip lines that end with punctuation (likely dialogue)
    if line.strip().endswith(('.', '!', '?', '...')):
        return False
    
    # Skip lines that are clearly part of a sentence
    if line.strip().startswith(('a', 'an', 'the', 'and', 'but', 'or', 'if', 'when', 'while', 'because')):
        return False
    
    # Skip lines that contain common dialogue words
    if any(word in line.lower() for word in ['said', 'asked', 'replied', 'answered', 'shouted', 'whispered', 'cried']):
        return False
    
    # Skip lines that are clearly dialogue
    if any(word in line.lower() for word in ['what', 'why', 'how', 'when', 'where', 'who']):
        return False
    
    # Skip lines that contain multiple exclamation marks or question marks
    if line.count('!') > 1 or line.count('?') > 1:
        return False
    
    # Skip lines that contain ellipsis
    if '...' in line:
        return False
    
    # Skip lines that contain multiple words that are all capitalized (likely dialogue)
    words = line.strip().split()
    if len(words) > 1 and all(word.isupper() for word in words):
        return False
    
    # Skip lines that contain multiple words (likely dialogue)
    if len(words) > 1:
        return False
    
    # Skip lines that contain common dialogue patterns
    if any(pattern in line.lower() for pattern in ['!', '?', '...', 'uh', 'um', 'ah', 'oh', 'hey', 'wow', 'ouch']):
        return False
    
    return True

def process_file(file_path):
    """Process a transcript file to add colons after character names."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        line = line.rstrip()  # Remove trailing whitespace but keep leading
        if is_character_line(line):
            # Add colon after character name
            new_lines.append(line + ':')
        else:
            new_lines.append(line)
    
    # Write back to the same file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

def main():
    transcript_dir = "episode-transcripts/transcript-txts"
    
    # Process all txt files
    for filename in os.listdir(transcript_dir):
        if filename.endswith('.txt'):
            print(f"Processing {filename}...")
            file_path = os.path.join(transcript_dir, filename)
            process_file(file_path)
            print(f"Completed {filename}")

if __name__ == "__main__":
    main() 