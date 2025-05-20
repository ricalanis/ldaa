import pytest
import os
from ldaa.agents.final_audit_export import final_audit_export

@pytest.fixture
def change_to_tmp_path(tmp_path):
    orig_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield
    os.chdir(orig_cwd)

def test_final_audit_export_creates_files(change_to_tmp_path, tmp_path, dummy_state, dummy_config, dummy_store):
    """Test that final_audit_export creates the expected output files in the output directory."""
    state = dummy_state.model_copy()
    # Inject a verbose_comparison into the comparison_result if possible
    if hasattr(state, 'comparison_result') and state.comparison_result is not None:
        # Handle both pydantic object and dict
        if hasattr(state.comparison_result, 'verbose_comparison'):
            state.comparison_result.verbose_comparison = "# Verbose Comparison\nSome detailed markdown content."
        elif isinstance(state.comparison_result, dict):
            state.comparison_result['verbose_comparison'] = "# Verbose Comparison\nSome detailed markdown content."
    result = final_audit_export(state, dummy_config, dummy_store)
    assert hasattr(result, 'output_path')
    assert 'final_audit' in result.meta
    assert result.meta['final_audit']['success']
    assert os.path.exists(result.output_path)
    md_path = os.path.join(tmp_path, 'output', 'report.md')
    assert os.path.exists(md_path)
    # Check for verbose_comparison.md if verbose_comparison was set
    verbose_md_path = os.path.join(tmp_path, 'output', 'verbose_comparison.md')
    if (hasattr(state, 'comparison_result') and (
        (hasattr(state.comparison_result, 'verbose_comparison') and state.comparison_result.verbose_comparison) or
        (isinstance(state.comparison_result, dict) and state.comparison_result.get('verbose_comparison'))
    )):
        assert os.path.exists(verbose_md_path)
        assert 'verbose_comparison_md' in result.meta['final_audit']
        assert result.meta['final_audit']['verbose_comparison_md'].endswith('verbose_comparison.md') 