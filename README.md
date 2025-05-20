# Seals AI Take-Home Challenge: AI Regulation Proposal Comparator

## Overview
This repository contains a solution to the Seals AI Take-Home Challenge: **Comparing AI Regulation Proposals in Mexico**. The goal is to build an AI-based agent that analyzes and compares two legislative proposals (PDFs) for AI regulation in Mexico, providing per-paragraph summaries, topic categorization, pros/cons, and a comparative report. The system is designed to be agentic, self-evaluating, and transparent in its reasoning.

---

## Features

- **PDF Ingestion & Segmentation:** Automatically extracts and segments legal documents by paragraph (or article/section if configured).
- **Per-Paragraph Analysis:**
  - Summarizes each paragraph.
  - Tags each section with a general topic/category (e.g., ethics, governance, innovation, human rights, compliance).
  - Extracts at least one "pro" and one "con" for each paragraph.
- **Comparative Summary:** Generates an overall comparative report highlighting differences, focus areas, and gaps between the two documents.
- **Agentic Workflow:**
  - Decides how to segment documents.
  - Evaluates its own outputs for confidence and consistency.
  - Retries or flags for human review if confidence is low.
  - Logs reasoning and confidence for each step.
- **Transparent, Auditable Output:**
  - Each output includes a meta-log of decisions, confidence scores, and reasoning.
  - Final report is structured and easy to audit.
- **Multiple Interfaces:** Run via CLI or a simple Streamlit web app.

---

## How It Works

1. **Document Ingestion:** Place the two PDF proposals in the `input/` directory, or upload them via the web interface.
2. **Segmentation:** The agent segments each document into paragraphs (or other units as configured).
3. **Per-Paragraph Processing:** For each segment, the agent:
   - Summarizes the content.
   - Assigns a topic/category.
   - Identifies at least one pro and one con.
   - Scores its confidence and logs its reasoning.
   - If confidence is low, retries with a refined prompt or flags for human review.
4. **Comparison:** After both documents are processed, the agent generates a comparative summary, highlighting key differences, overlaps, and gaps.
5. **Output:** Results are saved as structured JSON and Markdown, including all per-paragraph analyses, the comparative summary, and meta-logs.

---

## Setup & Usage

### 1. Clone the repository

```bash
git clone <repo-url>
cd <repo-folder>
```

### 2. Install dependencies

```bash
poetry install
# or
pip install -r requirements.txt
```

### 3. Prepare your documents

- Place the two PDF files in the `input/` directory as `ley1.pdf` and `ley2.pdf` (or specify paths via CLI).

### 4. Run the analysis

#### CLI

```bash
PYTHONPATH=. poetry run python scripts/cli.py input/ley1.pdf input/ley2.pdf
# or
PYTHONPATH=. python scripts/cli.py input/ley1.pdf input/ley2.pdf
```

#### Web Interface (Optional)

```bash
PYTHONPATH=. poetry run streamlit run scripts/app.py
# or
PYTHONPATH=. streamlit run scripts/app.py
```
- Upload two PDF files and click "Analyze Documents".

#### Jupyter Notebook

```bash
PYTHONPATH=. poetry run streamlit run scripts/app.py
# or
PYTHONPATH=. streamlit run scripts/app.py
```
- Upload two PDF files and click "Analyze Documents".

### 5. View the output

- Results are saved in the `output/` directory as JSON and/or Markdown files.
- For a detailed explanation of the output files and their structure, see [results/OUTPUT.md](results/OUTPUT.md).

---

## Example Output

Each segment is analyzed as follows:

```json
{
  "segment": "El suscrito, Dr. Ricardo Monreal Ávila, senador de la República...",
  "summary": "Senator Ricardo Monreal Ávila from the Morena Party submits a legislative proposal...",
  "category": "sectoral_regulation",
  "pros": ["Proactively addresses the regulation of emerging technology."],
  "cons": ["Lacks specific details on the content of the proposal."],
  "confidence": 0.85,
  "reasoning": "The segment provides a clear context of legislative activity concerning AI regulation, but lacks substantive detail on the initiative's content, affecting completeness.",
  "meta": {},
  "success": true
}
```
The final comparative summary provides a structured overview of differences, focus areas, and gaps. See [results/OUTPUT.md](results/OUTPUT.md) for more details on the output format. For a deeper understanding of the system's architecture and design choices, refer to [results/TECHNICAL.md](results/TECHNICAL.md). For evaluation criteria and scoring guidelines, see [results/REVIEW.md](results/REVIEW.md).

---

## Design Decisions

- **LangChain & LangGraph:** Used for modular, agentic workflow orchestration, tool calling, and state management. LangChain provides robust LLM integration and tool schemas; LangGraph enables agentic, self-evaluating workflows with conditional routing and retries.
- **Prompt Engineering:** Carefully crafted prompts (with few-shot examples) guide the LLM to produce consistent, structured outputs for summarization, categorization, and pros/cons extraction. Prompts are versioned and refined based on output quality.
- **Confidence & Consistency Handling:** Each LLM output is scored for confidence (using heuristics and/or LLM self-evaluation). Low-confidence outputs trigger retries with refined prompts or are flagged for human review. All decisions and confidence scores are logged.
- **Transparent Reasoning:** Every output includes a meta-log detailing the agent's reasoning, confidence, and any retries or prompt changes.
- **Extensibility:** The system is modular—new segmentation strategies, analysis skills, or output formats can be added easily.

---

## Dependencies

- Python 3.11+
- [LangChain](https://python.langchain.com/) (`>0.3.0`)
- [LangGraph](https://langchain-ai.github.io/langgraph/) (`>0.4.3`)
- [FAISS](https://github.com/facebookresearch/faiss) (for vector storage)
- [PyPDF2](https://pypi.org/project/PyPDF2/), [pdfplumber](https://github.com/jsvine/pdfplumber) (for PDF parsing)
- [Streamlit](https://streamlit.io/) (for web UI)
- See `pyproject.toml` for the full list.

---

## Example Data

- Place your two PDF proposals in the `input/` directory as `ley1.pdf` and `ley2.pdf`.
- Example output files are available in the `output/` directory.

---

## Evaluation Criteria (per challenge)

- **Architecture & Code Quality:** Clean, modular design with good separation of logic.
- **Prompt Engineering:** Clear, effective prompts for the LLM.
- **Understanding & Categorization:** Summaries are accurate and reflect the original content; paragraphs are correctly tagged by topic.
- **Critical Analysis:** Pros and cons are thoughtful and based on the paragraph content.
- **Comparison:** Final summary shows depth and useful insights.
- **Transparency:** Each output is auditable, with meta-logs and confidence scores.
- **Agentic System:** The agent can segment, self-evaluate, retry, and flag for review as needed.

---

## License

MIT

---

**For any questions, see the main README or contact the project maintainer.**
