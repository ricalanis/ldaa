from ldaa.agents.llm import get_llm
import asyncio
from ldaa.utils.logging import log_event, log_error
from ldaa.utils.json import extract_json_from_llm_output
from ldaa.schemas import DocumentSegment
from ldaa.utils import get_random_prompt_variant

async def segment_with_llm(text, doc_label="doc"):
    llm = get_llm()
    prompt_templates = [
        """
You are a legal document analysis assistant. Segment the following document into logical sections or paragraphs. For each segment, return a JSON object with: - 'title': a short title or heading for the segment (or empty if not available) - 'text': the full text of the segment - 'segment_type': the type of segment (choose one of: 'paragraph', 'article', 'section') based on document layout, coherence, and analytical granularity Return ONLY a JSON list of segments. Do not include any explanatory text, markdown, or code block formatting. - 'reasoning': a short explanation of your reasoning.\n\nExample output: [ {{ "title": "TITLE I: GENERAL PROVISIONS - Chapter 1: Definitions and Scope", "text": "...", "segment_type": "article", "reasoning": "..." }}, ... ]\n\nDocument ({doc_label}):\n{text}
""",
        """
As a legal document segmentation expert, your task is to divide the following document into logical sections or paragraphs. For each, provide a JSON object with: - 'title': a short heading (or empty) - 'text': the segment's full text - 'segment_type': one of 'paragraph', 'article', or 'section' - 'reasoning': a brief explanation for the segmentation. Output ONLY a JSON list of segments, no extra text or markdown.\n\nDocument ({doc_label}):\n{text}
""",
        """
Segment the document below into logical units. For each segment, output a JSON object with: - 'title': heading or empty - 'text': full segment text - 'segment_type': 'paragraph', 'article', or 'section' - 'reasoning': short explanation. Return a JSON list of segments only, no markdown or extra commentary.\n\nDocument ({doc_label}):\n{text}
""",
        """
You are tasked with segmenting the following legal document. Each segment must be represented as a JSON object with: - 'title': heading or empty - 'text': segment text - 'segment_type': 'paragraph', 'article', or 'section' - 'reasoning': brief explanation. Output a JSON list of segments, no markdown or extra text.\n\nDocument ({doc_label}):\n{text}
""",
        """
Act as a legal text segmenter. Divide the document below into logical sections or paragraphs. For each, return a JSON object: - 'title': heading or empty - 'text': full text - 'segment_type': 'paragraph', 'article', or 'section' - 'reasoning': short explanation. Output only a JSON list of segments, no markdown or commentary.\n\nDocument ({doc_label}):\n{text}
"""
    ]
    prompt = get_random_prompt_variant(prompt_templates, {"doc_label": doc_label, "text": text})
    try:
        response = await llm.ainvoke(prompt)
        segments = extract_json_from_llm_output(response.content)
        meta = {
            "num_segments": len(segments),
            "success": True,
            "reasoning": [seg.get("reasoning") or "" for seg in segments],
        }
        log_event("SEGMENTATION", "Segmentation successful.")
    except Exception as e:
        segments = []
        meta = {
            "num_segments": 0,
            "success": False,
            "reasoning": [],
        }
        log_error(str(e), context="decide_segmentation")
        raise
    return segments, meta

def enrich_segments(segments, document_id):
    return [
        DocumentSegment(
            id=f"{document_id}_seg_{i}",
            text=seg["text"],
            document_id=document_id,
            segment_type=seg.get("segment_type", "section"),
            position=i,
            reasoning=seg.get("reasoning")
        )
        for i, seg in enumerate(segments)
    ]

async def decide_segmentation(state, config, store):
    """
    Agentic node: Uses an LLM to segment each document into logical sections/paragraphs.
    Updates the state in-place and returns it, as required by LangGraph node conventions.
    """
    log_event("SEGMENTATION", "Starting segmentation.")
    doc1_text = state.doc1_text
    doc2_text = state.doc2_text
    print("[DEBUG] Segmentation input doc1_text:", repr(doc1_text[:500]) if doc1_text else "None")
    print("[DEBUG] Segmentation input doc2_text:", repr(doc2_text[:500]) if doc2_text else "None")
    doc1_segments_raw, meta1 = await segment_with_llm(doc1_text, doc_label="doc1") if doc1_text else ([], {"success": False, "reasoning": "No text provided"})
    doc2_segments_raw, meta2 = await segment_with_llm(doc2_text, doc_label="doc2") if doc2_text else ([], {"success": False, "reasoning": "No text provided"})
    # Enrich with required fields
    doc1_segments = enrich_segments(doc1_segments_raw, "doc1")
    doc2_segments = enrich_segments(doc2_segments_raw, "doc2")
    print("[DEBUG] Segmentation output doc1_segments:", repr(doc1_segments))
    print("[DEBUG] Segmentation output doc2_segments:", repr(doc2_segments))
    meta_log = {
        "doc1": meta1,
        "doc2": meta2,
    }
    state.doc1_segments = doc1_segments
    state.doc2_segments = doc2_segments
    state.meta['segmentation'] = meta_log
    log_event("SEGMENTATION", "Segmentation successful.")
    return state 