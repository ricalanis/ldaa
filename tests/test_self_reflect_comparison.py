import pytest
from ldaa.agents.self_reflect_comparison import self_reflect_comparison

@pytest.mark.asyncio
async def test_self_reflect_comparison_success(dummy_state, dummy_config, dummy_store, mock_llm):
    state = dummy_state.model_copy()
    state.comparison_result = {'comparative_summary': 'Diff', 'confidence': 0.95, 'reasoning': 'Solid', 'success': True}
    result = await self_reflect_comparison(state, dummy_config, dummy_store)
    assert hasattr(result, 'comparison_action')
    assert result.comparison_action.success
    assert 'reflect_comparison' in result.meta
    assert result.meta['reflect_comparison']['success']

@pytest.mark.asyncio
async def test_self_reflect_comparison_empty(dummy_state, dummy_config, dummy_store, mock_llm):
    state = dummy_state.model_copy()
    state.comparison_result = {}
    result = await self_reflect_comparison(state, dummy_config, dummy_store)
    assert hasattr(result, 'comparison_action')
    assert hasattr(result.comparison_action, 'success')
    assert 'reflect_comparison' in result.meta
    assert result.meta['reflect_comparison']['success'] 