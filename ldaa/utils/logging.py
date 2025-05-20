"""
Meta-logging utilities for workflow events, decisions, and errors.
"""
import logging

logger = logging.getLogger("ldaa")

# Configure logger (can be expanded for file/console handlers)
logging.basicConfig(level=logging.INFO)

def log_event(event_type, message, **kwargs):
    """Log a workflow event with optional metadata."""
    logger.info(f"[{event_type}] {message} | {kwargs}")

def log_decision(node, decision, confidence=None, meta=None):
    """Log a decision made at a workflow node."""
    logger.info(f"[DECISION] Node: {node}, Decision: {decision}, Confidence: {confidence}, Meta: {meta}")

def log_error(error, context=None):
    """Log an error with optional context."""
    logger.error(f"[ERROR] {error} | Context: {context}") 