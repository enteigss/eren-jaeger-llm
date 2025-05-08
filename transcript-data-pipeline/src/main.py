import yaml
from pathlib import Path
from src.converter import TranscriptParser
from src.transformers import TranscriptToJsonConverter
from src.generators import TrainingDataGenerator

def load_config():
    with open("config/pipeline_config.yaml") as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    
    # Initialize components
    converter = TranscriptToJsonConverter(config["processing"]["output_dir"])
    generator = TrainingDataGenerator(config["training_data"])
    
    # Process each transcript
    raw_dir = Path(config["input"]["raw_dir"])
    for transcript_file in raw_dir.glob(config["input"]["file_pattern"]):
        # Parse transcript
        transcript = parser.parse_file(transcript_file)
        
        # Convert to JSON
        json_path = converter.convert(transcript)
        
        # Generate training data
        training_data = generator.generate_prompts(transcript)
        generator.save_jsonl(training_data, config["training_data"]["output_dir"])