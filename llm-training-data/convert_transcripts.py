import os
import json
import re

def parse_episode_number(filename):
    """Extract episode number from filename."""
    match = re.search(r'E\.(\d+)', filename)
    if not match:
        match = re.search(r'E(\d+)', filename)
    return int(match.group(1)) if match else None

def clean_title(filename):
    """Clean the episode title to match episode 1's format."""
    # Remove (ENG sub) and clean up the title
    title = filename.replace(" (ENG sub)", "")
    # Ensure consistent season number format
    title = re.sub(r'S\.(\d+)', r'S.\1', title)
    return title

def parse_transcript(file_path):
    """Parse a transcript file into JSON format."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Initialize the JSON structure
    filename = os.path.basename(file_path)
    title = clean_title(os.path.splitext(filename)[0])
    
    transcript = {
        "title": title,
        "episode_info": {
            "title": ""  # We'll fill this if we find it
        },
        "scenes": []
    }

    current_scene = None
    current_dialogue = []
    in_character_list = False
    in_credits = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Skip credits and notes
        if line.startswith(("Do not ask for permission", "For till then", "Now, as thou seest")):
            in_credits = True
            continue
        if in_credits and not line.startswith("["):
            continue
        in_credits = False

        # Handle title
        if line.startswith("Title:"):
            transcript["episode_info"]["title"] = line[6:].strip()
            continue

        # Handle character list
        if line == "Character List:":
            in_character_list = True
            continue
        if in_character_list and not line.startswith("["):
            continue
        in_character_list = False

        # Handle scene descriptions
        if line.startswith("[Scene:"):
            # If we have a current scene, save it
            if current_scene:
                current_scene["dialogue"] = current_dialogue
                transcript["scenes"].append(current_scene)
            
            # Start a new scene
            scene_desc = line[7:-1].strip()  # Remove [Scene: and ]
            current_scene = {
                "description": scene_desc,
                "dialogue": []
            }
            current_dialogue = []
            continue

        # Handle action descriptions
        if line.startswith("[Action:"):
            if current_scene:
                action_desc = line[8:-1].strip()  # Remove [Action: and ]
                current_dialogue.append({
                    "type": "action",
                    "description": action_desc
                })
            continue

        # Handle dialogue
        if ':' in line:
            character, text = line.split(':', 1)
            character = character.strip()
            text = text.strip()
            
            # Clean up character names
            if character.startswith('('):
                character = character.strip('()')
            
            if current_scene:
                current_dialogue.append({
                    "type": "dialogue",
                    "character": character,
                    "line": text
                })

    # Don't forget to add the last scene
    if current_scene:
        current_scene["dialogue"] = current_dialogue
        transcript["scenes"].append(current_scene)

    return transcript

def main():
    transcript_dir = "episode-transcripts"
    
    # Process all txt files
    for filename in os.listdir(transcript_dir):
        if filename.endswith('.txt'):
            print(f"Converting {filename}...")
            file_path = os.path.join(transcript_dir, filename)
            
            # Parse the transcript
            transcript = parse_transcript(file_path)
            
            # Create the JSON filename
            json_filename = clean_title(os.path.splitext(filename)[0]) + '.json'
            json_path = os.path.join(transcript_dir, json_filename)
            
            # Save the JSON file
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(transcript, f, indent=2, ensure_ascii=False)
            
            print(f"Created {json_filename}")

if __name__ == "__main__":
    main() 