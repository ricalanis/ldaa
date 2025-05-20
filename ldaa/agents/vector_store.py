from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings  # or your preferred embedding model
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from ldaa.schemas import DocumentSegment  # Add this import

# Agent node: Save all segments from both documents into a FAISS vector store
def save_segments_to_faiss(state):
    """
    Agent node: Save all segments from both documents into a FAISS vector store.
    Expects state.doc1_segments and state.doc2_segments to be lists of DocumentSegment objects.
    """
    embeddings = OpenAIEmbeddings()  # configure as needed

    all_segments = []
    metadatas = []
    for doc_num, doc_segments in enumerate([getattr(state, "doc1_segments", []), getattr(state, "doc2_segments", [])], start=1):
        for i, seg in enumerate(doc_segments):
            # seg is a DocumentSegment instance
            all_segments.append(seg.text)
            metadatas.append({
                "doc": doc_num,
                "segment_id": seg.id,
                "title": getattr(seg, "title", f"Doc{doc_num} Segment {i}"),
                "document_id": seg.document_id,
                "segment_type": seg.segment_type,
                "position": seg.position,
            })

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = []
    doc_metas = []
    for text, meta in zip(all_segments, metadatas):
        for chunk in splitter.split_text(text):
            docs.append(chunk)
            doc_metas.append(meta)

    persist_dir = "vector_db"
    os.makedirs(persist_dir, exist_ok=True)
    vectorstore = FAISS.from_texts(docs, embeddings, metadatas=doc_metas)
    vectorstore.save_local(persist_dir)

    # Save only the count of segments in the output
    state.vector_db_path = persist_dir
    state.vector_store_output = {"segment_count": len(all_segments)}
    return state

# Function to query the vector database
def query_vector_db(query, db_path="vector_db", k=3):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.load_local(db_path, embeddings)
    results = vectorstore.similarity_search(query, k=k)
    return results 