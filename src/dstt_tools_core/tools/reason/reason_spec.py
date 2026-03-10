import yaml
import os
from pathlib import Path
from typing import Dict, Any

class ReasonSpecRegistry:
    """
    Registry for storing declarative reasoning specifications.
    It isolates deterministic LLM payload shapes away from code allowing strict architectural bounds.
    """
    def __init__(self):
        self._specs: Dict[str, Dict[str, Any]] = {}
        
    def load_from_file(self, filepath: str) -> None:
        """
        Parses a single YAML configuration file directly into the local registry.
        Derives the `spec_id` exclusively from the file's basename seamlessly.
        """
        path = Path(filepath)
        if not path.is_file():
            raise ValueError(f"ReasonSpec YAML file not found: {filepath}")
            
        with open(path, "r") as f:
            try:
                spec_data = yaml.safe_load(f) or {}
            except yaml.YAMLError as e:
                raise ValueError(f"Failed to parse ReasonSpec YAML '{filepath}': {e}")
                
        # Inherit spec identifier explicitly mapped against filesystem identity
        spec_id = path.stem 
        print("spec_id =", spec_id)
        print("spec_id type =", type(spec_id))
        self._specs[spec_id] = spec_data

    def load_from_directory(self, directory: str) -> None:
        """Recursively parses all .yaml and .yml files resolving nested spec dictionaries."""
        dir_path = Path(directory)
        if not dir_path.is_dir():
            raise ValueError(f"ReasonSpec directory not found: {directory}")
            
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith(".yaml") or file.endswith(".yml"):
                    self.load_from_file(os.path.join(root, file))

    def register(self, name: str, spec: Dict[str, Any]) -> None:
        """Register a ReasonSpec block mapping to its expected behavior."""
        self._specs[name] = spec

    def get(self, name: str) -> Dict[str, Any]:
        """Fetch the specific ReasonSpec schema. Explicit mapping failure enforces constraints."""
        if name not in self._specs:
            raise ValueError(f"ReasonSpec '{name}' not found.")
        return self._specs[name]

def build_prompt(spec_id: str, spec: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Abstracts prompt generation specifically dictated by the ReasonSpec configuration.
    Reasoning tools delegate their string logic to this parser.
    """
    template = spec.get("prompt_template")
    
    if not template:
        raise ValueError(f"ReasonSpec '{spec_id}' missing prompt_template")
        
    try:
        return template.format(**context)
    except KeyError as e:
        raise ValueError(f"ReasonSpec '{spec_id}' missing required context variable for prompt template formatting: {e}")
