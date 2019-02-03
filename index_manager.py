"""
We manage the last index as a csv for now.
This is a bad idea
Expensive to read and write the full file every time
But for now convenient to just use pandas for some diffing operations.
"""

import pandas as pd
from pathlib import Path

DEFAULT_INDEX_STORE_FILENAME = '.searchindex.csv'

def get_index_metadata_path(index_loc, index_store_filename):
    return Path(index_loc).joinpath(index_store_filename)


def index_exists(index_loc, index_store_filename=DEFAULT_INDEX_STORE_FILENAME):
    return get_index_metadata_path(index_loc, index_store_filename).exists()


def create_index(index_loc, index_store_filename=DEFAULT_INDEX_STORE_FILENAME):
    assert not index_exists(
        index_loc, index_store_filename), 'Index already exists.'
    get_index_metadata_path(
        index_loc, index_store_filename).touch(exist_ok=False)

def last_index_details(index_loc, index_store_filename=DEFAULT_INDEX_STORE_FILENAME):
    """
    load last index management data
    """
    return pd.read_csv(get_index_metadata_path(index_loc, index_store_filename))

def update_file_data():
    """
    update a single file's data
    """
    pass

def save_index_details(new_index_details, index_loc, index_store_filename=DEFAULT_INDEX_STORE_FILENAME):
    """
    save updated index management data
    """
    new_index_details.to_csv(get_index_metadata_path(
        index_loc, index_store_filename))
