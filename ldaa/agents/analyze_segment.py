from ldaa.agents.llm import get_llm
from ldaa.agents.config import load_config
import asyncio
from ldaa.utils.logging import log_event, log_error
from ldaa.utils.json import extract_json_from_llm_output
from ldaa.schemas import SegmentAnalysis
from ldaa.utils import get_random_prompt_variant

async def analyze_one_segment(segment, doc_label="doc"):
    llm = get_llm()
    config = load_config()
    taxonomy = ', '.join(config.taxonomy)
    prompt_templates = [
        """
You are a legal document analysis assistant. Analyze the following segment. Return a JSON object with: - 'segment_id': the unique id of the segment (provided below) - 'segment': the text of the paragraph or section being analyzed - 'summary': a concise summary of the segment - 'category': a topic or category tag. Use one of the following taxonomy categories: {taxonomy} - 'pros': a list of positive aspects or strengths (at least 2, max 5) - 'cons': a list of negative aspects or weaknesses (at least 2, max 5) - 'confidence': a score from 0 to 1 for your confidence in your analysis - 'reasoning': a short explanation of your reasoning.\n\nSegment ID: {segment_id}\nTitle: {title}\nText: {text}
""",
        """
As a legal segment analyst, your job is to review the segment below and provide a JSON object with: - 'segment_id': unique id - 'segment': text being analyzed - 'summary': concise summary - 'category': topic/category (choose from: {taxonomy}) - 'pros': 2-5 strengths - 'cons': 2-5 weaknesses - 'confidence': confidence score (0-1) - 'reasoning': brief explanation.\n\nSegment ID: {segment_id}\nTitle: {title}\nText: {text}
""",
        """
Analyze the following legal document segment. Output a JSON object with: - 'segment_id': unique id - 'segment': text - 'summary': concise summary - 'category': topic/category (from: {taxonomy}) - 'pros': 2-5 strengths - 'cons': 2-5 weaknesses - 'confidence': 0-1 score - 'reasoning': short explanation.\n\nSegment ID: {segment_id}\nTitle: {title}\nText: {text}
""",
        """
You are tasked with analyzing a legal segment. Return a JSON object with: - 'segment_id': unique id - 'segment': text - 'summary': summary - 'category': topic/category (from: {taxonomy}) - 'pros': 2-5 strengths - 'cons': 2-5 weaknesses - 'confidence': 0-1 - 'reasoning': explanation.\n\nSegment ID: {segment_id}\nTitle: {title}\nText: {text}
""",
        """
Act as a legal segment reviewer. For the segment below, provide a JSON object: - 'segment_id': unique id - 'segment': text - 'summary': summary - 'category': topic/category (from: {taxonomy}) - 'pros': 2-5 strengths - 'cons': 2-5 weaknesses - 'confidence': 0-1 - 'reasoning': explanation.\n\nSegment ID: {segment_id}\nTitle: {title}\nText: {text}
"""
    ]
    prompt = get_random_prompt_variant(prompt_templates, {"taxonomy": taxonomy, "segment_id": segment.id, "title": getattr(segment, 'title', ''), "text": segment.text})
    log_event("ANALYZE", f"Analyzing segment {doc_label} with title: {getattr(segment, 'title', 'No Title')}")
    try:
        response = await llm.ainvoke(prompt)
        analysis = extract_json_from_llm_output(response.content)
        analysis["segment"] = segment.text
        analysis["segment_id"] = segment.id
        analysis["segment_type"] = getattr(segment, "segment_type", None)
        log_event("ANALYZE", "Segment analysis successful.")
    except Exception as e:
        log_error(str(e), context="analyze_segment")
        analysis = {
            "segment_id": segment.id,
            "segment": segment.text,
            "summary": "",
            "category": "",
            "pros": [],
            "cons": [],
            "confidence": 0.0,
            "reasoning": f"LLM analysis failed: {str(e)}",
        }
    return analysis

async def analyze_segment(state, config, store):
    """
    Agentic node: Uses an LLM to analyze each segment of both documents.
    Updates the state in-place and returns it, as required by LangGraph node conventions.
    """
    doc1_segments = state.doc1_segments
    doc2_segments = state.doc2_segments
    doc1_analysis, doc2_analysis = [], []
    meta_log = {"doc1": [], "doc2": []}
    log_event("ANALYZE", "Starting segment analysis.")
    # Analyze doc1 segments
    for i, seg in enumerate(doc1_segments):
        analysis = await analyze_one_segment(seg, doc_label=f"doc1_seg_{i}")
        analysis = SegmentAnalysis(**analysis)
        doc1_analysis.append(analysis)
        meta_log["doc1"].append({"segment": i, "success": analysis.success, "reasoning": analysis.reasoning})
    # Analyze doc2 segments
    for i, seg in enumerate(doc2_segments):
        analysis = await analyze_one_segment(seg, doc_label=f"doc2_seg_{i}")
        analysis = SegmentAnalysis(**analysis)
        doc2_analysis.append(analysis)
        meta_log["doc2"].append({"segment": i, "success": analysis.success, "reasoning": analysis.reasoning})
    state.doc1_analysis = doc1_analysis
    state.doc2_analysis = doc2_analysis
    state.meta['analysis'] = meta_log
    log_event("ANALYZE", "Segment analysis completed.")
    return state 