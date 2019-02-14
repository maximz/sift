import pandas as pd
import test_status
import time
from pytest import fixture, mark
import search.update, search.metadata_manager
import itertools

@fixture
def indexdir(tmpdir):
    search.metadata_manager.create_index(str(tmpdir))
    return str(tmpdir)

@fixture
def mock_index_manager(mocker):
    # mock out lucene manager so we don't run on empty documents
    return mocker.patch('search.lucene_manager.LuceneManager',  autospec=True)

@fixture
def diff_plan():
    common_time = time.time()
    return {
        'unchanged': test_status.expected_unchanged_file_df(common_time),
        'deleted_files': test_status.expected_removed_file_df(common_time),
        'updated_files': test_status.expected_updated_files_df(common_time),
        'diff_strategy': test_status.expected_diff_strategy_df(common_time),
        'newer_strategy': test_status.expected_newer_strategy_df(common_time),
        'new_files': test_status.expected_new_file_df(common_time),
    }

def get_filenames(diff_plan, keys):
    return pd.concat([diff_plan[key] for key in keys]).index.unique()

def extract_from_call(call, arg_index):
    # call objects are (args, kwargs) tuples
    args, kwargs = call
    return args[arg_index]

def extract_filename_from_perform_single_file_call(call):
    return extract_from_call(call, 2)

def extract_filename_from_index_call(call):
    return extract_from_call(call, 0)

def assert_lists_equal(l1, l2):
    # https://stackoverflow.com/a/12813909/130164
    assert len(l1) == len(l2) and sorted(l1) == sorted(l2)

def assert_lists_have_no_shared_elements(l1, l2):
    assert set(l1).isdisjoint(set(l2))


def test_strategy_run_calls(indexdir, mock_index_manager, mocker, diff_plan):
    """
    Diff work synthetic classifications produce expected strategy run calls on all diff'd files, except unchanged and deleted.
    """
    mocker.patch.object(search.update, 'perform_single_file')

    # we expect strategy run() on these filenames
    keys_expected = get_filenames(diff_plan, ['new_files', 'newer_strategy', 'diff_strategy', 'updated_files'])
    # and not on these filenames
    keys_incorrect = get_filenames(diff_plan, ['unchanged', 'deleted_files'])

    # sanity check for the construction of this test
    # confirm none of keys_incorrect are in keys_expected
    for k in keys_incorrect:
        assert k not in keys_expected

    search.update.update(indexdir, mock_index_manager, diff_plan)
    filepaths = [extract_filename_from_perform_single_file_call(c) for c in search.update.perform_single_file.call_args_list]
    assert_lists_equal(filepaths, keys_expected)


@mark.parametrize("delete", [False, True])
def test_index_manager_calls_depending_on_delete(indexdir, mock_index_manager, mocker, diff_plan, delete):
    """
    Diff work synthetic classifications produce expected index manager calls on all diff'd files, except unchanged,
    and only on deleted if specified.
    """
    # mock file performer so we don't make real documents
    # instead return just the key so we can track where this key goes
    mocker.patch.object(search.update, 'perform_single_file')
    search.update.perform_single_file.side_effect = lambda strategies, extension, file_path: file_path
    # we also mocked lucene manager so we can measure -- mock_index_manager

    # we expect insert() on these filenames
    insert_expected = get_filenames(diff_plan, ['new_files'])

    # expect update() on these filenames
    update_expected = get_filenames(diff_plan, ['newer_strategy', 'diff_strategy', 'updated_files'])

    # possibly expect delete() on these filenames
    delete_expected = get_filenames(diff_plan, ['deleted_files'])

    # all other filenames -- no action expected
    no_action_expected = get_filenames(diff_plan, ['unchanged'])

    # sanity check on construction of this test
    # confirm no elements shared between any combination of these lists
    for a, b in itertools.combinations([insert_expected, update_expected, delete_expected, no_action_expected], 2):
        assert_lists_have_no_shared_elements(a, b)

    # run
    search.update.update(indexdir, mock_index_manager, diff_plan, delete=delete, verbose=True)

    filepaths_insert = [extract_filename_from_index_call(c) for c in mock_index_manager.insert.call_args_list]
    assert_lists_equal(filepaths_insert, insert_expected)

    filepaths_update = [extract_filename_from_index_call(c) for c in mock_index_manager.update.call_args_list]
    assert_lists_equal(filepaths_update, update_expected)

    if delete:
        filepaths_delete = [extract_filename_from_index_call(c) for c in mock_index_manager.delete.call_args_list]
        assert_lists_equal(filepaths_delete, delete_expected)
    else:
        mock_index_manager.delete.assert_not_called()

def test_summarize_new_index_status():
    """
    summarize_new_index_status handles synthetic diff plans and respects delete_missing.
    """
    pass

# test perform_single_file
# test update with some real files
