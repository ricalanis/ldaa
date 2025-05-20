from ldaa.agents.llm import get_llm
from ldaa.agents.config import load_config
from ldaa.utils.json import extract_json_from_llm_output
import asyncio
from ldaa.utils.logging import log_event, log_error
from ldaa.schemas import ComparisonAction
from ldaa.utils import get_random_prompt_variant

async def self_reflect_comparison(state, config, store):
    """
    Agentic node: Uses an LLM to self-reflect on the document comparison and recommend an action.
    Updates the state in-place and returns it, as required by LangGraph node conventions.
    Inputs (from state):
        - comparison_result: Dict with comparative summary, confidence, reasoning, verbose_report, etc.
    Outputs (to state):
        - comparison_action: Dict with {action, reboot, confidence, reasoning}
        - meta_log: Reflection meta information (success, errors, etc)
    """
    log_event("REFLECT_COMPARISON", "Starting self-reflection on comparison.")
    comparison = state.comparison_result
    llm = get_llm()
    config_obj = load_config()
    threshold = config_obj.confidence_threshold
    prompt_templates = [
        """
You are a legal document analysis assistant. Review the following document comparison and recommend an action. Return a JSON object with: - 'action': one of 'accept', 'retry', 'mark_review', or 'reboot' (if confidence > {threshold}, force accept; if confidence < 0.2, consider reboot) - 'confidence': the confidence score from 0 to 1 that represents consistency, completeness, and confidence from the comparison - 'reasoning': a short explanation for your decision\n\nComparison Result:\n{comparison}
""",
        """
As a comparison reflection expert, review the analysis below and provide a JSON object with: - 'action': 'accept', 'retry', 'mark_review', or 'reboot' (force accept if confidence > {threshold}; consider reboot if confidence < 0.2) - 'confidence': 0-1 score - 'reasoning': brief explanation.\n\nComparison Result:\n{comparison}
""",
        """
Reflect on the following document comparison and recommend an action. Output a JSON object: - 'action': 'accept', 'retry', 'mark_review', or 'reboot' (force accept if confidence > {threshold}; consider reboot if confidence < 0.2) - 'confidence': 0-1 - 'reasoning': explanation.\n\nComparison Result:\n{comparison}
""",
        """
You are tasked with reviewing a document comparison. Return a JSON object: - 'action': 'accept', 'retry', 'mark_review', or 'reboot' (force accept if confidence > {threshold}; consider reboot if confidence < 0.2) - 'confidence': 0-1 - 'reasoning': explanation.\n\nComparison Result:\n{comparison}
""",
        """
Act as a comparison review specialist. For the analysis below, provide a JSON object: - 'action': 'accept', 'retry', 'mark_review', or 'reboot' (force accept if confidence > {threshold}; consider reboot if confidence < 0.2) - 'confidence': 0-1 - 'reasoning': explanation.\n\nComparison Result:\n{comparison}
"""
    ]
    prompt = get_random_prompt_variant(prompt_templates, {"threshold": threshold, "comparison": comparison})
    try:
        response = await llm.ainvoke(prompt)
        reflection = extract_json_from_llm_output(response.content)
        reflection["success"] = True
        log_event("REFLECT_COMPARISON", "Self-reflection on comparison successful.")
        reflection = ComparisonAction(**reflection)
    except Exception as e:
        log_error(str(e), context="self_reflect_comparison")
        reflection = {
            "action": "mark_review",
            "confidence": getattr(comparison, "confidence", 0.0) if hasattr(comparison, "confidence") else 0.0,
            "reasoning": f"LLM reflection failed: {str(e)}",
            "success": False,
        }
    meta_log = {"success": reflection.success if hasattr(reflection, "success") else reflection["success"], "reasoning": getattr(reflection, "reasoning", "") if hasattr(reflection, "reasoning") else reflection.get("reasoning", "")}
    state.comparison_action = reflection
    state.meta['reflect_comparison'] = meta_log
    return state 