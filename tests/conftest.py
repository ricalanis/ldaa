import pytest
from unittest.mock import MagicMock, AsyncMock
from ldaa.schemas import DocumentSegment, SegmentAnalysis, SegmentAction, DocumentComparison, ComparisonAction, LegalAnalysisState

@pytest.fixture
def dummy_state():
    return LegalAnalysisState(
        doc1_path='dummy1.pdf',
        doc2_path='dummy2.pdf',
        doc1_text='Section 1. Foo. Section 2. Bar.',
        doc2_text='Section 1. Baz. Section 2. Qux.',
        doc1_segments=[DocumentSegment(id='1', text='Foo', document_id='doc1', segment_type='section', position=1)],
        doc2_segments=[DocumentSegment(id='2', text='Baz', document_id='doc2', segment_type='section', position=1)],
        doc1_analysis=[SegmentAnalysis(segment='Foo', segment_id='1', summary='Summary1', category='Cat1', pros=['pro'], cons=['con'], confidence=0.9, reasoning='Good', meta={}, success=True)],
        doc2_analysis=[SegmentAnalysis(segment='Baz', segment_id='2', summary='Summary2', category='Cat2', pros=['pro'], cons=['con'], confidence=0.8, reasoning='Okay', meta={}, success=True)],
        doc1_segment_actions=[SegmentAction(segment_index=0, action='accept', confidence=0.9, reasoning='Confident', success=True)],
        doc2_segment_actions=[SegmentAction(segment_index=0, action='accept', confidence=0.8, reasoning='Confident', success=True)],
        doc1_accepted_segments=[SegmentAnalysis(segment='Foo', segment_id='1', summary='Summary1', category='Cat1', pros=['pro'], cons=['con'], confidence=0.9, reasoning='Good', meta={}, success=True)],
        doc2_accepted_segments=[SegmentAnalysis(segment='Baz', segment_id='2', summary='Summary2', category='Cat2', pros=['pro'], cons=['con'], confidence=0.8, reasoning='Okay', meta={}, success=True)],
        comparison_result=DocumentComparison(
            similarities=[],
            differences=[],
            focus_areas={},
            gaps=[],
            meta={},
            verbose_comparison='',
            comparative_summary='',
            confidence=1.0,
            reasoning='',
            success=True
        ),
        comparison_action=ComparisonAction(action='accept', confidence=0.95, reasoning='Solid', success=True),
        output_path='dummy_output_path',
        meta={},
        # Explicitly set all fields, even if default
    )

@pytest.fixture
def dummy_state_all_fields():
    # This fixture sets every field in LegalAnalysisState explicitly, including defaults
    return LegalAnalysisState(
        doc1_path='dummy1.pdf',
        doc2_path='dummy2.pdf',
        doc1_text='Section 1. Foo. Section 2. Bar.',
        doc2_text='Section 1. Baz. Section 2. Qux.',
        doc1_segments=[DocumentSegment(id='1', text='Foo', document_id='doc1', segment_type='section', position=1)],
        doc2_segments=[DocumentSegment(id='2', text='Baz', document_id='doc2', segment_type='section', position=1)],
        doc1_analysis=[SegmentAnalysis(segment='Foo', segment_id='1', summary='Summary1', category='Cat1', pros=['pro'], cons=['con'], confidence=0.9, reasoning='Good', meta={}, success=True)],
        doc2_analysis=[SegmentAnalysis(segment='Baz', segment_id='2', summary='Summary2', category='Cat2', pros=['pro'], cons=['con'], confidence=0.8, reasoning='Okay', meta={}, success=True)],
        doc1_segment_actions=[SegmentAction(segment_index=0, action='accept', confidence=0.9, reasoning='Confident', success=True)],
        doc2_segment_actions=[SegmentAction(segment_index=0, action='accept', confidence=0.8, reasoning='Confident', success=True)],
        doc1_accepted_segments=[SegmentAnalysis(segment='Foo', segment_id='1', summary='Summary1', category='Cat1', pros=['pro'], cons=['con'], confidence=0.9, reasoning='Good', meta={}, success=True)],
        doc2_accepted_segments=[SegmentAnalysis(segment='Baz', segment_id='2', summary='Summary2', category='Cat2', pros=['pro'], cons=['con'], confidence=0.8, reasoning='Okay', meta={}, success=True)],
        comparison_result=DocumentComparison(similarities=[], differences=[], focus_areas={}, gaps=[], meta="", verbose_comparison=None, comparative_summary=None, confidence=None, reasoning=None, success=None),
        comparison_action=ComparisonAction(action='accept', confidence=0.95, reasoning='Solid', success=True),
        output_path='dummy_output_path',
        meta={},
    )

@pytest.fixture
def dummy_config():
    return MagicMock()

@pytest.fixture
def dummy_store():
    return MagicMock()

@pytest.fixture
def mock_llm(monkeypatch):
    class DummyLLM:
        async def ainvoke(self, prompt):
            class Response:
                content = '[{"title": "Section 1", "text": "Foo"}]'
            return Response()
    monkeypatch.setattr('ldaa.agents.llm.get_llm', lambda: DummyLLM())
    return DummyLLM() 