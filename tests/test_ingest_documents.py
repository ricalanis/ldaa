import pytest
from ldaa.agents.ingest_documents import ingest_documents
from ldaa.schemas import LegalAnalysisState, SegmentAnalysis, DocumentComparison
import sys

@pytest.mark.usefixtures("monkeypatch")
def test_ingest_documents_valid(tmp_path, monkeypatch):
    # Mock pdfplumber.open to return a dummy PDF object
    class DummyPage:
        def extract_text(self):
            return "Hello PDF"
    class DummyPDF:
        pages = [DummyPage(), DummyPage()]
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, exc_tb): pass
    monkeypatch.setattr("pdfplumber.open", lambda path: DummyPDF())
    # Create dummy file paths
    pdf1 = tmp_path / "doc1.pdf"
    pdf2 = tmp_path / "doc2.pdf"
    pdf1.write_bytes(b"%PDF-1.4\n...")
    pdf2.write_bytes(b"%PDF-1.4\n...")
    state = LegalAnalysisState(doc1_path=str(pdf1), doc2_path=str(pdf2))
    state.doc1_accepted_segments = [
        SegmentAnalysis(
            segment='Foo', segment_id='1', summary='Summary1', category='Cat1', segment_type='section',
            pros=['pro'], cons=['con'], confidence=0.9, reasoning='Good', meta={}, success=True
        )
    ]
    state.doc2_accepted_segments = [
        SegmentAnalysis(
            segment='Baz', segment_id='2', summary='Summary2', category='Cat2', segment_type='section',
            pros=['pro'], cons=['con'], confidence=0.8, reasoning='Okay', meta={}, success=True
        )
    ]
    result = ingest_documents(state, config=None, store=None)
    assert hasattr(result, 'doc1_text')
    assert hasattr(result, 'doc2_text')
    assert result.doc1_text == "Hello PDF\nHello PDF"
    assert result.doc2_text == "Hello PDF\nHello PDF"
    assert result.meta['ingest']["doc1"]["success"]
    assert result.meta['ingest']["doc2"]["success"]
    assert result.meta['ingest']["doc1"]["num_pages"] == 2
    assert result.meta['ingest']["doc2"]["num_pages"] == 2
    print("[DEBUG] Ingested doc1_text:", repr(result.doc1_text[:500]) if result.doc1_text else "None")
    print("[DEBUG] Ingested doc2_text:", repr(result.doc2_text[:500]) if result.doc2_text else "None")

    required_fields = {
        "similarities": [],
        "differences": [],
        "focus_areas": {},
        "gaps": [],
        "meta": result.meta['ingest']["doc1"]["reasoning"] or "",
        "success": False,
    }
    for k, v in required_fields.items():
        result.meta['ingest']["doc1"].setdefault(k, v)
    result.meta['ingest']["doc1"] = DocumentComparison(
        similarities=[],
        differences=[],
        focus_areas={},
        gaps=[],
        meta={},
        verbose_comparison="Test verbose",
        comparative_summary="Test summary",
        confidence=1.0,
        reasoning="Test reasoning",
        success=True
    )

    required_fields = {
        "similarities": [],
        "differences": [],
        "focus_areas": {},
        "gaps": [],
        "meta": result.meta['ingest']["doc2"]["reasoning"] or "",
        "success": False,
    }
    for k, v in required_fields.items():
        result.meta['ingest']["doc2"].setdefault(k, v)
    result.meta['ingest']["doc2"] = DocumentComparison(
        similarities=[],
        differences=[],
        focus_areas={},
        gaps=[],
        meta={},
        verbose_comparison="Test verbose",
        comparative_summary="Test summary",
        confidence=1.0,
        reasoning="Test reasoning",
        success=True
    )

@pytest.mark.usefixtures("monkeypatch")
def test_ingest_documents_missing_path(monkeypatch):
    # Mock pdfplumber.open to never be called
    monkeypatch.setattr("pdfplumber.open", lambda path: (_ for _ in ()).throw(Exception("Should not be called")))
    state = LegalAnalysisState(doc1_path=None, doc2_path=None)
    result = ingest_documents(state, config=None, store=None)
    assert result.doc1_text is None
    assert result.doc2_text is None
    assert not result.meta['ingest']["doc1"]["success"]
    assert not result.meta['ingest']["doc2"]["success"]

    required_fields = {
        "similarities": [],
        "differences": [],
        "focus_areas": {},
        "gaps": [],
        "meta": result.meta['ingest']["doc1"]["reasoning"] or "",
        "success": False,
    }
    for k, v in required_fields.items():
        result.meta['ingest']["doc1"].setdefault(k, v)
    result.meta['ingest']["doc1"] = DocumentComparison(
        similarities=[],
        differences=[],
        focus_areas={},
        gaps=[],
        meta={},
        verbose_comparison="Test verbose",
        comparative_summary="Test summary",
        confidence=1.0,
        reasoning="Test reasoning",
        success=False
    )

    required_fields = {
        "similarities": [],
        "differences": [],
        "focus_areas": {},
        "gaps": [],
        "meta": result.meta['ingest']["doc2"]["reasoning"] or "",
        "success": False,
    }
    for k, v in required_fields.items():
        result.meta['ingest']["doc2"].setdefault(k, v)
    result.meta['ingest']["doc2"] = DocumentComparison(
        similarities=[],
        differences=[],
        focus_areas={},
        gaps=[],
        meta={},
        verbose_comparison="Test verbose",
        comparative_summary="Test summary",
        confidence=1.0,
        reasoning="Test reasoning",
        success=False
    ) 