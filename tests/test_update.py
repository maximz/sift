import pandas as pd
import test_status
import time
from pytest import fixture
import search.update, search.metadata_manager

@fixture
def indexdir(tmpdir):
    search.metadata_manager.create_index(str(tmpdir))
    return str(tmpdir)


@fixture
def diff_plan():
    common_time = time.time()
    return {
        'unchanged': test_status.expected_unchanged_file_df(common_time),
        'deleted_files': test_status.expected_removed_file_df(common_time),
        'updated_files': test_status.expected_updated_files_df(common_time),
        'diff_strategy': test_status.expected_updated_files_df(common_time), # TODO
        'newer_strategy': test_status.expected_updated_files_df(common_time), # TODO
        'new_files': test_status.expected_new_file_df(common_time),
    }

def get_filenames(diff_plan, keys):
    return pd.concat([diff_plan[key] for key in keys]).index.unique()

def test_strategy_run_calls(indexdir, mocker, diff_plan):
    """
    Diff work synthetic classifications produce expected strategy run calls on all diff'd files, except unchanged and deleted.
    """
    mocker.patch.object(search.update, 'perform_single_file')
    # also mock out lucene manager so we don't run on empty documents
    mocker.patch('search.lucene_manager.LuceneManager')

    # we expect strategy run() on these filenames
    keys_expected = get_filenames(diff_plan, ['new_files', 'newer_strategy', 'diff_strategy', 'updated_files'])
    # and not on these filenames
    keys_incorrect = get_filenames(diff_plan, ['unchanged', 'deleted_files'])
    search.update.update(indexdir, diff_plan)
    for call in search.update.perform_single_file.call_args_list:
        # call objects are (args, kwargs) tuples
        args, kwargs = call
        file_path = args[2]
        assert file_path in keys_expected
        assert file_path not in keys_incorrect

def test_index_manager_calls():
    """
    Diff work synthetic classifications produce expected index manager calls on all diff'd files, except unchanged,
    and only on deleted if specified.
    """
    pass

def test_summarize_new_index_status():
    """
    summarize_new_index_status handles synthetic diff plans and respects delete_missing.
    """
    pass
