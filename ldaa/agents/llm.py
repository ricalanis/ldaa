from langchain.chat_models import init_chat_model
from ldaa.agents.config import load_config
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Note: Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY in your .env file for tracking

def get_llm():
    config = load_config()
    model = getattr(config, "model", None) or os.getenv("OPENAI_MODEL", "openai:gpt-4o")
    return init_chat_model(model)

# Utility for prompt construction (can be expanded for few-shot, etc.)
def build_prompt(task: str, segment_text: str, examples=None):
    prompt = f"Task: {task}\nText: {segment_text}\n"
    if examples:
        prompt += "Examples:\n"
        for ex in examples:
            prompt += f"Input: {ex['input']}\n"
            if 'output' in ex:
                prompt += f"Output: {ex['output']}\n"
            else:
                # For analysis examples
                if 'pros' in ex:
                    prompt += f"Pros: {'; '.join(ex['pros'])}\n"
                if 'cons' in ex:
                    prompt += f"Cons: {'; '.join(ex['cons'])}\n"
                if 'reasoning' in ex:
                    prompt += f"Reasoning: {ex['reasoning']}\n"
    return prompt 