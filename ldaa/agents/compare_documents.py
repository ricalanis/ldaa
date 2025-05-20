from ldaa.agents.llm import get_llm
from ldaa.utils.logging import log_event, log_error
from ldaa.utils.json import extract_json_from_llm_output
from ldaa.schemas import DocumentComparison
from ldaa.agents.config import load_config
from ldaa.utils import get_random_prompt_variant

async def compare_documents(state, config, store):
    """
    Agentic node: Compares two sets of document segments using an LLM.
    Updates the state in-place and returns it, as required by LangGraph node conventions.
    Inputs (from state):
        - doc1_accepted_segments: List of accepted analysis dicts for doc1
        - doc2_accepted_segments: List of accepted analysis dicts for doc2
    Outputs (to state):
        - comparison_result: Dict with comparative summary, confidence, reasoning/meta-log
        - meta_log: Comparison meta information (success, errors, etc)
    """
    log_event("COMPARE", "Starting document comparison.")
    llm = get_llm()
    config = load_config()
    doc1_segments = state.doc1_accepted_segments
    doc2_segments = state.doc2_accepted_segments
    taxonomy = config.taxonomy
    prompt_templates = [
        # 1
        """
You are a legal document analysis assistant. Compare the following two sets of document segments. Consider the summaries, categories, pros, cons, and reasoning for each segment. At the end, output a JSON object with: - 'comparative_summary': a concise summary of the key differences, similarities, focus areas, and gaps between the two documents - 'similarities': A list of dictionaries, each with 'topic' (str, as per the taxonomy: {taxonomy}) and 'explanation' (str), describing commonalities. - 'differences': A list of dictionaries, each with 'topic' (str, as per the taxonomy: {taxonomy}) and 'explanation' (str), describing distinctions. - 'focus_areas': A dictionary with two keys identifying each document ('doc1', 'doc2') and mapping to a list of high-level topics (as per the taxonomy: {taxonomy}) that represent the main areas of focus for that document. - 'gaps': A list of strings, each describing an omission or missing element in either document that is present in the other, or important regulatory elements that are missing in both. Do NOT return a list of objects or dicts for this field. - 'confidence': a score from 0 to 1 for your confidence in your comparison - 'reasoning': a short explanation of your reasoning - 'verbose_report': a markdown-formatted, detailed report of your comparative analysis, including per-paragraph summaries, topic tags, pros and cons, a final synthesis highlighting similarities, differences, and gaps, reasoning logs, and a summary table of key contrasts between the two proposals.\n\nDocument 1 Segments:\n{doc1_segments}\n\nDocument 2 Segments:\n{doc2_segments}\n\nNow, output the required JSON object.
""",
        # 2
        """
As a legal document analysis assistant, compare the following two sets of document segments. Consider the summaries, categories, pros, cons, and reasoning for each segment. At the end, output a JSON object with: - 'comparative_summary': a concise summary of the key differences, similarities, focus areas, and gaps between the two documents - 'similarities': A list of dictionaries, each with 'topic' (str, as per the taxonomy: {taxonomy}) and 'explanation' (str), describing commonalities. - 'differences': A list of dictionaries, each with 'topic' (str, as per the taxonomy: {taxonomy}) and 'explanation' (str), describing distinctions. - 'focus_areas': A dictionary with two keys identifying each document ('doc1', 'doc2') and mapping to a list of high-level topics (as per the taxonomy: {taxonomy}) that represent the main areas of focus for that document. - 'gaps': A list of strings, each describing an omission or missing element in either document that is present in the other, or important regulatory elements that are missing in both. Do NOT return a list of objects or dicts for this field. - 'confidence': a score from 0 to 1 for your confidence in your comparison - 'reasoning': a short explanation of your reasoning - 'verbose_report': a markdown-formatted, detailed report of your comparative analysis, including per-paragraph summaries, topic tags, pros and cons, a final synthesis highlighting similarities, differences, and gaps, reasoning logs, and a summary table of key contrasts between the two proposals.\n\nDocument 1 Segments:\n{doc1_segments}\n\nDocument 2 Segments:\n{doc2_segments}\n\nNow, output the required JSON object.
""",
        # 3
        """
You are a legal document analysis assistant. Compare the following two sets of document segments. Consider the summaries, categories, pros, cons, and reasoning for each segment. At the end, output a JSON object with: - 'comparative_summary': a concise summary of the key differences, similarities, focus areas, and gaps between the two documents - 'similarities': A list of dictionaries, each with 'topic' (str, as per the taxonomy: {taxonomy}) and 'explanation' (str), describing commonalities. - 'differences': A list of dictionaries, each with 'topic' (str, as per the taxonomy: {taxonomy}) and 'explanation' (str), describing distinctions. - 'focus_areas': A dictionary with two keys identifying each document ('doc1', 'doc2') and mapping to a list of high-level topics (as per the taxonomy: {taxonomy}) that represent the main areas of focus for that document. - 'gaps': A list of strings, each describing an omission or missing element in either document that is present in the other, or important regulatory elements that are missing in both. Do NOT return a list of objects or dicts for this field. - 'confidence': a score from 0 to 1 for your confidence in your comparison - 'reasoning': a short explanation of your reasoning - 'verbose_report': a markdown-formatted, detailed report of your comparative analysis, including per-paragraph summaries, topic tags, pros and cons, a final synthesis highlighting similarities, differences, and gaps, reasoning logs, and a summary table of key contrasts between the two proposals.\n\nDocument 1 Segments:\n{doc1_segments}\n\nDocument 2 Segments:\n{doc2_segments}\n\nNow, output the required JSON object.
""",
        # 4
        """
You are a legal document analysis assistant. Compare the following two sets of document segments. Consider the summaries, categories, pros, cons, and reasoning for each segment. At the end, output a JSON object with: - 'comparative_summary': a concise summary of the key differences, similarities, focus areas, and gaps between the two documents - 'similarities': A list of dictionaries, each with 'topic' (str, as per the taxonomy: {taxonomy}) and 'explanation' (str), describing commonalities. - 'differences': A list of dictionaries, each with 'topic' (str, as per the taxonomy: {taxonomy}) and 'explanation' (str), describing distinctions. - 'focus_areas': A dictionary with two keys identifying each document ('doc1', 'doc2') and mapping to a list of high-level topics (as per the taxonomy: {taxonomy}) that represent the main areas of focus for that document. - 'gaps': A list of strings, each describing an omission or missing element in either document that is present in the other, or important regulatory elements that are missing in both. Do NOT return a list of objects or dicts for this field. - 'confidence': a score from 0 to 1 for your confidence in your comparison - 'reasoning': a short explanation of your reasoning - 'verbose_report': a markdown-formatted, detailed report of your comparative analysis, including per-paragraph summaries, topic tags, pros and cons, a final synthesis highlighting similarities, differences, and gaps, reasoning logs, and a summary table of key contrasts between the two proposals.\n\nDocument 1 Segments:\n{doc1_segments}\n\nDocument 2 Segments:\n{doc2_segments}\n\nNow, output the required JSON object.
""",
        # 5
        """
You are a legal document analysis assistant. Compare the following two sets of document segments. Consider the summaries, categories, pros, cons, and reasoning for each segment. At the end, output a JSON object with: - 'comparative_summary': a concise summary of the key differences, similarities, focus areas, and gaps between the two documents - 'similarities': A list of dictionaries, each with 'topic' (str, as per the taxonomy: {taxonomy}) and 'explanation' (str), describing commonalities. - 'differences': A list of dictionaries, each with 'topic' (str, as per the taxonomy: {taxonomy}) and 'explanation' (str), describing distinctions. - 'focus_areas': A dictionary with two keys identifying each document ('doc1', 'doc2') and mapping to a list of high-level topics (as per the taxonomy: {taxonomy}) that represent the main areas of focus for that document. - 'gaps': A list of strings, each describing an omission or missing element in either document that is present in the other, or important regulatory elements that are missing in both. Do NOT return a list of objects or dicts for this field. - 'confidence': a score from 0 to 1 for your confidence in your comparison - 'reasoning': a short explanation of your reasoning - 'verbose_report': a markdown-formatted, detailed report of your comparative analysis, including per-paragraph summaries, topic tags, pros and cons, a final synthesis highlighting similarities, differences, and gaps, reasoning logs, and a summary table of key contrasts between the two proposals.\n\nDocument 1 Segments:\n{doc1_segments}\n\nDocument 2 Segments:\n{doc2_segments}\n\nNow, output the required JSON object.
"""
    ]
    prompt = get_random_prompt_variant(prompt_templates, {"taxonomy": taxonomy, "doc1_segments": doc1_segments, "doc2_segments": doc2_segments})
    try:
        print("[DEBUG] Prompt sent to LLM:\n", prompt)
        response = await llm.ainvoke(prompt)
        content = getattr(response, 'content', None)
        print("[DEBUG] Raw LLM response content:\n", repr(content))
        if not content or not isinstance(content, str):
            raise ValueError(f"LLM returned empty or non-string content: {repr(content)}")
        comparison = extract_json_from_llm_output(content)
        comparison["success"] = True
        required_fields = {
            "meta": getattr(state, "meta", getattr(comparison, "reasoning", "") if hasattr(comparison, "reasoning") else ""),
        }
        meta_val = comparison.get("meta", {})
        if not isinstance(meta_val, dict):
            comparison["meta"] = {}
        else:
            comparison.setdefault("meta", {})
        for k, v in required_fields.items():
            comparison.setdefault(k, v)
        meta = {"success": True, "reasoning": comparison.get("reasoning", "")}
        log_event("COMPARE", "Document comparison successful.")
        if "verbose_report" in comparison:
            comparison["verbose_comparison"] = comparison.pop("verbose_report")
        try:
            comparison = DocumentComparison(**comparison)
        except Exception as e:
            comparison = DocumentComparison(
                similarities=[],
                differences=[],
                focus_areas={},
                gaps=[],
                meta={},
                verbose_comparison="",
                comparative_summary="",
                confidence=0.0,
                reasoning=f"LLM comparison failed: {str(e)}",
                success=False,
            )
            meta = {"success": False, "reasoning": f"LLM comparison failed: {str(e)}"}
    except Exception as e:
        log_error(str(e), context="compare_documents")
        print("[ERROR] Exception during LLM comparison:", str(e))
        comparison = DocumentComparison(
            similarities=[],
            differences=[],
            focus_areas={},
            gaps=[],
            meta={},
            verbose_comparison="",
            comparative_summary="",
            confidence=0.0,
            reasoning=f"LLM comparison failed: {str(e)}",
            success=False,
        )
        meta = {"success": False, "reasoning": f"LLM comparison failed: {str(e)}"}
    state.comparison_result = comparison
    state.meta['compare'] = meta
    return state 