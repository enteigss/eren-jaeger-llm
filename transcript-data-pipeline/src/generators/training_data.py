from typing import List
from src.converter.transcript import Transcript
import json
import os
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))

class TrainingDataGenerator:
    def __init__(self, config: dict):
        self.config = config

    def process_episode(self, transcript: Transcript):
        """Process a single episode into training data."""
    
        # Extract episode number
        episode_num = self.extract_episode_number(transcript["title"])
        if not episode_num:
            print(f"Could not extract episode number from {transcript['title']}")
            return
    
        # Process each scene
        for scene_num, scene in enumerate(transcript["scenes"], 1):
            # Find Eren's lines in this scene
            eren_lines = []
            scene_info = self.get_scene_context_llm(scene, episode_num)
        
            # Go through dialogue to find Eren's lines
            for i, entry in enumerate(scene["events"]):
                if entry["type"] == "dialogue" and entry["character"] == "Eren":
                    # Check if this is a continuation of previous Eren dialogue
                    if eren_lines and i == eren_lines[-1][0] + 1 and scene["dialogue"][i-1]["character"] == "Eren":
                        continue
                    eren_lines.append((i, entry))
        
            # Generate prompt files for each of Eren's unique dialogue segments
            data = []
            for line_num, (i, line) in enumerate(eren_lines, 1):
                prompt = self.generate_prompt_file_v2(
                    episode_num,
                    scene_num,
                    line_num,
                    scene["description"],
                    scene["dialogue"][:i],  # Only include dialogue up to this line not including it
                    line,
                    scene_info
                )
                # add prompt and completion to data, hard to do because of the structure of the completion
    
    def generate_prompts(self, transcript: Transcript) -> List[dict]:
        """Generates prompt training data in txt format for each episode and puts it in training-txts directory."""
        # Generate prompt-completion pairs
    def extract_episode_number(self, filename):
        """Extract episode number from filename."""
        match = re.search(r'E\.(\d+)', filename)
        return match.group(1) if match else None

    def get_scene_context_llm(self, scene, episode_num):
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

    def combine_dialogue(self, dialogue):
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

    def generate_prompt_file_v2(self, episode_num, scene_num, line_num, scene_desc, dialogue, current_line, scene_info):
        """Generate a prompt file"""
    
        # Combine consecutive dialogue from the same character
        combined_dialogue = self.combine_dialogue(dialogue)

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

    def save_as_txt(self, json_file):
            

        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        transcript_dir = os.path.join(project_root, "tests", "transcript-json")
        for filename in os.listdir(transcript_dir):
            if filename.endswith(".json"):
                print(f"Processing {filename}...")
                file_path = os.path.join(transcript_dir, filename)
                self.process_episode(file_path)
    
    def save_jsonl(self, data: List[dict], output_path: str):
        # Save as JSONL
        pass