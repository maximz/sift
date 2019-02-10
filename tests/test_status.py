import search.status
import time
import pytest
import pandas as pd
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


def test_make_plan_from_scratch(mocker, filetype_strategies):
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
        pd.DataFrame({
            'fname': ['test.txt', 'test.md'],
            'last_mod': [common_time, common_time],
            'strategy': ['TextImporter', 'MarkdownImporter'],
            'strategy_version': [1.0, 3.0],
        }).set_index('fname')
    )
