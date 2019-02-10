import pandas as pd
from . import index_manager
from pathlib import Path
from .importers.registry import IMPORTER_REGISTRY

"""
These methods are responsible for checking status of current index and formulating work plan to update current index with changed files.
"""

def file_list(base_path, extension):
    """
    Get file attributes on paths matching this extension that are confirmed to be files.
    Returns list of { fname: "filename", last_mod: "last modified time as unix timestamp" } dictionaries
    """
    all_files_with_extension = Path(base_path).glob('**/*.%s' % extension)
    confirm_is_file = lambda path: path.is_file()
    def get_file_attributes(path):
        return {
            'fname': str(path),
            'last_mod': path.stat().st_mtime  # unix timestamp
        }

    # full list all_files_with_extension --> filter by confirm_is_file --> apply map get_file_attributes
    return list(map(
        get_file_attributes,
        filter(
            confirm_is_file,
            all_files_with_extension
        )
    ))

def make_plan_from_scratch(index_loc, strategies):
    """
    Plan how to index this directory from scratch.
    Arguments:
        - index_loc: directory to analyze
        - strategies: dict mapping file extensions to their Importer strategies
    Returns: pandas dataframe with columns:
        - relative path to file (index)
        - last modified time (as unix timestamp)
        - importer strategy name
        - importer strategy version
    """
    def make_plan_per_extension(extension, strategy):
        files = file_list(index_loc, extension)
        if len(files) == 0:
            # return empty frame with correct types
            return pd.DataFrame({
                'fname': pd.Series(dtype='str'),
                'last_mod': pd.Series(dtype='float'),
                'strategy': pd.Series(dtype='str'),
                'strategy_version': pd.Series(dtype='float'),
            }).set_index('fname')
        df = pd.DataFrame.from_records(
            files,
            index='fname' # requires files to be non-empty
        )
        df['strategy'] = strategy.__name__
        df['strategy_version'] = strategy.version
        return df
    return pd.concat([make_plan_per_extension(extension, strategy) for extension, strategy in strategies.items()])

def diff_work_between_plans(last_index_details, new_plan):
    """
    Compares new plan to index this directory from scratch against the last plan that was executed.
    Returns list of changes that, if applied to last_index_details, would transform it into new_plan:
        - new files
        - removed files
        - files with newer date modified
        - files with different strategy
        - files with same strategy but different strategy version

    Not handled: files with older date modified
    """
    df = pd.merge(
        last_index_details,
        new_plan,
        left_index=True,
        right_index=True,
        how='outer',
        suffixes=('_old', '_new'),
        indicator=True
    )
    rollups = {
        'new_files': df.loc[df['_merge'] == 'right_only'],
        'deleted_files': df.loc[df['_merge'] == 'left_only'],
        'updated_files': df.loc[(df['_merge'] == 'both') & (
            df['last_mod_new'] > df['last_mod_old'])],
        'diff_strategy': df.loc[(df['_merge'] == 'both') & (
            df['strategy_new'] != df['strategy_old'])],
        'newer_strategy': df.loc[(df['_merge'] == 'both') & (
            df['strategy_version_new'] > df['strategy_version_old']) & (
            df['strategy_new'] == df['strategy_old'])],
        'unchanged': df.loc[(df['_merge'] == 'both') & (
            df['last_mod_new'] == df['last_mod_old']) & (
            df['strategy_version_new'] == df['strategy_version_old']) & (
            df['strategy_new'] == df['strategy_old'])]
    }
    assert sum([value.shape[0] for key,value in rollups.items()]) == df.shape[0]
    return rollups

def format_status(work_plan):
    """
    Pretty-print a plan to update last index.
    """
    headers_and_data = [
        ("New", work_plan['new_files']),
        ("Deleted", work_plan['deleted_files']),
        ("Updated", work_plan['updated_files']),
        ("New importer available", work_plan['diff_strategy']),
        ("Updated importer available", work_plan['newer_strategy']),
        # ("Unchanged", work_plan['unchanged']), # debug only
    ]
    section_separator = '\n'
    def make_section(header, data):
        def get_file_names(diff_plan):
            return '\n'.join(diff_plan.index.values)

        if len(data) == 0:
            return None

        return "{header}:\n{filenames}".format(
            header=header,
            filenames=get_file_names(data)
        )

    section_outputs = [make_section(header, data)
                       for (header, data) in headers_and_data]
    return section_separator.join(filter(lambda s: s != None, section_outputs))

def status(index_loc):
    assert index_manager.index_exists(index_loc), "Index doesn't exist."
    return diff_work_between_plans(
        index_manager.last_index_details(index_loc),
        make_plan_from_scratch(index_loc, IMPORTER_REGISTRY)
    )
