"""
using high-level interfaces from main.py
"""

import search.main, search.metadata_manager
import argparse
from pytest import fixture
from pandas.testing import assert_frame_equal
from pathlib import Path


@fixture
def args(datadir):
    return argparse.Namespace(path=str(datadir), delete_missing=False)

@fixture
def search_args(datadir):
    def _search_args(terms):
        return argparse.Namespace(path=str(datadir), delete_missing=False, terms=terms)
    return _search_args

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

    # sanity check: confirm the index is as of yet empty
    assert search.metadata_manager.last_index_details(args.path).shape[0] == 0

    search.main.update_index(args)
    status_one = search.main.get_status(args)
    search.main.update_index(args)
    status_two = search.main.get_status(args)
    # status objects are dicts holding dataframes
    for key in status_one.keys():
        assert_frame_equal(status_one[key], status_two[key])

def test_queries(prep_index, args, search_args):
    """
    init --> status --> update --> query for expected terms
    """
    search.main.get_status(args)
    search.main.update_index(args)
    # expect 1 result
    assert len(search.main.run_query(search_args(['apple']))) == 1

    # OR or AND should work, expect 1 result
    assert len(search.main.run_query(search_args(['apple', 'banana']))) == 1

    # only OR should work, expect 1 result
    assert len(search.main.run_query(search_args(['apple', 'blackberry']))) == 1

    # only OR should work, expect 2 results
    assert len(search.main.run_query(search_args(['apple', 'apricot']))) == 2


def test_repeated_index_new_files(prep_index, args, datadir):
    """
    init --> update --> add new file --> update; should not throw errors
    """
    # sanity check: confirm the index is as of yet empty
    assert search.metadata_manager.last_index_details(args.path).shape[0] == 0

    search.main.update_index(args)

    # add new file
    Path(str(datadir)).joinpath('test10.md').touch()

    search.main.update_index(args)
