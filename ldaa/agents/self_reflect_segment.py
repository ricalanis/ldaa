from ldaa.agents.llm import get_llm
from ldaa.agents.config import load_config
import asyncio
from ldaa.utils.logging import log_event, log_error
from ldaa.utils.json import extract_json_from_llm_output
from ldaa.schemas import SegmentAction
from ldaa.utils import get_random_prompt_variant

async def reflect_on_segment(analysis, segment_index, doc_label="doc"):
    llm = get_llm()
    config = load_config()
    threshold = config.confidence_threshold
    prompt_templates = [
        """
You are a legal document analysis assistant. Review the following segment analysis and recommend an action. Return a JSON object with: - 'action': one of 'accept', 'retry', or 'mark_review' (if confidence > {threshold}, force accept) - 'confidence': the confidence score from 0 to 1 that represents consistency, completeness, and confidence from the segmentation - 'reasoning': a short explanation for your decision\n\nSegment index: {segment_index}\nDocument: {doc_label}\nAnalysis:\n{analysis}
""",
        """
As a segment reflection expert, review the analysis below and provide a JSON object with: - 'action': 'accept', 'retry', or 'mark_review' (force accept if confidence > {threshold}) - 'confidence': 0-1 score - 'reasoning': brief explanation.\n\nSegment index: {segment_index}\nDocument: {doc_label}\nAnalysis:\n{analysis}
""",
        """
Reflect on the following segment analysis and recommend an action. Output a JSON object: - 'action': 'accept', 'retry', or 'mark_review' (force accept if confidence > {threshold}) - 'confidence': 0-1 - 'reasoning': explanation.\n\nSegment index: {segment_index}\nDocument: {doc_label}\nAnalysis:\n{analysis}
""",
        """
You are tasked with reviewing a segment analysis. Return a JSON object: - 'action': 'accept', 'retry', or 'mark_review' (force accept if confidence > {threshold}) - 'confidence': 0-1 - 'reasoning': explanation.\n\nSegment index: {segment_index}\nDocument: {doc_label}\nAnalysis:\n{analysis}
""",
        """
Act as a segment review specialist. For the analysis below, provide a JSON object: - 'action': 'accept', 'retry', or 'mark_review' (force accept if confidence > {threshold}) - 'confidence': 0-1 - 'reasoning': explanation.\n\nSegment index: {segment_index}\nDocument: {doc_label}\nAnalysis:\n{analysis}
"""
    ]
    prompt = get_random_prompt_variant(prompt_templates, {"threshold": threshold, "segment_index": segment_index, "doc_label": doc_label, "analysis": analysis})
    try:
        response = await llm.ainvoke(prompt)
        reflection = extract_json_from_llm_output(response.content)
        reflection["success"] = True
        reflection["segment_index"] = segment_index
    except Exception as e:
        reflection = {
            "action": "mark_review",
            "confidence": analysis.confidence if hasattr(analysis, "confidence") else analysis.get("confidence", 0.0),
            "reasoning": f"LLM reflection failed: {str(e)}",
            "success": False,
            "segment_index": segment_index,
        }
    return reflection

async def self_reflect_segment(state, config, store):
    """
    Agentic node: Uses an LLM to self-reflect on each segment analysis and recommend an action.
    Updates the state in-place and returns it, as required by LangGraph node conventions.
    """
    log_event("REFLECT_SEGMENT", "Starting self-reflection on segments.")
    doc1_analysis = state.doc1_analysis
    doc2_analysis = state.doc2_analysis
    doc1_segment_actions, doc2_segment_actions = [], []
    meta_log = {"doc1": [], "doc2": []}
    # Reflect on doc1 segments
    for i, analysis in enumerate(doc1_analysis):
        reflection = await reflect_on_segment(analysis, i, doc_label="doc1")
        reflection = SegmentAction(**reflection)
        doc1_segment_actions.append(reflection)
        meta_log["doc1"].append({"segment": i, "success": reflection.success, "reasoning": reflection.reasoning})
    # Reflect on doc2 segments
    for i, analysis in enumerate(doc2_analysis):
        reflection = await reflect_on_segment(analysis, i, doc_label="doc2")
        reflection = SegmentAction(**reflection)
        doc2_segment_actions.append(reflection)
        meta_log["doc2"].append({"segment": i, "success": reflection.success, "reasoning": reflection.reasoning})
    state.doc1_segment_actions = doc1_segment_actions
    state.doc2_segment_actions = doc2_segment_actions
    state.meta['reflect_segment'] = meta_log
    log_event("REFLECT_SEGMENT", "Self-reflection on segments successful.")
    return state 