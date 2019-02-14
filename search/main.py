import argparse
from . import status, metadata_manager, update, lucene_manager

def main():
    parser = argparse.ArgumentParser(prog='searchtool', description="Index a file tree and search it.")
    parser.add_argument('--path', help='Index path', default='.')

    subparsers = parser.add_subparsers()

    init_parser = subparsers.add_parser('init', help='Init index')
    init_parser.set_defaults(func=init_index)

    status_parser = subparsers.add_parser('status', help='Status of index')
    status_parser.set_defaults(func=get_status)

    update_parser = subparsers.add_parser('update', help='Update index')
    update_parser.add_argument('--delete-missing', dest='delete_missing', help='Delete files that no longer exist', action='store_true')
    update_parser.set_defaults(func=update_index)

    query_parser = subparsers.add_parser('query', aliases=['q'], help='Query index')
    query_parser.set_defaults(func=run_query)
    query_parser.add_argument('terms', metavar='term',
                              type=str, nargs='+', help='Search query terms')

    args = parser.parse_args()
    if 'func' not in args:
        # we fell through all the subparsers
        parser.print_help()
        return
    args.func(args)

def init_index(args):
    metadata_manager.create_index(args.path)
    print("Index created")

def get_status(args):
    computed_status = status.status(args.path)
    pretty_print_status = status.format_status(computed_status)
    if pretty_print_status != '':
        # be silent (not even a newline) unless we have status to report
        print(pretty_print_status)
    return computed_status

def update_index(args):
    index_loc = args.path
    work_plan = status.status(index_loc)
    formatted_status = status.format_status(work_plan)
    if formatted_status == '':
        print('Nothing to update.')
        return
    with lucene_manager.LuceneManager(index_loc) as index_manager:
        update.update(index_loc, index_manager, work_plan, delete=args.delete_missing, verbose=True)

def run_query(args):
    query = ' '.join(args.terms)
    print('query: %s' % query)
    with lucene_manager.LuceneManager(args.path) as index_manager:
        results = list(index_manager.search(query))
        pretty_printed = [lucene_manager.format_document(r) for r in results]
        print('\n'.join(pretty_printed))
        return results


if __name__ == '__main__':
    main()
