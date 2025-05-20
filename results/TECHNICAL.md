# Technical Brief: Agentic AI Comparator for Legal Proposals

## Overview
This system implements an agentic AI workflow for analyzing and comparing two legislative proposals (PDFs) for AI regulation in Mexico. The solution is designed to:
- Segment documents into logical units (paragraphs, articles, or sections)
- Summarize, categorize, and critically analyze each segment (pros/cons)
- Generate a comparative summary and detailed report
- Self-evaluate, retry, and flag low-confidence outputs for human review
- Provide transparent, auditable outputs with meta-logs and confidence scores

## Architecture & Technologies

### Core Technologies
- **LangChain**: Provides LLM integration, tool schemas, and prompt management.
- **LangGraph**: Orchestrates the agentic workflow as a directed graph of nodes (steps), supporting conditional routing, retries, and state management.
- **OpenAI API**: Used for LLM-based analysis, segmentation, and comparison.
- **FAISS**: Vector store for segment storage and retrieval (enables semantic search and future extensibility).
- **Pydantic**: Data validation and modeling for all state and output schemas.
- **Streamlit**: Web interface for interactive document upload and analysis.
- **Python Asyncio**: Enables concurrent LLM calls and responsive UI.

### Project Structure
- `ldaa/agents/`: All agent node implementations (segmentation, analysis, comparison, etc.) and the main graph definition.
- `ldaa/schemas.py`: Pydantic models for state, segment, analysis, and comparison outputs.
- `ldaa/utils/`: Utilities for prompt variants, JSON extraction, logging, and session management.
- `scripts/cli.py`: CLI entry point for batch analysis.
- `scripts/app.py`: Streamlit web app for interactive use.
- `output/`: Stores generated JSON/Markdown reports.
- `results/`: Documentation and technical briefs.

## Agentic Graph Workflow

The core workflow is defined in `ldaa/agents/graph.py` using LangGraph's `StateGraph`:

1. **Ingest Documents**: Loads and preprocesses the two PDF files.
2. **Decide Segmentation**: Uses an LLM to segment each document into logical units (paragraphs, articles, or sections), with reasoning for each split.
3. **Analyze Segment**: For each segment, an LLM summarizes, categorizes, and lists pros/cons, returning a confidence score and reasoning.
4. **Self-Reflect Segment**: The agent reviews its own outputs, scoring confidence and deciding whether to retry, escalate for human review, or proceed.
5. **Aggregate Results**: Collects and organizes all per-segment analyses.
6. **Compare Documents**: An LLM compares the two sets of analyzed segments, generating a comparative summary, similarities, differences, focus areas, gaps, and a verbose markdown report.
7. **Self-Reflect Comparison**: The agent reviews the comparison output, with options to retry, backtrack, or escalate.
8. **Final Audit Export**: Prepares the final output, including all meta-logs and confidence scores.
9. **Human-in-the-Loop Nodes**: If confidence is low or errors occur, the workflow can pause for human review and intervention.
10. **Vector Store Integration**: Segments and analyses can be stored in FAISS for semantic search and future retrieval.

```
[Ingest Documents]
         |
         v
[Decide Segmentation]
         |
         v
[Analyze Segment]
         |
         v
[Self-Reflect Segment]
   |      |      |
   |   [Retry]   |
   |      v      |
   |<--[Human Review]
   |
   v
[Aggregate Results]
         |
         v
[Compare Documents]
         |
         v
[Self-Reflect Comparison]
   |      |      |
   |   [Retry]   |
   |      v      |
   |<--[Human Review]
   |
   v
[Save to Vector Store]
         |
         v
[Final Audit Export]
         |
         v
        END
```

Conditional routers in the graph enable dynamic control flow, supporting retries, escalation, and human-in-the-loop as required by the agentic paradigm.

## State & Data Modeling
- **LegalAnalysisState**: Central state object (Pydantic model) tracks all document paths, raw texts, segments, analyses, actions, comparison results, meta-logs, and output paths.
- **DocumentSegment**: Represents a single segment with type, position, and reasoning for segmentation.
- **SegmentAnalysis**: Stores summary, category, pros, cons, confidence, and reasoning for each segment.
- **DocumentComparison**: Captures similarities, differences, focus areas, gaps, and a verbose comparative summary.
- **Meta-Logs**: Every step logs reasoning, confidence, and retry counts for transparency and auditability.

## Prompt Engineering & LLM Usage
- Each node that interacts with an LLM uses carefully crafted, versioned prompt templates (with few-shot examples and explicit output schemas).
- Prompts instruct the LLM to return structured JSON, which is parsed and validated.
- Multiple prompt variants are randomly selected to improve robustness and reduce prompt overfitting.
- Confidence scores and reasoning are always requested from the LLM, enabling self-evaluation and agentic control.

## Error Handling, Retries, and Human-in-the-Loop
- If an LLM output is missing required fields, has low confidence, or fails validation, the agent retries the operation.
- If quality persist in a lower than threshold level, it is flagged for human review.
- Human-in-the-loop nodes pause execution and allow for manual intervention or approval, with the use of Langsmith Agent Inbox.
- All errors and retries are logged in the meta-log for each step.

## Interfaces
- **CLI**: `scripts/cli.py` allows batch processing of two PDFs, saving results to JSON.
- **Web App**: `scripts/app.py` provides a Streamlit UI for uploading PDFs, running the analysis, and downloading results.
- **Notebook**: (Optional) Jupyter notebook for interactive exploration and debugging.
- **Server**: Langgraph client is leveraged to interface with the Model.

## Meeting the Challenge Requirements
- **Summarization**: Each segment is summarized by the LLM, with concise, accurate outputs.
- **Categorization**: Segments are tagged with topics from a configurable taxonomy.
- **Pros/Cons**: At least one pro and one con are extracted per segment, with reasoning.
- **Comparison**: The agent generates a detailed comparative summary, including similarities, differences, focus areas, and gaps.
- **Agentic Features**: The workflow is fully agentic—able to segment, self-evaluate, retry, escalate, and log all decisions.
- **Transparency**: All outputs include meta-logs, confidence scores, and reasoning for auditability.

## Extensibility & Modularity
- New segmentation, analysis, or comparison strategies can be added as new nodes or prompt variants.
- The taxonomy for categorization is configurable.
- The vector store enables future semantic search, retrieval, or RAG workflows.
- The modular node design allows for easy integration of new LLMs, tools, or human-in-the-loop interfaces.

## Notable Design Decisions
- **LangGraph for Orchestration**: Enables explicit, auditable agentic workflows with conditional routing and state management.
- **Pydantic for Validation**: Ensures all LLM outputs are validated and structured, reducing silent failures.
- **Prompt Randomization**: Reduces prompt overfitting and increases robustness.
- **Meta-Logging**: Every step logs its reasoning, confidence, and retry count for full transparency.
- **Separation of Concerns**: Each node is responsible for a single step, making the system easy to test, debug, and extend.
- **One directional vector-store**: A node for vector storage was created, but was not used due lack of use case at this moment.

## Tradeoffs
- **LLM Cost/Latency**: Multiple retries and self-evaluation increase LLM usage and latency, but improve reliability and auditability.
- **Strict Output Validation**: May result in more retries or human review, but ensures high-quality, structured outputs.

---

This implementation provides a robust, extensible, and transparent agentic system for legal document comparison, fully aligned with the expectations and evaluation criteria of the Seals AI challenge. 
