import pytest
import copy
from ldaa.agents.aggregate_results import aggregate_results
from ldaa.schemas import SegmentAction, SegmentAnalysis

# Fixtures for dummy_state, dummy_config, and dummy_store are provided in conftest.py

def test_aggregate_results_accept(dummy_state, dummy_config, dummy_store):
    """Test that all 'accept' actions are aggregated correctly."""
    state = dummy_state.model_copy()
    result = aggregate_results(state, dummy_config, dummy_store)
    assert hasattr(result, 'doc1_accepted_segments')
    assert hasattr(result, 'doc2_accepted_segments')
    assert result.meta['aggregate']['doc1']['accept'] == len(state.doc1_segment_actions)
    assert result.meta['aggregate']['doc2']['accept'] == len(state.doc2_segment_actions)
    assert all(a.action == 'accept' for a in state.doc1_segment_actions)
    assert all(a.action == 'accept' for a in state.doc2_segment_actions)
    assert len(result.doc1_accepted_segments) == len(state.doc1_segment_actions)
    assert len(result.doc2_accepted_segments) == len(state.doc2_segment_actions)
    assert all(hasattr(a, 'summary') for a in result.doc1_accepted_segments)
    assert all(hasattr(a, 'summary') for a in result.doc2_accepted_segments)

def test_aggregate_results_mixed_actions(dummy_state, dummy_config, dummy_store):
    """Test aggregation with mixed actions (accept, retry, mark_review)."""
    state = dummy_state.model_copy()
    state.doc1_segment_actions = [
        SegmentAction(segment_index=0, action='accept', confidence=0.9, reasoning='Confident', success=True),
        SegmentAction(segment_index=1, action='retry', confidence=0.5, reasoning='Retry', success=True),
        SegmentAction(segment_index=2, action='mark_review', confidence=0.2, reasoning='Review', success=True),
    ]
    state.doc1_analysis = [
        SegmentAnalysis(segment='S1', segment_id='1', summary='S1', category='C1', segment_type='section', pros=['pro'], cons=['con'], confidence=0.9, reasoning='Good', meta={}, success=True),
        SegmentAnalysis(segment='S2', segment_id='2', summary='S2', category='C2', segment_type='section', pros=['pro'], cons=['con'], confidence=0.5, reasoning='Retry', meta={}, success=True),
        SegmentAnalysis(segment='S3', segment_id='3', summary='S3', category='C3', segment_type='section', pros=['pro'], cons=['con'], confidence=0.2, reasoning='Review', meta={}, success=True),
    ]
    state.doc2_segment_actions = [
        SegmentAction(segment_index=0, action='accept', confidence=0.8, reasoning='Confident', success=True),
        SegmentAction(segment_index=1, action='accept', confidence=0.7, reasoning='Confident', success=True),
    ]
    state.doc2_analysis = [
        SegmentAnalysis(segment='S4', segment_id='4', summary='S4', category='C4', segment_type='section', pros=['pro'], cons=['con'], confidence=0.8, reasoning='Good', meta={}, success=True),
        SegmentAnalysis(segment='S5', segment_id='5', summary='S5', category='C5', segment_type='section', pros=['pro'], cons=['con'], confidence=0.7, reasoning='Good', meta={}, success=True),
    ]
    result = aggregate_results(state, dummy_config, dummy_store)
    assert result.meta['aggregate']['doc1']['accept'] == 1
    assert result.meta['aggregate']['doc1']['retry'] == 1
    assert result.meta['aggregate']['doc1']['mark_review'] == 1
    assert len(result.doc1_accepted_segments) == 1
    assert result.meta['aggregate']['doc2']['accept'] == 2
    assert len(result.doc2_accepted_segments) == 2
    assert all(hasattr(a, 'summary') for a in result.doc1_accepted_segments)
    assert all(hasattr(a, 'summary') for a in result.doc2_accepted_segments) 