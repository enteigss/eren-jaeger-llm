import json
import os
from pathlib import Path
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_episode_number(filename):
    """Extract episode number from filename."""
    match = re.search(r'E\.(\d+)', filename)
    return match.group(1) if match else None

def extract_location_and_context(scene_desc):
    """Extract location and context from scene description."""
    # Clean up the description
    desc = scene_desc.strip()
    
    # Split into location and context
    parts = desc.split(".", 1)
    location = parts[0].strip()
    context = parts[1].strip() if len(parts) > 1 else location
    
    # Clean up location
    if location.lower().startswith("in "):
        location = location[3:]
    elif location.lower().startswith("at "):
        location = location[3:]
    elif location.lower().startswith("on "):
        location = location[3:]
    
    return location.capitalize(), context.capitalize()

def get_conversation_history(scene_dialogue, up_to_index):
    """Get conversation history up to a specific index."""
    conversation = []
    for i in range(up_to_index):
        if scene_dialogue[i]["type"] == "dialogue":
            conversation.append(f"{scene_dialogue[i]['character']}: {scene_dialogue[i]['line']}")
        elif scene_dialogue[i]["type"] == "action":
            conversation.append(f"[Action: {scene_dialogue[i]['description']}]")
    return "\n".join(conversation)

def get_other_characters(scene_dialogue, up_to_index):
    """Get list of other characters in the conversation."""
    characters = set()
    for i in range(up_to_index):
        if scene_dialogue[i]["type"] == "dialogue":
            char = scene_dialogue[i]["character"]
            if char != "Eren":
                characters.add(char)
    characters = sorted(list(characters))
    return characters

def get_scene_context(scene_dialogue, up_to_index):
    """Get context from actions and dialogue up to the current point."""
    context_parts = []
    for i in range(up_to_index):
        if scene_dialogue[i]["type"] == "action":
            context_parts.append(scene_dialogue[i]["description"])
    return " ".join(context_parts)

def get_scene_context_llm(scene, episode_num):
    """Get context from actions and dialogue up to the current point."""

    with open(f"episode-summaries/episode-{episode_num}.txt", "r") as f:
        episode_summary = f.read()

    current_convo = ""
    for line in scene["dialogue"]:
        if line["type"] == "dialogue":
            current_convo += f"{line['character']}: {line['line']}\n"
        if line["type"] == "action":
            current_convo += f"[Action: {line['description']}]\n"

    prompt = f"""Using the episode summary and transcript scene below, extract the following fields:

            - past_context: 1-2 sentence description of past context relevant to the scene.
            - current_context: 1-2 sentence description of immediate relevant context to the scene.
            - retrieved_memory (optional): If Eren is influenced by a memory, describe it; otherwise, write "N/A".
            - current_location: the location of the scene.
            - target_persona: The name of the person Eren is addressing his line to. If Eren is not addressing anyone, write "N/A".

            [Episode Summary]
            {episode_summary}

            [Scene Transcript]
            {current_convo}

            Output format (Make sure it is a valid json that can be properly processed by the json.loads function, do not put it in markdown code blocks):
            {{
            "past_context": "...",
            "current_context": "...",
            "retrieved_memory": "...",
            "current_location": "...",
            "target_persona": "..."
            }}"""
    
    print("prompt:", prompt)
    
    response = client.responses.create(
        model="gpt-4.1",
        input=prompt
    )

    response = response.output_text
    try: 
        response = response.strip()
        end_index = response.rfind('}') + 1
        response = response[:end_index]
        data = json.loads(response)
    except:
        print("Error parsing JSON response:", response)
        raise
    
    info = {"current_location": data["current_location"],
            "current_context": data["current_context"],
            "retrieved_memory": data["retrieved_memory"],
            "target_persona": data["target_persona"],
            }

    return info

def format_characters_string(characters):
    """Format the characters string for the prompt."""
    if not characters:
        return "The scene begins"
    elif len(characters) == 1:
        return f"{characters[0]} is present"
    else:
        return f"{', '.join(characters[:-1])} and {characters[-1]} are present"

def combine_dialogue(dialogue):
    """Combine consecutive dialogue entries from the same character."""
    combined = []
    current_character = None
    current_lines = []
    
    for entry in dialogue:
        if entry["type"] == "action":
            # If we have pending dialogue, add it
            if current_character and current_lines:
                combined.append({
                    "type": "dialogue",
                    "character": current_character,
                    "line": " ".join(current_lines)
                })
                current_lines = []
            combined.append(entry)
            continue
            
        if entry["type"] == "dialogue":
            if entry["character"] == current_character:
                # Same character, append the line
                current_lines.append(entry["line"])
            else:
                # Different character, add pending dialogue and start new
                if current_character and current_lines:
                    combined.append({
                        "type": "dialogue",
                        "character": current_character,
                        "line": " ".join(current_lines)
                    })
                current_character = entry["character"]
                current_lines = [entry["line"]]
    
    # Add any remaining dialogue
    if current_character and current_lines:
        combined.append({
            "type": "dialogue",
            "character": current_character,
            "line": " ".join(current_lines)
        })
    
    return combined

