import pytest
from ldaa.agents.self_reflect_segment import self_reflect_segment

@pytest.mark.asyncio
async def test_self_reflect_segment_success(dummy_state, dummy_config, dummy_store, mock_llm):
    state = dummy_state.model_copy()
    state.doc1_analysis = [{'summary': 'Summary1', 'category': 'Cat1', 'pros': [], 'cons': [], 'confidence': 0.9, 'reasoning': 'Good', 'success': True}]
    state.doc2_analysis = [{'summary': 'Summary2', 'category': 'Cat2', 'pros': [], 'cons': [], 'confidence': 0.8, 'reasoning': 'Okay', 'success': True}]
    result = await self_reflect_segment(state, dummy_config, dummy_store)
    assert hasattr(result, 'doc1_segment_actions')
    assert hasattr(result, 'doc2_segment_actions')
    assert len(result.doc1_segment_actions) == 1
    assert len(result.doc2_segment_actions) == 1
    assert result.meta['reflect_segment']['doc1'][0]['success']
    assert result.meta['reflect_segment']['doc2'][0]['success']
    assert all(hasattr(a, 'action') and hasattr(a, 'success') for a in result.doc1_segment_actions)
    assert all(hasattr(a, 'action') and hasattr(a, 'success') for a in result.doc2_segment_actions)

@pytest.mark.asyncio
async def test_self_reflect_segment_empty(dummy_state, dummy_config, dummy_store, mock_llm):
    state = dummy_state.model_copy()
    state.doc1_analysis = []
    state.doc2_analysis = []
    result = await self_reflect_segment(state, dummy_config, dummy_store)
    assert result.doc1_segment_actions == []
    assert result.doc2_segment_actions == [] 