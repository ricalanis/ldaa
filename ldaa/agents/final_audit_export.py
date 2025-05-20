import os
import json
from pathlib import Path
from ldaa.utils.logging import log_event, log_error

def build_markdown_report(state):
    md = []
    md.append("# Legal Document Analysis Report\n")
    md.append("## Input Files")
    md.append(f"- Document 1: {state.doc1_path if hasattr(state, 'doc1_path') else 'N/A'}")
    md.append(f"- Document 2: {state.doc2_path if hasattr(state, 'doc2_path') else 'N/A'}")
    md.append("\n---\n")
    md.append("## Segmentation and Analysis\n")
    for doc_label in ["doc1", "doc2"]:
        md.append(f"### {doc_label.upper()} Segments and Analysis")
        segments = getattr(state, f"{doc_label}_segments", [])
        analysis = getattr(state, f"{doc_label}_analysis", [])
        actions = getattr(state, f"{doc_label}_segment_actions", [])
        for i, seg in enumerate(segments):
            md.append(f"#### Segment {i+1}: {getattr(seg, 'title', '')}")
            md.append(f"Text: {getattr(seg, 'text', '')}")
            if i < len(analysis):
                a = analysis[i]
                md.append(f"- Segment: {getattr(a, 'segment', '')}")
                md.append(f"- Summary: {getattr(a, 'summary', '')}")
                md.append(f"- Category: {getattr(a, 'category', '')}")
                md.append(f"- Pros: {getattr(a, 'pros', [])}")
                md.append(f"- Cons: {getattr(a, 'cons', [])}")
                md.append(f"- Confidence: {getattr(a, 'confidence', '')}")
                md.append(f"- Reasoning: {getattr(a, 'reasoning', '')}")
            if i < len(actions):
                act = actions[i]
                md.append(f"- Action: {getattr(act, 'action', '')}")
                md.append(f"- Reflection Reasoning: {getattr(act, 'reasoning', '')}")
            md.append("")
    md.append("\n---\n")
    md.append("## Comparison Result\n")
    comparison = getattr(state, 'comparison_result', {})
    md.append(f"Comparative Summary: {getattr(comparison, 'comparative_summary', '') if hasattr(comparison, 'comparative_summary') else comparison.get('comparative_summary', '') if isinstance(comparison, dict) else ''}")
    md.append(f"Confidence: {getattr(comparison, 'confidence', '') if hasattr(comparison, 'confidence') else comparison.get('confidence', '') if isinstance(comparison, dict) else ''}")
    md.append(f"Reasoning: {getattr(comparison, 'reasoning', '') if hasattr(comparison, 'reasoning') else comparison.get('reasoning', '') if isinstance(comparison, dict) else ''}")
    md.append(f"Meta: {getattr(comparison, 'meta', '') if hasattr(comparison, 'meta') else comparison.get('meta', '') if isinstance(comparison, dict) else ''}")
    md.append("")
    action = getattr(state, 'comparison_action', {})
    md.append(f"## Final Decision: {getattr(action, 'action', '') if hasattr(action, 'action') else action.get('action', '') if isinstance(action, dict) else ''}")
    md.append(f"Reasoning: {getattr(action, 'reasoning', '') if hasattr(action, 'reasoning') else action.get('reasoning', '') if isinstance(action, dict) else ''}")
    md.append("")
    md.append("## Meta-Logs\n")
    for key, value in state.meta.items():
        md.append(f"### {key}")
        md.append(str(value))
        md.append("")
    return "\n".join(md)

def final_audit_export(state, config, store):
    """
    Utility node: Outputs a structured report (JSON and Markdown) with all inputs, intermediate results, outputs, and meta-logs.
    Updates the state in-place and returns it, as required by LangGraph node conventions.
    """
    log_event("FINAL_AUDIT", "Starting final audit export.")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_json = output_dir / "final_result.json"
    output_md = output_dir / "report.md"
    try:
        # Write JSON
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(state.dict(), f, indent=2, ensure_ascii=False)
        # Write Markdown
        md = build_markdown_report(state)
        with open(output_md, "w", encoding="utf-8") as f:
            f.write(md)
        # Write verbose_comparison as Markdown if present
        verbose_md_path = None
        comparison = getattr(state, 'comparison_result', None)
        verbose_comparison = None
        if comparison is not None:
            # Handle both pydantic object and dict
            if hasattr(comparison, 'verbose_comparison'):
                verbose_comparison = getattr(comparison, 'verbose_comparison', None)
            elif isinstance(comparison, dict):
                verbose_comparison = comparison.get('verbose_comparison', None)
            if verbose_comparison:
                verbose_md_path = output_dir / "verbose_comparison.md"
                with open(verbose_md_path, "w", encoding="utf-8") as f:
                    f.write(verbose_comparison)
        meta_log = {"success": True, "output_json": str(output_json), "output_md": str(output_md)}
        if verbose_md_path:
            meta_log["verbose_comparison_md"] = str(verbose_md_path)
        log_event("FINAL_AUDIT", "Final audit export successful.")
    except Exception as e:
        log_error(str(e), context="final_audit_export")
        raise
    state.output_path = str(output_json)
    state.meta['final_audit'] = meta_log
    return state 