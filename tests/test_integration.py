"""
using high-level interfaces from main.py
"""

import search.main
import argparse
from pytest import fixture
from pandas.testing import assert_frame_equal


@fixture
def args(datadir):
    return argparse.Namespace(path=str(datadir), delete_missing=False)

@fixture
def prep_index(args):
    search.main.init_index(args)

@fixture(autouse=True)  # will run automatically before each test
def reset(prep_index):
    # remove index?
    pass

def test_repeated_reindex(prep_index, args):
    """
    init --> status --> update --> status --> update --> status
    2nd and 3rd status should match
    """
    status_orig = search.main.get_status(args)
    search.main.update_index(args)
    status_one = search.main.get_status(args)
    search.main.update_index(args)
    status_two = search.main.get_status(args)
    # status objects are dicts holding dataframes
    for key in status_one.keys():
        assert_frame_equal(status_one[key], status_two[key])

def test_queries(prep_index, args):
    """
    init --> status --> update --> query for expected terms
    """
    pass
