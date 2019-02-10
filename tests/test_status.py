import search.status
import time
import pytest
import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal

@pytest.fixture
def mock_importer(mocker):
    def _mock_importer(name, version):
        mock = mocker.MagicMock(spec=search.importers.importer.Importer)
        mock.__name__ = name
        mock.version = version
        return mock
    return _mock_importer

@pytest.fixture
def filetype_strategies(mock_importer):
    return {
        'txt': mock_importer('TextImporter', 1.0),
        'md': mock_importer('MarkdownImporter', 3.0),
        'pdf': mock_importer('PandocImporter', 5.0),
    }


@pytest.fixture
def mock_index():
    def _mock_index(names, times, strategies=None, strategy_versions=None):
        if strategies is None:
            strategies = ['MyImporter' for i in range(len(names))]
        if strategy_versions is None:
            strategy_versions = [1.0 for i in range(len(names))]
        assert len(names) == len(times) == len(
            strategies) == len(strategy_versions)
        # specify dtypes so that string NaNs become None not np.nan
        return pd.DataFrame({
            'fname': pd.Series(names, dtype='str'),
            'last_mod': pd.Series(times, dtype='float'),
            'strategy': pd.Series(strategies, dtype='str'),
            'strategy_version': pd.Series(strategy_versions, dtype='float'),
        }).set_index('fname')
    return _mock_index


def test_make_plan_from_scratch(mocker, filetype_strategies, mock_index):
    """
    Confirm make_plan_from_scratch returns whitelisted extensions only with appropriate importer metadata.
    """
    mocker.patch.object(search.status, 'file_list')
    common_time = time.time()
    search.status.file_list.side_effect = [
        # return value for first execution
        [
            {
                'fname': 'test.txt',
                'last_mod': common_time
            }
        ],
        # return value for second execution
        [
            {
                'fname': 'test.md',
                'last_mod': common_time
            }
        ],
        # return value for third execution
        [],
    ]
    assert_frame_equal(
        search.status.make_plan_from_scratch('.', filetype_strategies),
        mock_index(
            names=['test.txt', 'test.md'],
            times=[common_time, common_time],
            strategies=['TextImporter', 'MarkdownImporter'],
            strategy_versions=[1.0, 3.0],
        )
    )

def test_make_plan_from_scratch_empty_directory_dtypes(mocker, filetype_strategies, mock_index):
    """
    Confirm make_plan_from_scratch returns the right dtypes when there are no files.
    """
    mocker.patch.object(search.status, 'file_list')
    search.status.file_list.return_value = []
    assert_frame_equal(
        search.status.make_plan_from_scratch('.', filetype_strategies),
        mock_index([], []) # correct dtypes specified here
    )


# expected column order
diff_plan_expected_column_order = [
    'last_mod_old', 'strategy_old', 'strategy_version_old', 'last_mod_new',
    'strategy_new', 'strategy_version_new', '_merge'
]
expected_empty_diffplan_shape = (0, len(diff_plan_expected_column_order))
def empty_diffplan(plan):
    return plan.shape == expected_empty_diffplan_shape

def test_diff_work_new_files(mock_index):
    """
    Confirm diff_work_between_plans produces proper classifications on synthetic plans, in this case with a new file.
    """
    common_time = time.time()
    old_index = mock_index([], [])
    new_index = mock_index(['new_file.txt'], [common_time])

    diff_work = search.status.diff_work_between_plans(old_index, new_index)
    print(diff_work['new_files'])

    assert_frame_equal(
        diff_work['new_files'],
        pd.DataFrame({
            'fname': ['new_file.txt'],
            'last_mod_old': [np.nan],  # float
            'last_mod_new': [common_time],
            'strategy_old': [None],  # object
            'strategy_new': ['MyImporter'],
            'strategy_version_old': [np.nan],  # float
            'strategy_version_new': [1.0],
            '_merge': pd.Series(
                ['right_only'],
                dtype=pd.api.types.CategoricalDtype(
                    categories=['left_only', 'right_only', 'both'], ordered=False)
            )
        }).set_index('fname')[diff_plan_expected_column_order]
    )

    assert empty_diffplan(diff_work['unchanged'])
    assert empty_diffplan(diff_work['deleted_files'])
    assert empty_diffplan(diff_work['updated_files'])
    assert empty_diffplan(diff_work['diff_strategy'])
    assert empty_diffplan(diff_work['newer_strategy'])


