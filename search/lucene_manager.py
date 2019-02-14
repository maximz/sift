# from pylucene samples
import os
import lucene
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType, TextField, LongPoint, StoredField, StringField
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexReader, IndexWriterConfig, IndexOptions, DirectoryReader, Term
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher, TermQuery, BooleanQuery, BooleanClause, MatchAllDocsQuery
from org.apache.lucene.queryparser.classic import QueryParser, MultiFieldQueryParser
from org.apache.lucene.analysis.tokenattributes import CharTermAttribute
from pathlib import Path

class LuceneManager(object):

    def __init__(self, index_root_loc, index_subdir_name='.searchindex'):
        self.index_root_loc = index_root_loc
        self.index_subdir_name = index_subdir_name

    def __enter__(self):
        """
        Used by "with" statement. Like an "open" / "init" method.
        """
        if lucene.getVMEnv() is None:
            lucene.initVM(vmargs=['-Djava.awt.headless=true'])
        index_path = str(Path(self.index_root_loc).joinpath('%s/' % self.index_subdir_name))
        if not os.path.exists(index_path):
            os.mkdir(index_path)
        store = SimpleFSDirectory(Paths.get(index_path))
        self.analyzer = StandardAnalyzer()
        config = IndexWriterConfig(self.analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE_OR_APPEND)
        # IndexWriter
        self.writer = IndexWriter(store, config)
        # IndexReader
        self.reader = DirectoryReader.open(self.writer)
        # IndexSearcher
        self.searcher = IndexSearcher(self.reader)

        return self

    def insert(self, document):
        self.writer.addDocument(document)
        return document['key']

    def delete(self, key):
        self.writer.deleteDocuments(Term('key', key))
        return key

    def delete_all(self):
        self.writer.deleteAll()

    def num_docs(self):
        return self.reader.numDocs()

    def update(self, key, document):
        # atomic delete and add
        self.writer.updateDocument(Term('key', key), document)
        return key

    def exists(self, key):
        boolean_query = BooleanQuery.Builder()
        boolean_query.add(TermQuery(Term('key', key)),
                          BooleanClause.Occur.MUST)
        results = self.searcher.search(boolean_query.build(), 1)
        return results.totalHits > 0

    def commit(self):
        self.writer.commit()
        # make IndexReader reflect index updates
        # TODO: try IndexReader.isCurrent()
        new_reader = DirectoryReader.openIfChanged(self.reader)
        if new_reader is not None:
            self.reader.close() # note: not thread safe, may need to revisit
            self.reader = new_reader
            self.searcher = IndexSearcher(self.reader)

    def process_search_result(self, result):
        docid = result.doc  # this is not a stable identifier
        # obtain document through an IndexReader
        doc = self.searcher.doc(docid)
        # doc.getFields() -> field.name(), field.stringValue()
        # TODO: highlighter to extract relevant part of body
        return {
            'fullpath': doc['fullpath'],
            'last_modified_time': doc['last_modified_time'],
            'score': result.score
        }


    def search(self, terms, n_hits=50):
        """
        Run search query.
        """
        # TODO: support date range queries

        # build query
        parser = MultiFieldQueryParser(['fullpath', 'body'], self.analyzer)
        #parser.setDefaultOperator(QueryParser.Operator.AND) # defaults to OR unless terms have modifier
        query = MultiFieldQueryParser.parse(parser, terms) # https://stackoverflow.com/a/26853987/130164
        # execute search for top N hits
        return [self.process_search_result(result) for result in self.searcher.search(query, n_hits).scoreDocs]

    def get_all_docs(self, n_hits=1000):
        # debug method
        return [self.process_search_result(result) for result in self.searcher.search(MatchAllDocsQuery(), n_hits).scoreDocs]


    def __exit__(self, type, value, traceback):
        """
        Used by the "with" statement. Handles close.
        TODO: error handling
        """
        self.writer.close()
        self.reader.close()


    def debug_analyzer(self, text):
        """
        Debug what StandardAnalyzer will give on this text.
        Ref: https://lucene.apache.org/core/7_6_0/core/org/apache/lucene/analysis/package-summary.html
        Ref: pylucene tests --> test_Analyzers.py, BaseTokenStreamTestCase.py
        """
        token_stream = self.analyzer.tokenStream('field', text)
        termAtt = token_stream.getAttribute(CharTermAttribute.class_)
        token_stream.reset()
        tokens = []
        while token_stream.incrementToken():
            #tokens.append(token_stream.reflectAsString(True))
            tokens.append(termAtt.toString())
        token_stream.end()
        token_stream.close()
        return tokens

def make_document(full_path, unix_timestamp, contents):
    """
    Create Lucene document with specific content.
    """
    doc = Document()
    # two separate date fields per recommendation
    # at https://lucene.apache.org/core/7_6_0/core/org/apache/lucene/document/DateTools.html
    doc.add(LongPoint('date_for_pointrangequery', int(unix_timestamp)))
    doc.add(StoredField('last_modified_time', int(unix_timestamp)))
    # https://lucene.apache.org/core/7_6_0/core/org/apache/lucene/document/TextField.html
    # indexed and tokenized
    doc.add(TextField('fullpath', full_path, Field.Store.YES)) # this is file key but tokenized
    doc.add(TextField('body', contents, Field.Store.NO))
    # It is also possible to add fields that are indexed but not tokenized.
    # See https://lucene.apache.org/core/7_6_0/core/org/apache/lucene/document/StringField.html
    # However there is a limitation: https://stackoverflow.com/a/32654329/130164
    # MultiFieldQueryParser will have bizarre results because the query parser runs the analyzer
    # , while StringField does not run the analyzer.
    # We deliberately store the key as untokenized so we can search by it directly with a TermQuery.
    doc.add(StringField('key', full_path, Field.Store.YES)) # this is file key
    return doc

def format_document(document):
    """
    pretty print
    """
    return """
Full path: {fullpath}
Timestamp: {last_modified_time}
""".format(fullpath=document['fullpath'], last_modified_time=document['last_modified_time'])

def assert_document_equals(document1, document2):
    assert document1['last_modified_time'] == document2['last_modified_time']
    assert document1['fullpath'] == document2['fullpath']
