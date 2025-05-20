import random
from typing import List, Dict, Any

def get_random_prompt_variant(prompt_templates: List[str], params: Dict[str, Any]) -> str:
    """
    Selects a random prompt template from the provided list and formats it with the given parameters.
    Args:
        prompt_templates: List of prompt templates (as f-strings or format strings).
        params: Dictionary of parameters to fill into the prompt template.
    Returns:
        A formatted prompt string with the parameters applied.
    """
    if not prompt_templates:
        raise ValueError("No prompt templates provided.")
    template = random.choice(prompt_templates)
    return template.format(**params) 