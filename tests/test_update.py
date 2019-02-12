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

def extract_filename_from_call(call):
    # call objects are (args, kwargs) tuples
    args, kwargs = call
    file_path = args[2]
    return file_path

def assert_lists_equal(l1, l2):
    # https://stackoverflow.com/a/12813909/130164
    assert len(l1) == len(l2) and sorted(l1) == sorted(l2)

def assert_lists_have_no_shared_elements(l1, l2):
    assert set(l1).isdisjoint(set(l2))

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

    # sanity check for the construction of this test
    # confirm none of keys_incorrect are in keys_expected
    for k in keys_incorrect:
        assert k not in keys_expected

    search.update.update(indexdir, diff_plan)
    filepaths = [extract_filename_from_call(c) for c in search.update.perform_single_file.call_args_list]
    assert_lists_equal(filepaths, keys_expected)

def test_index_manager_calls_no_delete(indexdir, mocker, diff_plan):
    """
    Diff work synthetic classifications produce expected index manager calls on all diff'd files, except unchanged,
    and only on deleted if specified.
    """
    # mock file performer so we don't make real documents
    mocker.patch.object(search.update, 'perform_single_file')
    # mock lucene manager so we can measure
    mocker.patch('search.lucene_manager.LuceneManager')

    # we expect insert() on these filenames
    insert_expected = get_filenames(diff_plan, ['new_files'])

    # expect update() on these filenames
    update_expected = get_filenames(diff_plan, ['newer_strategy', 'diff_strategy', 'updated_files'])

    # all other filenames -- no action expected
    no_action_expected = get_filenames(diff_plan, ['unchanged', 'deleted_files'])

    # sanity check on construction of this test
    assert_lists_have_no_shared_elements(insert_expected, update_expected)
    assert_lists_have_no_shared_elements(insert_expected, no_action_expected)
    assert_lists_have_no_shared_elements(update_expected, no_action_expected)

    # run
    search.update.update(indexdir, diff_plan, delete=False)

    filepaths_insert = [extract_filename_from_call(c) for c in search.lucene_manager.LuceneManager.insert.call_args_list]
    assert_lists_equal(filepaths_insert, insert_expected)

    filepaths_update = [extract_filename_from_call(c) for c in search.lucene_manager.LuceneManager.update.call_args_list]
    assert_lists_equal(filepaths_update, update_expected)

    search.lucene_manager.LuceneManager.delete.assert_not_called()

# TODO: exact same with delete -- parametrize?

def test_summarize_new_index_status():
    """
    summarize_new_index_status handles synthetic diff plans and respects delete_missing.
    """
    pass

# test perform_single_file
# test update with some real files