def test_diff_work_unchanged_file(mock_index):
    """
    Confirm diff_work_between_plans produces proper classifications on synthetic plans, in this case with a new file.
    """
    common_time = time.time()
    index = mock_index(['old_file.txt'], [common_time])

    diff_work = search.status.diff_work_between_plans(index, index)

    assert empty_diffplan(diff_work['new_files'])
    assert empty_diffplan(diff_work['deleted_files'])
    assert empty_diffplan(diff_work['updated_files'])
    assert empty_diffplan(diff_work['diff_strategy'])
    assert empty_diffplan(diff_work['newer_strategy'])

    assert_frame_equal(
        diff_work['unchanged'],
        pd.DataFrame({
            'fname': ['old_file.txt'],
            'last_mod_old': [common_time],
            'last_mod_new': [common_time],
            'strategy_old': ['MyImporter'],
            'strategy_new': ['MyImporter'],
            'strategy_version_old': [1.0],
            'strategy_version_new': [1.0],
            '_merge': pd.Series(
                ['both'],
                dtype=pd.api.types.CategoricalDtype(
                    categories=['left_only', 'right_only', 'both'], ordered=False)
            )
        }).set_index('fname')[diff_plan_expected_column_order]
    )


def test_diff_work_new_and_unchanged_files(mock_index):
    """
    Confirm diff_work_between_plans produces proper classifications on synthetic plans, in this case with 1 new, 1 unchanged file.
    """
    common_time = time.time()
    old_index = mock_index(['old_file.txt'], [common_time])
    new_index = mock_index(['old_file.txt', 'new_file.txt'], [common_time, common_time])

    diff_work = search.status.diff_work_between_plans(old_index, new_index)

    assert_frame_equal(
        diff_work['new_files'],
        pd.DataFrame({
            'fname': ['new_file.txt'],
            'last_mod_old': [np.nan], # float
            'last_mod_new': [common_time],
            'strategy_old': [None], # object
            'strategy_new': ['MyImporter'],
            'strategy_version_old': [np.nan], # float
            'strategy_version_new': [1.0],
            '_merge': pd.Series(
                ['right_only'],
                dtype=pd.api.types.CategoricalDtype(
                    categories=['left_only', 'right_only', 'both'], ordered=False)
            )
        }).set_index('fname')[diff_plan_expected_column_order]
    )

    assert empty_diffplan(diff_work['deleted_files'])
    assert empty_diffplan(diff_work['updated_files'])
    assert empty_diffplan(diff_work['diff_strategy'])
    assert empty_diffplan(diff_work['newer_strategy'])

    assert_frame_equal(
        diff_work['unchanged'],
        pd.DataFrame({
            'fname': ['old_file.txt'],
            'last_mod_old': [common_time],
            'last_mod_new': [common_time],
            'strategy_old': ['MyImporter'],
            'strategy_new': ['MyImporter'],
            'strategy_version_old': [1.0],
            'strategy_version_new': [1.0],
            '_merge': pd.Series(
                ['both'],
                dtype=pd.api.types.CategoricalDtype(
                    categories=['left_only', 'right_only', 'both'], ordered=False)
            )
        }).set_index('fname')[diff_plan_expected_column_order]
    )





