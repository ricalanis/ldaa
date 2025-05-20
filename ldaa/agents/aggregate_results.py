from ldaa.utils.logging import log_event, log_error
from ldaa.schemas import SegmentAnalysis

def aggregate_results(state, config, store):
    """
    Aggregates all segment analyses and their actions for each document.
    Updates the state in-place and returns it, as required by LangGraph node conventions.
    Inputs (from state):
        - doc1_analysis: List of analysis dicts for doc1 segments
        - doc2_analysis: List of analysis dicts for doc2 segments
        - doc1_segment_actions: List of action dicts for doc1 segments
        - doc2_segment_actions: List of action dicts for doc2 segments
    Outputs (to state):
        - doc1_accepted_segments: List of accepted analysis dicts for doc1
        - doc2_accepted_segments: List of accepted analysis dicts for doc2
        - meta_log_aggregate: Aggregation meta information (counts, etc)
    """
    log_event("AGGREGATE", "Starting aggregation of results.")
    try:
        doc1_analysis = state.doc1_analysis
        doc2_analysis = state.doc2_analysis
        doc1_actions = state.doc1_segment_actions
        doc2_actions = state.doc2_segment_actions
        print("[DEBUG] doc1_analysis:", doc1_analysis)
        print("[DEBUG] doc1_actions:", doc1_actions)
        print("[DEBUG] doc2_analysis:", doc2_analysis)
        print("[DEBUG] doc2_actions:", doc2_actions)
        doc1_accepted, doc2_accepted = [], []
        doc1_counts = {"accept": 0, "retry": 0, "mark_review": 0}
        doc2_counts = {"accept": 0, "retry": 0, "mark_review": 0}
        # Aggregate doc1
        for i, (analysis, action) in enumerate(zip(doc1_analysis, doc1_actions)):
            print(f"[DEBUG] doc1 Index {i}: action={getattr(action, 'action', None)}, analysis={analysis}")
            act = action.action
            doc1_counts[act] = doc1_counts[act] + 1 if act in doc1_counts else 1
            if act == "accept":
                print(f"[DEBUG] Accepting doc1 analysis at index {i}: {analysis}")
                doc1_accepted.append(analysis)
        # Aggregate doc2
        for i, (analysis, action) in enumerate(zip(doc2_analysis, doc2_actions)):
            print(f"[DEBUG] doc2 Index {i}: action={getattr(action, 'action', None)}, analysis={analysis}")
            act = action.action
            doc2_counts[act] = doc2_counts[act] + 1 if act in doc2_counts else 1
            if act == "accept":
                print(f"[DEBUG] Accepting doc2 analysis at index {i}: {analysis}")
                doc2_accepted.append(analysis)
        meta_log = {
            "doc1": doc1_counts,
            "doc2": doc2_counts,
        }
        state.doc1_accepted_segments = doc1_accepted
        state.doc2_accepted_segments = doc2_accepted
        state.meta['aggregate'] = meta_log
        log_event("AGGREGATE", "Aggregation successful.")
        return state
    except Exception as e:
        log_error(str(e), context="aggregate_results")
        raise 