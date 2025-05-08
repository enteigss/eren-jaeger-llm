import os
import json
import re

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
    current_character = None
    current_text = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Handle title
        if line.startswith("Title:"):
            transcript["episode_info"]["title"] = line[6:].strip()
            continue

        # Handle scene descriptions
        if line.startswith("[Scene:"):
            # If we have a current scene, save it
            if current_scene:
                # Add any pending dialogue
                if current_character and current_text:
                    current_dialogue.append({
                        "type": "dialogue",
                        "character": current_character,
                        "line": " ".join(current_text)
                    })
                current_scene["dialogue"] = current_dialogue
                transcript["scenes"].append(current_scene)
            
            # Start a new scene
            scene_desc = line[7:-1].strip()  # Remove [Scene: and ]
            current_scene = {
                "description": scene_desc,
                "dialogue": []
            }
            current_dialogue = []
            current_character = None
            current_text = []
            continue

        # Handle action descriptions
        if line.startswith("[Action:"):
            # Add any pending dialogue
            if current_character and current_text:
                current_dialogue.append({
                    "type": "dialogue",
                    "character": current_character,
                    "line": " ".join(current_text)
                })
                current_character = None
                current_text = []
            
            if current_scene:
                action_desc = line[8:-1].strip()  # Remove [Action: and ]
                current_dialogue.append({
                    "type": "action",
                    "description": action_desc
                })
            continue

        # Handle dialogue
        if ':' in line:
            # Add any pending dialogue
            if current_character and current_text:
                current_dialogue.append({
                    "type": "dialogue",
                    "character": current_character,
                    "line": " ".join(current_text)
                })
            
            character, text = line.split(':', 1)
            character = character.strip()
            text = text.strip()
            
            # Clean up character names
            if character.startswith('('):
                character = character.strip('()')
            
            # Skip lines that are not actual dialogue
            if any(skip in line for skip in ["For till then", "Now, as thou seest"]):
                continue
            
            if current_scene:
                current_character = character
                current_text = [text] if text else []
        else:
            # This is a continuation of the previous dialogue
            if current_character and line:
                current_text.append(line)

    # Don't forget to add the last scene
    if current_scene:
        # Add any pending dialogue
        if current_character and current_text:
            current_dialogue.append({
                "type": "dialogue",
                "character": current_character,
                "line": " ".join(current_text)
            })
        current_scene["dialogue"] = current_dialogue
        transcript["scenes"].append(current_scene)

    return transcript

def main():
    transcript_dir = "episode-transcripts/transcript-txts"
    output_dir = "episode-transcripts"
    
    # Process all txt files
    for filename in os.listdir(transcript_dir):
        if filename.endswith('.txt'):
            print(f"Converting {filename}...")
            file_path = os.path.join(transcript_dir, filename)
            
            # Parse the transcript
            transcript = parse_transcript(file_path)
            
            # Create the JSON filename
            json_filename = clean_title(os.path.splitext(filename)[0]) + '.json'
            json_path = os.path.join(output_dir, json_filename)
            
            # Save the JSON file
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(transcript, f, indent=2, ensure_ascii=False)
            
            print(f"Created {json_filename}")

if __name__ == "__main__":
    main() 