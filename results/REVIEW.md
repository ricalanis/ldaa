# REVIEW.md

This document guides reviewers to the relevant files, code, and outputs for each evaluation criterion in the Seals AI Take-Home Challenge solution. Use this as a map to quickly locate evidence for each required element.

---

## 1. Architecture & Code Quality
- **README.md**: Project structure, design decisions, and workflow overview.
- **ldaa/agents/graph.py**: Main agentic workflow (LangGraph state graph, modular nodes).
- **ldaa/agents/**: Each node is a separate, well-documented module (e.g., `analyze_segment.py`, `compare_documents.py`).
- **pyproject.toml** & **requirements.txt**: Dependency management and project setup.

## 2. Prompt Engineering
- **ldaa/agents/analyze_segment.py**: Multiple prompt templates for segment analysis (see `prompt_templates`).
- **ldaa/agents/compare_documents.py**: Prompt templates for comparative analysis.
- **ldaa/agents/self_reflect_segment.py** & **self_reflect_comparison.py**: Prompts for self-reflection and agentic decision-making.
- **ldaa/utils/prompt_variants.py**: Utility for prompt randomization.
- **README.md**: High-level description of prompt engineering approach.

## 3. Understanding & Categorization
- **output/report.json** & **output/report.md**: Per-paragraph summaries and topic categorization.
- **ldaa/agents/analyze_segment.py**: Code for extracting summaries and categories.
- **results/OUTPUT.md**: Example output structure and explanation.

## 4. Critical Analysis (Pros/Cons Extraction)
- **output/report.json** & **output/report.md**: Each segment includes pros and cons.
- **ldaa/agents/analyze_segment.py**: LLM prompt and extraction logic for pros/cons.

## 5. Comparison (Comparative Summary)
- **output/report.json** & **output/report.md**: Contains the comparative summary and detailed comparison.
- **ldaa/agents/compare_documents.py**: Code and prompts for generating the comparative summary.
- **results/OUTPUT.md**: Explanation of comparison output.

## 6. Transparency (Meta-logs & Confidence Scores)
- **output/report.json** & **output/report.md**: Meta-logs and confidence scores included for each segment and the overall comparison.
- **ldaa/agents/analyze_segment.py**, **self_reflect_segment.py**, **compare_documents.py**, **self_reflect_comparison.py**: All log reasoning, confidence, and meta information.
- **ldaa/agents/final_audit_export.py**: Aggregates and exports all meta-logs.

## 7. Agentic System (Self-evaluation, Retries, Logging)
- **ldaa/agents/graph.py**: Conditional routing for retries, human-in-the-loop, and escalation.
- **ldaa/agents/self_reflect_segment.py** & **self_reflect_comparison.py**: Self-evaluation logic and action recommendations (accept, retry, mark_review, reboot).
- **ldaa/agents/human_in_the_loop.py**: Human review node for unresolved/flagged segments.
- **output/report.json** & **output/report.md**: Evidence of retries, self-evaluation, and escalation in meta-logs.

---

For a detailed walkthrough of the system's architecture and design, see **results/TECHNICAL.md**. 