def generate_prompt_file_v2(episode_num, scene_num, line_num, scene_desc, dialogue, current_line, scene_info):
    """Generate a prompt file"""
    
    # Combine consecutive dialogue from the same character
    combined_dialogue = combine_dialogue(dialogue)

    current_conversation = []
    for entry in combined_dialogue:
        if entry["type"] == "dialogue":
            current_conversation.append(f"{entry['character']}: {entry['line']}")
        elif entry["type"] == "action":
            current_conversation.append(f"[Action: {entry['description']}]")
        # Stop when we reach Eren's current line
        if entry["type"] == "dialogue" and entry["character"] == "Eren" and current_line["line"] in entry["line"]:
            break

    
    # Create prompt content
    prompt_content = f"""Context for the task: 

    Here is the memory that is in Eren Jaeger's head: 
    N/A

    Past Context: 
    N/A

    Current Location: {scene_info["current_location"]}

    Current Context: 
    {scene_info["current_context"]}

    {', '.join(set(entry["character"] for entry in combined_dialogue if entry["type"] == "dialogue"))} are chatting. Here is their conversation so far: 
    {chr(10).join(current_conversation)}

    ---
    Task: Given the above, what should Eren Jaeger say next in the conversation? And did it end the conversation?

    Output format: Output a json of the following format: 
    {{
    "Eren Jaeger": "<Eren Jaeger's utterance>",
    "Did the conversation end with Eren Jaeger's utterance?": "<json Boolean>"
    }}"""

    # Create directories if they don't exist
    base_dir = "prompts"
    episode_dir = os.path.join(base_dir, f"episode_{episode_num}")
    scene_dir = os.path.join(episode_dir, f"scene_{scene_num:02d}")  # Zero-pad scene number
    os.makedirs(scene_dir, exist_ok=True)
    
    # Write prompt file
    prompt_file = os.path.join(scene_dir, f"line_{line_num:02d}.txt")  # Zero-pad line number
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(prompt_content)

def generate_prompt_file(episode_num, scene_num, line_num, scene_desc, dialogue, current_line):
    """Generate a prompt file for a single line."""
    # Extract location from scene description
    location = scene_desc.split('.')[0] if '.' in scene_desc else scene_desc
    
    # Combine consecutive dialogue from the same character
    combined_dialogue = combine_dialogue(dialogue)
    
    # Build conversation context
    current_conversation = []
    for entry in combined_dialogue:
        if entry["type"] == "dialogue":
            current_conversation.append(f"{entry['character']}: {entry['line']}")
        elif entry["type"] == "action":
            current_conversation.append(f"[Action: {entry['description']}]")
        # Stop when we reach Eren's current line
        if entry["type"] == "dialogue" and entry["character"] == "Eren" and current_line["line"] in entry["line"]:
            break
    
    # Create prompt content
    prompt_content = f"""Context for the task: 

Here is the memory that is in Eren Jaeger's head: 
N/A

Past Context: 
N/A

Current Location: {location}

Current Context: 
{scene_desc}

{', '.join(set(entry["character"] for entry in combined_dialogue if entry["type"] == "dialogue"))} are chatting. Here is their conversation so far: 
{chr(10).join(current_conversation)}

---
Task: Given the above, what should Eren Jaeger say next in the conversation? And did it end the conversation?

Output format: Output a json of the following format: 
{{
"Eren Jaeger's utterance": "{current_line["line"]}",
"Did the conversation end with Eren Jaeger's utterance?": "false"
}}"""

    # Create directories if they don't exist
    base_dir = "prompts"
    episode_dir = os.path.join(base_dir, f"episode_{episode_num}")
    scene_dir = os.path.join(episode_dir, f"scene_{scene_num:02d}")  # Zero-pad scene number
    os.makedirs(scene_dir, exist_ok=True)
    
    # Write prompt file
    prompt_file = os.path.join(scene_dir, f"line_{line_num:02d}.txt")  # Zero-pad line number
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(prompt_content)

def process_episode(json_file):
    """Process a single episode JSON file."""
    with open(json_file, 'r', encoding='utf-8') as f:
        episode = json.load(f)
    
    # Extract episode number
    episode_num = extract_episode_number(episode["title"])
    if not episode_num:
        print(f"Could not extract episode number from {episode['title']}")
        return
    
    skip_episode_nums = ['12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25']
    if episode_num in skip_episode_nums:
        return
    
    # Process each scene
    for scene_num, scene in enumerate(episode["scenes"], 1):
        # Find Eren's lines in this scene
        eren_lines = []
        current_line_start = 0
        # scene_info = get_scene_context_llm(scene, episode_num)
        
        # Go through dialogue to find Eren's lines
        for i, entry in enumerate(scene["dialogue"]):
            if entry["type"] == "dialogue" and entry["character"] == "Eren":
                # Check if this is a continuation of previous Eren dialogue
                if eren_lines and i == eren_lines[-1][0] + 1 and scene["dialogue"][i-1]["character"] == "Eren":
                    continue
                eren_lines.append((i, entry))
        
        # Generate prompt files for each of Eren's unique dialogue segments
        for line_num, (i, line) in enumerate(eren_lines, 1):
            # generate_prompt_file_v2(
            #     episode_num,
            #     scene_num,
            #     line_num,
            #     scene["description"],
            #     scene["dialogue"][:i],  # Only include dialogue up to this line not including it
            #     line,
            #    scene_info
            # )
            # generate completion file
            base_dir = "completions"
            episode_dir = os.path.join(base_dir, f"episode_{episode_num}")
            scene_dir = os.path.join(episode_dir, f"scene_{scene_num:02d}")  # Zero-pad scene number
            os.makedirs(scene_dir, exist_ok=True)
    
            # Write prompt file
            completion_file = os.path.join(scene_dir, f"line_{line_num:02d}.txt")  # Zero-pad line number
            with open(completion_file, 'w', encoding='utf-8') as f:
                f.write(line["line"])


def main():
    # Process all JSON files in the transcript-jsons directory
    transcript_dir = "episode-transcripts/transcript-jsons"
    for filename in os.listdir(transcript_dir):
        if filename.endswith('.json'):
            print(f"Processing {filename}...")
            file_path = os.path.join(transcript_dir, filename)
            process_episode(file_path)
            print(f"Completed {filename}")

if __name__ == "__main__":
    main() 