from search.lucene_manager import LuceneManager, assert_document_equals, format_document, make_document
from pytest import fixture
import time

@fixture
def manager(datadir):
    with LuceneManager(index_root_loc=str(datadir)) as mgr:
        yield mgr

@fixture
def document():
    return make_document('test/test2/test3.txt', time.time() - 10000, 'Sample contents of a document')

@fixture
def document_updated():
    return make_document('test/test2/test3.txt', time.time() + 10000, 'This is completely different')

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

def test_insert_query_by_filename(manager, document):
    """
    Insert a document, then query for the filename, and confirm the document matches with the right values returned.
    """
    manager.insert(document)
    manager.commit()
    assert manager.num_docs() == 1
    results = list(manager.search(document['fullpath']))
    # print('\n'.join([format_document(d) for d in manager.get_all_docs()]))
    assert len(results) == 1
    assert_document_equals(results[0], document)

def test_insert_query_by_body(manager, document):
    """
    Insert a document, then query for the body, and confirm the document matches with the right values returned.
    """
    manager.insert(document)
    manager.commit()
    assert manager.num_docs() == 1
    query_text = ' '.join(document['body'].split(' ')[:2])
    results = list(manager.search(query_text))
    assert len(results) == 1
    assert_document_equals(results[0], document)

def test_update_document(manager, document, document_updated):
    """
    Insert a document, then update it, and confirm it was updated in index.
    """
    manager.insert(document)
    manager.commit()
    manager.update(document['key'], document_updated)
    manager.commit()
    assert document['key'] == document_updated['key'], 'sanity check'
    assert manager.exists(document['key'])
    assert manager.num_docs() == 1
    results = list(manager.search(document_updated['body']))
    assert len(results) == 1
    assert_document_equals(results[0], document_updated)

def test_insert_delete_notexist(manager, document):
    """
    Insert a document, then delete, then confirm it does not exist.
    """
    manager.insert(document)
    manager.commit()
    manager.delete(document['key'])
    manager.commit()
    assert not manager.exists(document['key'])
    assert manager.num_docs() == 0

def test_analyzer(manager):
    """
    Declare expected behavior of the Lucene tokenization process.
    """
    tokens = manager.debug_analyzer('file/path/test/test5.txt')
    assert tokens == ['file', 'path', 'test', 'test5', 'txt'], tokens

    tokens = manager.debug_analyzer('test_File-More1.tar.gz')
    assert tokens == ['test_file', 'more1', 'tar.gz'], tokens