def test_diff_work_removed_only_file(mock_index):
    """
    Confirm diff_work_between_plans produces proper classifications on synthetic plans, in this case with 1 removed file.
    """
    common_time = time.time()
    old_index = mock_index(['file.txt'], [common_time])
    new_index = mock_index([], [])

    diff_work = search.status.diff_work_between_plans(old_index, new_index)

    assert_frame_equal(
        diff_work['deleted_files'],
        pd.DataFrame({
            'fname': ['file.txt'],
            'last_mod_old': [common_time],
            'last_mod_new': [np.nan],  # float
            'strategy_new': [None],  # object
            'strategy_old': ['MyImporter'],
            'strategy_version_new': [np.nan],  # float
            'strategy_version_old': [1.0],
            '_merge': pd.Series(
                ['left_only'],
                dtype=pd.api.types.CategoricalDtype(
                    categories=['left_only', 'right_only', 'both'], ordered=False)
            )
        }).set_index('fname')[diff_plan_expected_column_order]
    )

    assert empty_diffplan(diff_work['new_files'])
    assert empty_diffplan(diff_work['updated_files'])
    assert empty_diffplan(diff_work['diff_strategy'])
    assert empty_diffplan(diff_work['newer_strategy'])
    assert empty_diffplan(diff_work['unchanged'])


def test_diff_work_removed_and_unchanged_files(mock_index):
    """
    Confirm diff_work_between_plans produces proper classifications on synthetic plans, in this case with 1 removed, 1 unchanged file.
    """
    common_time = time.time()
    old_index = mock_index(['permanent_file.txt', 'temporary_file.txt'], [
                           common_time, common_time])
    new_index = mock_index(['permanent_file.txt'], [common_time])

    diff_work = search.status.diff_work_between_plans(old_index, new_index)

    assert_frame_equal(
        diff_work['deleted_files'],
        pd.DataFrame({
            'fname': ['temporary_file.txt'],
            'last_mod_old': [common_time],
            'last_mod_new': [np.nan],  # float
            'strategy_new': [None],  # object
            'strategy_old': ['MyImporter'],
            'strategy_version_new': [np.nan],  # float
            'strategy_version_old': [1.0],
            '_merge': pd.Series(
                ['left_only'],
                dtype=pd.api.types.CategoricalDtype(
                    categories=['left_only', 'right_only', 'both'], ordered=False)
            )
        }).set_index('fname')[diff_plan_expected_column_order]
    )

    assert empty_diffplan(diff_work['new_files'])
    assert empty_diffplan(diff_work['updated_files'])
    assert empty_diffplan(diff_work['diff_strategy'])
    assert empty_diffplan(diff_work['newer_strategy'])

    assert_frame_equal(
        diff_work['unchanged'],
        pd.DataFrame({
            'fname': ['permanent_file.txt'],
            'last_mod_old': [common_time],
            'last_mod_new': [common_time],
            'strategy_old': ['MyImporter'],
            'strategy_new': ['MyImporter'],
            'strategy_version_old': [1.0],
            'strategy_version_new': [1.0],
            '_merge': pd.Series(
                ['both'],
                dtype=pd.api.types.CategoricalDtype(
                    categories=['left_only', 'right_only', 'both'], ordered=False)
            )
        }).set_index('fname')[diff_plan_expected_column_order]
    )

def test_diff_work_updated_files(mock_index):
    """
    Confirm diff_work_between_plans produces proper classifications on synthetic plans, in this case with an updated file.
    """
    common_time = time.time()
    old_index = mock_index(['file.txt'], [common_time - 1000])
    new_index = mock_index(['file.txt'], [common_time])

    diff_work = search.status.diff_work_between_plans(old_index, new_index)

    assert_frame_equal(
        diff_work['updated_files'],
        pd.DataFrame({
            'fname': ['file.txt'],
            'last_mod_old': [common_time - 1000],
            'last_mod_new': [common_time],
            'strategy_new': ['MyImporter'],
            'strategy_old': ['MyImporter'],
            'strategy_version_new': [1.0],
            'strategy_version_old': [1.0],
            '_merge': pd.Series(
                ['both'],
                dtype=pd.api.types.CategoricalDtype(
                    categories=['left_only', 'right_only', 'both'], ordered=False)
            )
        }).set_index('fname')[diff_plan_expected_column_order]
    )

    assert empty_diffplan(diff_work['new_files'])
    assert empty_diffplan(diff_work['deleted_files'])
    assert empty_diffplan(diff_work['diff_strategy'])
    assert empty_diffplan(diff_work['newer_strategy'])
    assert empty_diffplan(diff_work['unchanged'])


# TODO: test diff strategy, newer strategy
