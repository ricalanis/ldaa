import streamlit as st
import tempfile
import os
import sys
import json
import asyncio
import threading
import queue
from ldaa.agents.graph import compiled_graph
from ldaa.utils.json import to_serializable
from ldaa.utils.session import generate_session_id

# --- Streamlit UI ---
st.set_page_config(page_title="AI Regulation Comparator", layout="wide")
st.title("🇲🇽 AI Regulation Comparator")

uploaded_files = st.file_uploader(
    "Upload exactly 2 PDF proposals", type=["pdf"], accept_multiple_files=True, key="pdf_uploader"
)

output_format = st.selectbox("Output format", ["json", "markdown"])
run_btn = st.button("Analyze Documents")
console_container = st.empty()
results_container = st.container()

# Enforce a maximum of 2 files in the UI
if uploaded_files and len(uploaded_files) > 2:
    st.warning("Please upload no more than 2 PDF files.")
    uploaded_files = uploaded_files[:2]

def analysis_worker(doc1_path, doc2_path, log_queue, result_queue):
    async def run():
        state = {
            "doc1_path": str(doc1_path),
            "doc2_path": str(doc2_path),
        }
        thread_id = generate_session_id()
        class LogWriter:
            def write(self, msg):
                log_queue.put(msg)
            def flush(self): pass
        old_stdout = sys.stdout
        sys.stdout = LogWriter()
        try:
            print(f"Running agentic graph on: {doc1_path} and {doc2_path} (thread_id={thread_id})")
            result = await compiled_graph.ainvoke(state, config={"configurable": {"thread_id": thread_id}})
            result_queue.put(result)
        finally:
            sys.stdout = old_stdout
    asyncio.run(run())

if run_btn:
    if not uploaded_files or len(uploaded_files) != 2:
        st.warning("You must upload exactly 2 PDF files to proceed.")
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_paths = []
            for i, file in enumerate(uploaded_files):
                file_path = os.path.join(tmpdir, f"doc{i+1}.pdf")
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())
                doc_paths.append(file_path)

            log_queue = queue.Queue()
            result_queue = queue.Queue()
            thread = threading.Thread(target=analysis_worker, args=(doc_paths[0], 
                                                                    doc_paths[1], 
                                                                    log_queue, 
                                                                    result_queue))
            thread.start()

            logs = ""
            import time
            while thread.is_alive() or not log_queue.empty():
                while not log_queue.empty():
                    logs += log_queue.get()
                console_container.text(logs)
                time.sleep(0.1)
            thread.join()
            # Get the result
            result = result_queue.get()
            results_container.subheader("Comparative Summary")
            if output_format == "json":
                results_container.json(to_serializable(result))
                # Add download button for JSON
                json_bytes = json.dumps(to_serializable(result), indent=2).encode('utf-8')
                results_container.download_button(
                    label="Download JSON Report",
                    data=json_bytes,
                    file_name="comparison_result.json",
                    mime="application/json"
                )
            else:
                results_container.info("Markdown output not implemented yet. Showing JSON instead.")
                results_container.json(to_serializable(result))
else:
    st.info("Please upload exactly 2 PDF files and click 'Analyze Documents'.") 