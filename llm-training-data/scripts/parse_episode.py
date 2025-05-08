import json
import re

def parse_transcript(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Initialize the transcript structure
    transcript = {
        "title": "",
        "episode_info": {},
        "scenes": []
    }

    # Split content into sections
    sections = content.split("[Scene:")
    
    # Process header section
    header = sections[0].strip().split('\n')
    for line in header:
        if line.startswith("Attack on Titan"):
            transcript["title"] = line.strip()
        elif line.startswith("Title:"):
            transcript["episode_info"]["title"] = line[6:].strip()

    # Process each scene
    for section in sections[1:]:
        if not section.strip():
            continue

        # Split scene into description and content
        scene_parts = section.split(']', 1)
        if len(scene_parts) != 2:
            continue

        scene_desc = scene_parts[0].strip()
        scene_content = scene_parts[1].strip()

        current_scene = {
            "description": scene_desc,
            "dialogue": []
        }

        # Process scene content
        lines = scene_content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue

            # Handle action blocks
            if line.startswith("[Action:"):
                action_desc = line[8:-1]  # Remove [Action: and ]
                current_scene["dialogue"].append({
                    "type": "action",
                    "description": action_desc.strip()
                })
                i += 1
                continue

            # Handle dialogue
            dialogue_match = re.match(r'^([A-Za-z0-9 .\'-]+):\s*(.*)', line)
            if dialogue_match:
                character, text = dialogue_match.groups()
                # Collect multi-line dialogue
                full_text = text.strip()
                i += 1
                while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('[') and ':' not in lines[i]:
                    full_text += ' ' + lines[i].strip()
                    i += 1
                
                if full_text:  # Only add if there's actual dialogue
                    current_scene["dialogue"].append({
                        "type": "dialogue",
                        "character": character.strip(),
                        "line": full_text.strip()
                    })
                continue

            i += 1

        if current_scene["dialogue"]:  # Only add scenes that have content
            transcript["scenes"].append(current_scene)

    return transcript

def save_json(transcript, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(transcript, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    input_file = "episode-transcripts/Attack on Titan S.1 E.01 (ENG sub).txt"
    output_file = "episode-transcripts/Attack on Titan S.1 E.01.json"
    
    transcript = parse_transcript(input_file)
    save_json(transcript, output_file)
    print(f"Transcript has been converted to JSON and saved to {output_file}") 