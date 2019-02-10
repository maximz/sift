from . import index_manager
import pandas as pd

def update(index_loc, work_plan, delete=False):
    """
    Execute a work plan from .status.status() to update index.
    """
    assert index_manager.index_exists(index_loc), "Index doesn't exist."

    # TODO: execute new_files, updated_files, new importer, updated importer, and maybe deletions

    # update our index metadata
    new_index_details = summarize_new_index_status(work_plan, delete)
    index_manager.save_index_details(new_index_details, index_loc)

def perform_single_file(f):
    pass

def summarize_new_index_status(work_plan, delete):
    """
    return new_files, updated_files, new importer, updated importer, and maybe deletions
    """
    choose_newer = ['new_files', 'updated_files', 'diff_strategy', 'newer_strategy', 'unchanged']
    all_dfs = pd.concat([work_plan[key] for key in choose_newer])
    all_dfs = all_dfs.drop(['last_mod_old', 'strategy_old',
                         'strategy_version_old'], axis=1)
    all_dfs = all_dfs.rename(columns={
        'last_mod_new': 'last_mod',
        'strategy_new': 'strategy',
        'strategy_version_new': 'strategy_version'
    })
    if not delete:
        # concat deleted files
        choose_older_df = work_plan['deleted_files'].copy()
        choose_older_df = choose_older_df.drop(['last_mod_new', 'strategy_new',
                      'strategy_version_new'], axis=1)
        choose_older_df = choose_older_df.rename(columns={
            'last_mod_old': 'last_mod',
            'strategy_old': 'strategy',
            'strategy_version_old': 'strategy_version'
        })
        all_dfs = pd.concat([all_dfs, choose_older_df])
    return all_dfs.drop(['_merge'], axis=1)
