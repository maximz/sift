import argparse
import status, index_manager

def main():
    parser = argparse.ArgumentParser(prog='searchtool', description="Index a file tree and search it.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--init', action='store_true', help='Init index')
    group.add_argument('--status', action='store_true', help='Status of index')
    group.add_argument('--update', action='store_true', help='Update index')
    group.add_argument('query', metavar='term', type=str, nargs='+', help='Search query word')
    args = parser.parse_args()

    if args.init:
        init_index()
    elif args.status:
        get_status()
    elif args.update():
        print('updating index..')
    else:
        print('query: %s' % ' '.join(args.query))

def init_index():
    index_manager.create_index('.')
    print("Index created")

def get_status():
    print(status.format_status(status.status('.')))

if __name__ == '__main__':
    main()
