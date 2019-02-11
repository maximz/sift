from search.lucene_manager import LuceneManager, assert_document_equals, format_document
from pytest import fixture
import time

@fixture
def manager(datadir):
    # set up
    index_path = str(datadir.join('.searchindex/'))
    mgr = LuceneManager(index_path)
    # use in tests
    yield mgr
    # clean up
    mgr.close()

@fixture
def document(manager):
    return manager.make_document('test/test2/test3.txt', 'test3.txt', time.time() - 10000, 'Sample contents of a document')

@fixture(autouse=True) # will run automatically before each test
def reset(manager):
    manager.delete_all()
    manager.commit()

def test_insert_exists(manager, document):
    """
    Insert a document, then confirm it exists.
    """
    manager.insert(document)
    manager.commit()
    assert manager.exists(document['key'])
    assert manager.num_docs() == 1

def test_insert_before_commit_no_exists(manager, document):
    """
    Insert a document WITHOUT commiting it. Confirm it doesn't exist.
    """
    manager.insert(document)
    assert not manager.exists(document['key'])

def test_reset_fixture(manager):
    """
    Make sure the reset fixture is properly removing all documents between consecutive tests.
    """
    assert manager.num_docs() == 0

def test_insert_query(manager, document):
    """
    Insert a document, then confirm query returns the right values.
    """
    manager.insert(document)
    manager.commit()
    assert manager.num_docs() == 1
    results = list(manager.search(document['filename']))
    print('\n'.join([format_document(d) for d in manager.get_all_docs()]))
    print(document['filename'])
    assert len(results) == 1
    assert_document_equals(results[0], document)


# insert and then query by body.
# update. then query. make sure updated.
# insert. delete. then not exists.

def test_analyzer(manager):
    """
    Declare expected behavior of the Lucene tokenization process.
    """
    tokens = manager.debug_analyzer('file/path/test5.txt')
    assert tokens == ['file', 'path', 'test5', 'txt'], tokens

    tokens = manager.debug_analyzer('test_File-More1.tar.gz')
    assert tokens == ['test_file', 'more1', 'tar.gz'], tokens
