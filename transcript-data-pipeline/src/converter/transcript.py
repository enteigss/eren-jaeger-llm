# src/parsers/transcript.py
from dataclasses import dataclass
from typing import List, Optional, Union

@dataclass
class Dialogue:
    character: str
    line: str
    type: str = "dialogue"

@dataclass
class Action:
    description: str
    type: str = "action"

@dataclass
class Scene:
    description: str
    events: List[Union[Dialogue, Action]]

@dataclass
class Transcript:
    title: str
    episode_info: dict
    scenes: List[Scene]

class TranscriptParser:
    def __init__(self, config: dict):
        self.config = config
    
    def parse_file(self, file_path: str) -> Transcript:
        # Implementation of your current parse_transcript logic
        pass