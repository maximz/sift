import pandas as pd
import index_manager
from pathlib import Path
from importers.registry import IMPORTER_REGISTRY

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

def plan_work(index_loc, strategies):
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
        df = pd.DataFrame.from_records(
            file_list(index_loc, extension),
            index='fname'
        )
        df['strategy'] = strategy.__name__
        df['strategy_version'] = strategy.version
        return df
    return pd.concat([make_plan_per_extension(extension, strategy) for extension, strategy in strategies.items()])

def diff_work(last_index_details, new_plan):
    """
    Compares new plan to index this directory from scratch against the last plan that was executed.
    Returns:
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
    return {
        'new_files': df.loc[df['_merge'] == 'right_only'],
        'deleted_files': df.loc[df['_merge'] == 'left_only'],
        'updated_files': df.loc[(df['_merge'] == 'both') & (
            df['last_mod_new'] > df['last_mod_old'])],
        'diff_strategy': df.loc[(df['_merge'] == 'both') & (
            df['strategy_new'] != df['strategy_old'])],
        'newer_strategy': df.loc[(df['_merge'] == 'both') & (
            df['strategy_version_new'] > df['strategy_version_old']) & (
            df['strategy_new'] == df['strategy_old'])]
    }

def format_status(work_plan):
    """
    Pretty-print a plan to update last index.
    """
    def get_file_names(diff_plan):
        return '\n'.join(diff_plan.index.values)

    return """
New:
{new_files}

Deleted:
{deleted_files}

Updated:
{updated_files}

New importer available:
{diff_strategy}

Updated importer available:
{newer_strategy}
""".format(
        new_files=get_file_names(work_plan.new_files),
        deleted_files=get_file_names(work_plan.deleted_files),
        updated_files=get_file_names(work_plan.updated_files),
        diff_strategy=get_file_names(work_plan.diff_strategy),
        newer_strategy=get_file_names(work_plan.newer_strategy),
    )

def status(index_loc):
    assert index_manager.index_exists(index_loc)
    return diff_work(
        index_manager.last_index_details(index_loc),
        plan_work(index_loc, IMPORTER_REGISTRY)
    )
