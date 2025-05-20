import pdfplumber
from ldaa.utils.logging import log_event, log_error

def extract_pdf_text(pdf_path):
    print("[DEBUG] Attempting to read PDF with pdfplumber:", pdf_path)
    results = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            print(f"[DEBUG] Page {i+1} text: ", repr(text[:200]))
            results.append(text)
    all_text = "\n".join(results)
    meta = {
        "num_pages": len(results),
        "success": True,
        "error": None,
        "reasoning": "Successfully extracted PDF text."
    }
    print(f"***{all_text}***")
    return all_text, meta

def ingest_documents(state, config, store):
    """
    Ingests two PDF documents, extracts raw text from each, and logs meta information.
    Updates the state in-place and returns it, as required by LangGraph node conventions.
    """
    log_event("INGEST", "Starting document ingestion")
    doc1_path = state.doc1_path
    doc2_path = state.doc2_path
    doc1_text, meta1 = extract_pdf_text(doc1_path) if doc1_path else (None, {"success": False, "error": "No path provided", "reasoning": "No path provided."})
    doc2_text, meta2 = extract_pdf_text(doc2_path) if doc2_path else (None, {"success": False, "error": "No path provided", "reasoning": "No path provided."})
    print("[DEBUG] Ingested doc1_text:", repr(doc1_text[:500]) if doc1_text is not None else "None")
    print("[DEBUG] Ingested doc2_text:", repr(doc2_text[:500]) if doc2_text is not None else "None")
    meta_log = {
        "doc1": meta1,
        "doc2": meta2,
    }
    # Update state using attribute access
    state.doc1_text = doc1_text
    state.doc2_text = doc2_text
    state.meta['ingest'] = meta_log
    log_event("INGEST", "Document ingestion successful.")
    return state