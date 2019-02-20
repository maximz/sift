"""
using high-level interfaces from main.py
"""

import sift.main, sift.metadata_manager
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
    sift.main.init_index(args)

@fixture(autouse=True)  # will run automatically before each test
def reset(prep_index):
    # remove index?
    pass

def test_repeated_reindex(prep_index, args):
    """
    init --> status --> update --> status --> update --> status
    2nd and 3rd status should match
    """
    status_orig = sift.main.get_status(args)

    # sanity check: confirm the index is as of yet empty
    assert sift.metadata_manager.last_index_details(args.path).shape[0] == 0

    sift.main.update_index(args)
    status_one = sift.main.get_status(args)
    sift.main.update_index(args)
    status_two = sift.main.get_status(args)
    # status objects are dicts holding dataframes
    for key in status_one.keys():
        assert_frame_equal(status_one[key], status_two[key])

def test_queries(prep_index, args, search_args):
    """
    init --> status --> update --> query for expected terms
    """
    sift.main.get_status(args)
    sift.main.update_index(args)
    # expect 1 result
    assert len(sift.main.run_query(search_args(['apple']))) == 1

    # OR or AND should work, expect 1 result
    assert len(sift.main.run_query(search_args(['apple', 'banana']))) == 1

    # only OR should work, expect 1 result
    assert len(sift.main.run_query(search_args(['apple', 'blackberry']))) == 1

    # only OR should work, expect 2 results
    assert len(sift.main.run_query(search_args(['apple', 'apricot']))) == 2


def test_repeated_index_new_files(prep_index, args, datadir):
    """
    init --> update --> add new file --> update; should not throw errors
    """
    # sanity check: confirm the index is as of yet empty
    assert sift.metadata_manager.last_index_details(args.path).shape[0] == 0

    sift.main.update_index(args)

    # add new file
    Path(str(datadir)).joinpath('test10.md').touch()

    sift.main.update_index(args)
