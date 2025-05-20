import yaml
from pydantic import BaseModel, Field
from typing import List
from pathlib import Path

class Config(BaseModel):
    model: str
    confidence_threshold: float = Field(..., ge=0.0, le=1.0)
    taxonomy: List[str]
    output_format: str = "json"

def load_config(path: str = None) -> Config:
    config_path = Path(path) if path else Path(__file__).parent / "config.yaml"
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)
    return Config(**data) 