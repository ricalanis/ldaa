import pytest
from ldaa.agents.compare_documents import compare_documents
from ldaa.schemas import SegmentAnalysis

@pytest.mark.asyncio
async def test_compare_documents_success(dummy_state, dummy_config, dummy_store, mock_llm):
    state = dummy_state.model_copy()
    state.doc1_accepted_segments = [
        SegmentAnalysis(segment='S1', segment_id='1', summary='Summary1', category='Cat1', segment_type='section', pros=['pro1'], cons=['con1'], confidence=0.9, reasoning='Good', meta={}, success=True)
    ]
    state.doc2_accepted_segments = [
        SegmentAnalysis(segment='S2', segment_id='2', summary='Summary2', category='Cat2', segment_type='section', pros=['pro2'], cons=['con2'], confidence=0.8, reasoning='Okay', meta={}, success=True)
    ]
    result = await compare_documents(state, dummy_config, dummy_store)
    assert hasattr(result, 'comparison_result')
    assert result.comparison_result.success
    assert hasattr(result, 'meta')
    assert result.meta['compare']['success']

@pytest.mark.asyncio
async def test_compare_documents_empty(dummy_state, dummy_config, dummy_store, mock_llm):
    state = dummy_state.model_copy()
    state.doc1_accepted_segments = []
    state.doc2_accepted_segments = []
    result = await compare_documents(state, dummy_config, dummy_store)
    assert hasattr(result, 'comparison_result')
    assert hasattr(result.comparison_result, 'success') 