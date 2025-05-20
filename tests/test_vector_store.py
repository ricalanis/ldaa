import os
import shutil
import pytest
from unittest.mock import patch, MagicMock
from ldaa.agents.vector_store import save_segments_to_faiss, query_vector_db
from ldaa.schemas import DocumentSegment

@pytest.fixture
def dummy_segments():
    return [
        DocumentSegment(
            id="seg1",
            text="This is the first segment of doc1.",
            document_id="doc1",
            segment_type="paragraph",
            position=1
        ),
        DocumentSegment(
            id="seg2",
            text="This is the second segment of doc1.",
            document_id="doc1",
            segment_type="paragraph",
            position=2
        ),
    ]

@pytest.fixture
def dummy_state(dummy_segments):
    class State:
        doc1_segments = dummy_segments
        doc2_segments = []
    return State()

@pytest.fixture(autouse=True)
def cleanup_vector_db():
    yield
    if os.path.exists("vector_db"):
        shutil.rmtree("vector_db")

@patch("ldaa.agents.vector_store.OpenAIEmbeddings")
@patch("ldaa.agents.vector_store.FAISS")
def test_save_segments_to_faiss(mock_faiss, mock_embeddings, dummy_state):
    mock_embeddings.return_value = MagicMock()
    mock_faiss.from_texts.return_value = MagicMock(save_local=MagicMock())
    state = save_segments_to_faiss(dummy_state)
    assert hasattr(state, "vector_db_path")
    assert state.vector_db_path == "vector_db"
    assert hasattr(state, "vector_store_output")
    assert isinstance(state.vector_store_output, dict)
    assert state.vector_store_output["segment_count"] == 2
    mock_faiss.from_texts.assert_called()
    mock_faiss.from_texts.return_value.save_local.assert_called_with("vector_db")

@patch("ldaa.agents.vector_store.OpenAIEmbeddings")
@patch("ldaa.agents.vector_store.FAISS")
def test_query_vector_db(mock_faiss, mock_embeddings):
    mock_embeddings.return_value = MagicMock()
    mock_vectorstore = MagicMock()
    mock_vectorstore.similarity_search.return_value = ["result1", "result2"]
    mock_faiss.load_local.return_value = mock_vectorstore
    results = query_vector_db("test query", db_path="vector_db", k=2)
    mock_faiss.load_local.assert_called_with("vector_db", mock_embeddings.return_value)
    mock_vectorstore.similarity_search.assert_called_with("test query", k=2)
    assert results == ["result1", "result2"] 