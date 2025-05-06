import json
import os
from typing import List, Dict
import pandas as pd
from tqdm import tqdm

class ErenDataCollector:
    def __init__(self, raw_data_dir: str, processed_data_dir: str):
        self.raw_data_dir = raw_data_dir
        self.processed_data_dir = processed_data_dir
        self.character_traits = {
            "personality": [
                "determined", "passionate", "driven", "protective",
                "stubborn", "impulsive", "idealistic", "vengeful"
            ],
            "motivations": [
                "freedom", "revenge", "protecting friends",
                "destroying titans", "understanding the truth"
            ],
            "relationships": {
                "Mikasa": "protective sister-like figure",
                "Armin": "childhood friend and strategist",
                "Levi": "mentor and superior",
                "Historia": "ally and friend",
                "Zeke": "half-brother and enemy"
            }
        }

    def process_dialogue(self, dialogue_data: List[Dict]) -> pd.DataFrame:
        """Process raw dialogue data into training format."""
        processed_data = []
        
        for entry in tqdm(dialogue_data, desc="Processing dialogue"):
            context = entry.get("context", "")
            dialogue = entry.get("dialogue", "")
            emotion = entry.get("emotion", "")
            
            # Create training prompt
            prompt = f"""Context: {context}
Emotion: {emotion}
Character: Eren Jaeger
Dialogue:"""
            
            processed_data.append({
                "prompt": prompt,
                "completion": dialogue,
                "context": context,
                "emotion": emotion
            })
        
        return pd.DataFrame(processed_data)

    def process_decision_scenarios(self, scenarios: List[Dict]) -> pd.DataFrame:
        """Process decision-making scenarios into training format."""
        processed_scenarios = []
        
        for scenario in tqdm(scenarios, desc="Processing scenarios"):
            situation = scenario.get("situation", "")
            options = scenario.get("options", [])
            chosen_action = scenario.get("chosen_action", "")
            reasoning = scenario.get("reasoning", "")
            
            prompt = f"""Situation: {situation}
Options: {', '.join(options)}
Character: Eren Jaeger
Decision:"""
            
            processed_scenarios.append({
                "prompt": prompt,
                "completion": f"{chosen_action} | {reasoning}",
                "situation": situation,
                "options": options
            })
        
        return pd.DataFrame(processed_scenarios)

    def save_processed_data(self, df: pd.DataFrame, filename: str):
        """Save processed data to CSV file."""
        os.makedirs(self.processed_data_dir, exist_ok=True)
        output_path = os.path.join(self.processed_data_dir, filename)
        df.to_csv(output_path, index=False)
        print(f"Saved processed data to {output_path}")

    def load_raw_data(self, filename: str) -> List[Dict]:
        """Load raw data from JSON file."""
        input_path = os.path.join(self.raw_data_dir, filename)
        with open(input_path, 'r', encoding='utf-8') as f:
            return json.load(f)

if __name__ == "__main__":
    # Example usage
    collector = ErenDataCollector(
        raw_data_dir="data/raw",
        processed_data_dir="data/processed"
    )
    
    # Load and process dialogue data
    dialogue_data = collector.load_raw_data("eren_dialogue.json")
    processed_dialogue = collector.process_dialogue(dialogue_data)
    collector.save_processed_data(processed_dialogue, "processed_dialogue.csv")
    
    # Load and process decision scenarios
    scenarios = collector.load_raw_data("eren_decisions.json")
    processed_scenarios = collector.process_decision_scenarios(scenarios)
    collector.save_processed_data(processed_scenarios, "processed_scenarios.csv") 