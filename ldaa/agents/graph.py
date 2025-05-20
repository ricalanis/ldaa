from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from ldaa.agents.ingest_documents import ingest_documents
from ldaa.agents.decide_segmentation import decide_segmentation
from ldaa.agents.analyze_segment import analyze_segment
from ldaa.agents.self_reflect_segment import self_reflect_segment
from ldaa.agents.aggregate_results import aggregate_results
from ldaa.agents.compare_documents import compare_documents
from ldaa.agents.self_reflect_comparison import self_reflect_comparison
from ldaa.agents.final_audit_export import final_audit_export
from ldaa.agents.human_in_the_loop import human_in_the_loop
from ldaa.schemas import LegalAnalysisState
from ldaa.agents.vector_store import save_segments_to_faiss
from langgraph.checkpoint.memory import MemorySaver

# --- Conditional routers ---
def segment_reflection_router(state: LegalAnalysisState):
    """
    Route after self_reflect_segment:
    - If any segment action is 'retry', go back to analyze_segment
    - If any is 'mark_review', escalate (here: continue to aggregate_results)
    - Else, continue to aggregate_results
    """
    actions = (getattr(state, "doc1_segment_actions", []) + getattr(state, "doc2_segment_actions", []))
    if any(a.action == "retry" for a in actions):
        return "analyze_segment"
    elif any(a.action == "mark_review" for a in actions):
        return "human_in_the_loop_segment"
    else:
        return "aggregate_results"

def comparison_reflection_router(state: LegalAnalysisState):
    """
    Route after self_reflect_comparison:
    - If action is 'retry', go back to compare_documents
    - If action is 'reboot', go back to analyze_segment
    - If 'mark_review', escalate (here: continue to final_audit_export)
    - Else, continue to final_audit_export
    """
    actions = getattr(state, "comparison_actions", [])
    if any(a.action == "retry" for a in actions):
        return "retry_comparison"
    if any(a.action == "reboot" for a in actions):
        return "analyze_segment"
    elif any(a.action == "mark_review" for a in actions):
        return "human_in_the_loop_comparison"
    return "final_audit_export"

# --- Build the agentic graph ---
graph = StateGraph(LegalAnalysisState)

graph.add_node("ingest_documents", ingest_documents)
graph.add_node("decide_segmentation", decide_segmentation)
graph.add_node("analyze_segment", analyze_segment)
graph.add_node("self_reflect_segment", self_reflect_segment)
graph.add_node("aggregate_results", aggregate_results)
graph.add_node("compare_documents", compare_documents)
graph.add_node("self_reflect_comparison", self_reflect_comparison)
graph.add_node("final_audit_export", final_audit_export)
graph.add_node("human_in_the_loop_segment", human_in_the_loop)
graph.add_node("human_in_the_loop_comparison", human_in_the_loop)
graph.add_node("save_segments_to_faiss", save_segments_to_faiss)

# Edges for agentic flow
graph.add_edge("ingest_documents", "decide_segmentation")
graph.add_edge("decide_segmentation", "analyze_segment")
graph.add_edge("analyze_segment", "self_reflect_segment")
graph.add_conditional_edges("self_reflect_segment", segment_reflection_router)
graph.add_edge("aggregate_results", "compare_documents")
graph.add_edge("compare_documents", "self_reflect_comparison")
graph.add_conditional_edges("self_reflect_comparison", comparison_reflection_router)
graph.add_edge("human_in_the_loop_segment", "aggregate_results")
graph.add_edge("aggregate_results", "compare_documents")
graph.add_edge("compare_documents", "self_reflect_comparison")
graph.add_edge("human_in_the_loop_comparison", "save_segments_to_faiss")
graph.add_edge("save_segments_to_faiss", "final_audit_export")
graph.add_edge("final_audit_export", END)

graph.set_entry_point("ingest_documents")

# The compiled graph is ready for orchestration/testing
compiled_graph = graph.compile(checkpointer = MemorySaver())