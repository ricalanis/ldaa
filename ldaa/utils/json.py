import re
import json

def extract_json_from_llm_output(output: str):
    """
    Extracts JSON from LLM output, handling markdown code blocks and extra text.
    """
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", output)
    if match:
        output = match.group(1)
    output = output.strip()
    json_start = min([i for i in [output.find("["), output.find("{")] if i != -1], default=0)
    output = output[json_start:]
    return json.loads(output)

def to_serializable(obj):
    """Recursively convert objects to something JSON serializable, with robust fallback for unknown types."""
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_serializable(i) for i in obj]
    elif hasattr(obj, 'dict'):  # Pydantic models
        return to_serializable(obj.dict())
    elif hasattr(obj, '__dict__') and not isinstance(obj, type):
        # For custom classes, try to use __dict__ (may need to filter private keys)
        return {k: to_serializable(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
    try:
        # Try to convert to string as a last resort
        return str(obj)
    except Exception:
        return f"<non-serializable: {type(obj).__name__}>" 