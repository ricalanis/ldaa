# scripts/cli.py
import sys
from pathlib import Path
from ldaa.agents.graph import compiled_graph
import asyncio
import json
from ldaa.utils.json import to_serializable
import argparse
from ldaa.utils.session import generate_session_id

def print_result(result):
    print("\n---\nGraph run complete.")
    print(f"Output JSON: {result.get('output_path')}")
    meta = result.get('meta_log', {})
    print(f"Meta-log: {meta}")
    comp = result.get('comparison_result', {})

def parse_args():
    parser = argparse.ArgumentParser(description="Run the LDAA agentic graph on two PDF documents.")
    parser.add_argument("doc1", type=str, nargs="?", default="input/ley1.pdf", help="Path to the first PDF document.")
    parser.add_argument("doc2", type=str, nargs="?", default="input/ley2.pdf", help="Path to the second PDF document.")
    return parser.parse_args()

async def main():
    args = parse_args()
    doc1 = Path(args.doc1)
    doc2 = Path(args.doc2)
    state = {
        "doc1_path": str(doc1),
        "doc2_path": str(doc2),
    }
    thread_id = generate_session_id()
    print(f"Running agentic graph on: {doc1} and {doc2} (thread_id={thread_id})")
    await compiled_graph.ainvoke(
        state,
        config={"configurable": {"thread_id": thread_id}}
    )


if __name__ == "__main__":
    asyncio.run(main())

# scripts/run_graph.py
# Deprecated: Please use scripts/cli.py instead.
# Example: python scripts/cli.py input/ley1.pdf input/ley2.pdf --output output/final_result.json 