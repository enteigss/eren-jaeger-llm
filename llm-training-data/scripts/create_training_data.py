import os
import json
from pathlib import Path

def convert_to_jsonl(prompts_dir, completions_dir, output_file):
    """
    Convert prompts and completions to JSONL format.
    
    Args:
        prompts_dir (str): Path to prompts directory
        completions_dir (str): Path to completions directory
        output_file (str): Path to output JSONL file
    """
    prompts_dir = Path(prompts_dir)
    completions_dir = Path(completions_dir)
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Walk through all episode directories
        for episode_dir in prompts_dir.glob('episode_*'):
            episode_num = episode_dir.name
            completion_episode_dir = completions_dir / episode_num
            
            # Skip if no matching completion directory
            if not completion_episode_dir.exists():
                print(f"Warning: No completions found for {episode_num}")
                continue
            
            # Process each scene
            for scene_dir in episode_dir.glob('scene_*'):
                scene_num = scene_dir.name
                completion_scene_dir = completion_episode_dir / scene_num
                
                # Skip if no matching completion scene directory
                if not completion_scene_dir.exists():
                    print(f"Warning: No completions found for {episode_num}/{scene_num}")
                    continue
                
                # Process each line
                for prompt_file in scene_dir.glob('line_*.txt'):
                    line_num = prompt_file.name
                    completion_file = completion_scene_dir / line_num
                    
                    # Skip if no matching completion file
                    if not completion_file.exists():
                        print(f"Warning: No completion found for {prompt_file}")
                        continue
                    
                    # Read prompt and completion
                    try:
                        with open(prompt_file, 'r', encoding='utf-8') as f:
                            prompt = f.read().strip()
                        
                        with open(completion_file, 'r', encoding='utf-8') as f:
                            completion = f.read().strip()
                        
                        # Create JSON object
                        json_obj = {
                            "prompt": prompt,
                            "completion": completion
                        }
                        
                        # Write to JSONL file
                        outfile.write(json.dumps(json_obj) + '\n')
                        
                    except Exception as e:
                        print(f"Error processing {prompt_file}: {str(e)}")

def main():
    # Define paths
    base_dir = Path("llm-training-data")
    prompts_dir = base_dir / "prompts"
    completions_dir = base_dir / "completions"
    output_file = base_dir / "training_data.jsonl"
    
    # Convert to JSONL
    convert_to_jsonl(prompts_dir, completions_dir, output_file)
    print(f"Conversion complete. Output written to {output_file}")

if __name__ == "__main__":
    main()