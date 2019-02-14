from . import metadata_manager
import pandas as pd
from .importers.registry import IMPORTER_REGISTRY
from .lucene_manager import make_document

def update(index_loc, index_manager, work_plan, delete=False, strategies=IMPORTER_REGISTRY, verbose=False):
    """
    Execute a work plan from .status.status() to update index.
    """
    assert metadata_manager.index_exists(index_loc), "Index doesn't exist."

    # execute new_files, updated_files, new importer, updated importer, and maybe deletions
    if delete:
        for fname, _, __ in extract_file_info(work_plan['deleted_files']):
            deleted_key = index_manager.delete(fname)
            if verbose:
                print('Deleted: %s' % deleted_key)
    if verbose:
        print('Missing objects removed from index.' if delete else 'Missing objects NOT removed from index.')

    for fname, extension, modified_time in extract_file_info(work_plan['new_files']):
        inserted_key = index_manager.insert(
            perform_single_file(strategies, extension, fname, modified_time)
        )
        if verbose:
            print('Inserted: %s' % inserted_key)

    for df_key in ['updated_files', 'diff_strategy', 'newer_strategy']:
        for fname, extension, modified_time in extract_file_info(work_plan[df_key]):
            updated_key = index_manager.update(
                fname,
                perform_single_file(strategies, extension, fname, modified_time)
            )
            if verbose:
                print('Updated: %s' % updated_key)

    # commit changes
    index_manager.commit()

    # update our index metadata
    new_index_details = summarize_new_index_status(work_plan, delete)
    metadata_manager.save_index_details(new_index_details, index_loc)


def extract_file_info(df):
    """
    Convenience generator over file names, file extensions, and file modified times from a work plan dataframe.
    """
    for fname, row in df[['extension_new', 'last_mod_new']].iterrows():  # fname is index
        yield (fname, row['extension_new'], row['last_mod_new'])

def perform_single_file(strategies, extension, file_path, modified_time):
    """
    Launches and executes an importer strategy. Then transforms into a lucene document.
    """
    importer_strategy = strategies[extension]() # instantiate
    contents = importer_strategy.run(file_path)
    return make_document(file_path, modified_time, contents)

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
