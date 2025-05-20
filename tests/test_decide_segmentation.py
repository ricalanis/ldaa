import pytest
from ldaa.agents.decide_segmentation import decide_segmentation

@pytest.mark.asyncio
async def test_decide_segmentation_success(dummy_state, dummy_config, dummy_store, mock_llm):
    # Provide doc1_text and doc2_text in dummy_state
    state = dummy_state.model_copy()
    state.doc1_text = 'Section 1. Foo. Section 2. Bar.'
    state.doc2_text = 'Section 1. Baz. Section 2. Qux.'
    result = await decide_segmentation(state, dummy_config, dummy_store)
    assert hasattr(result, 'doc1_segments')
    assert hasattr(result, 'doc2_segments')
    assert result.meta['segmentation']['doc1']['success']
    assert result.meta['segmentation']['doc2']['success']
    assert all(hasattr(seg, 'text') for seg in result.doc1_segments)
    assert all(hasattr(seg, 'text') for seg in result.doc2_segments)

@pytest.mark.asyncio
async def test_decide_segmentation_no_text(dummy_state, dummy_config, dummy_store, mock_llm):
    state = dummy_state.model_copy()
    state.doc1_text = ''
    state.doc2_text = ''
    result = await decide_segmentation(state, dummy_config, dummy_store)
    assert result.doc1_segments == []
    assert result.doc2_segments == []
    assert not result.meta['segmentation']['doc1']['success']
    assert not result.meta['segmentation']['doc2']['success'] 