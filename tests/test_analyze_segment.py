import pytest
from ldaa.agents.analyze_segment import analyze_segment
from ldaa.schemas import DocumentSegment

@pytest.mark.asyncio
async def test_analyze_segment_success(dummy_state, dummy_config, dummy_store, mock_llm):
    state = dummy_state.model_copy()
    state.doc1_segments = [DocumentSegment(id='doc1_seg_0', text='Foo', document_id='doc1', segment_type='section', position=0)]
    state.doc2_segments = [DocumentSegment(id='doc2_seg_0', text='Baz', document_id='doc2', segment_type='section', position=0)]
    result = await analyze_segment(state, dummy_config, dummy_store)
    assert hasattr(result, 'doc1_analysis')
    assert hasattr(result, 'doc2_analysis')
    assert len(result.doc1_analysis) == 1
    assert len(result.doc2_analysis) == 1
    assert result.meta['analysis']['doc1'][0]['success']
    assert result.meta['analysis']['doc2'][0]['success']
    assert all(hasattr(a, 'summary') and hasattr(a, 'category') and hasattr(a, 'success') for a in result.doc1_analysis)
    assert all(hasattr(a, 'summary') and hasattr(a, 'category') and hasattr(a, 'success') for a in result.doc2_analysis)

@pytest.mark.asyncio
async def test_analyze_segment_empty(dummy_state, dummy_config, dummy_store, mock_llm):
    state = dummy_state.model_copy()
    state.doc1_segments = []
    state.doc2_segments = []
    result = await analyze_segment(state, dummy_config, dummy_store)
    assert result.doc1_analysis == []
    assert result.doc2_analysis == [] 