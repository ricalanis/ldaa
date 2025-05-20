from typing import Any, Dict, Optional
from langgraph.types import interrupt
from langsmith import traceable

@traceable
def human_in_the_loop(state, config=None, store=None):
    """
    Human-in-the-loop review node. Pauses execution and waits for human input via the LangGraph Agent Inbox or similar UI.
    This node is fully traced in LangSmith for observability and auditability.
    """
    # Determine context for description
    context = getattr(state, 'current_review_context', "Please review the segment/comparison below.")
    request = {
        "action_request": {"action": "review", "args": state.dict()},
        "config": {
            "allow_ignore": True,
            "allow_respond": True,
            "allow_edit": True,
            "allow_accept": True,
        },
        "description": context,
    }
    response = interrupt([request])[0]
    # Update state based on human response
    if response["type"] == "accept":
        state.human_review = "accepted"
    elif response["type"] == "ignore":
        state.human_review = "ignored"
    elif response["type"] == "edit":
        # For edit, update state with provided args (could be a partial update)
        for k, v in response["args"]["args"].items():
            setattr(state, k, v)
        state.human_review = "edited"
    elif response["type"] == "response":
        state.human_review = response["args"]
    else:
        state.human_review = f"unknown: {response}"
    return state 