# from pylucene samples
import os
import lucene
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType, TextField, LongPoint, StoredField, StringField
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexReader, IndexWriterConfig, IndexOptions, DirectoryReader, Term
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher, TermQuery, BooleanQuery, BooleanClause
from org.apache.lucene.queryparser.classic import QueryParser, MultiFieldQueryParser


class LuceneManager(object):

    def init(self, indexPath):
        lucene.initVM(vmargs=['-Djava.awt.headless=true'])
        if not os.path.exists(indexPath):
            os.mkdir(indexPath)
        store = SimpleFSDirectory(Paths.get(indexPath))
        self.analyzer = StandardAnalyzer()
        config = IndexWriterConfig(self.analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE_OR_APPEND)
        # IndexWriter
        self.writer = IndexWriter(store, config)
        # IndexReader
        self.reader = DirectoryReader.open(store) # plays well with IndexWriter
        # IndexSearcher
        self.searcher = IndexSearcher(self.reader)

    def insert(self, key, document):
        self.writer.addDocument(document)

    def delete(self, key):
        self.writer.deleteDocuments(Term('fullpath', key))

    def update(self, key, document):
        # atomic delete and add
        self.writer.updateDocument(Term('fullpath', key), document)

    def exists(self, key):
        termQuery = TermQuery(Term("fullpath", key))
        booleanQuery = BooleanQuery()
        booleanQuery.add(termQuery, BooleanClause.Occur.MUST)
        results = self.searcher.search(booleanQuery, 1)
        return results.totalHits > 0

    def commit(self):
        self.writer.commit()
        # TODO: use DirectoryReader.openIfChanged() to make IndexReader reflect index updates
        # IndexReader.isCurrent() may help there.

    def search(self, terms, n_hits=50):
        # build query
        parser = MultiFieldQueryParser(['text', 'title'], self.analyzer)
        #parser.setDefaultOperator(QueryParser.Operator.AND) # defaults to OR unless terms have modifier
        query = parser.parse(terms)
        # execute search for top N hits
        for result in self.searcher.search(query, n_hits).scoreDocs:
            docid = result.doc  # this is not a stable identifier
            doc = self.searcher.doc(docid)  # obtain document through an IndexReader
            # doc.getFields() -> field.name(), field.stringValue()
            # TODO: highlighter to extract relevant part of body
            yield {
                'filename': doc['filename'],
                'fullpath': doc['fullpath'],
                'date': doc['date_stored'],
                'score': result.score
            }

    def close(self):
        self.writer.optimize()
        self.writer.close()
        self.reader.close()
        self.searcher.close()

    def make_document(self, full_path, filename, unix_timestamp, contents):
        doc = Document()
        # two separate date fields per recommendation
        # at https://lucene.apache.org/core/7_6_0/core/org/apache/lucene/document/DateTools.html
        doc.add(LongPoint('date_for_pointrangequery', unix_timestamp))
        doc.add(StoredField('date_stored', unix_timestamp))
        # https://lucene.apache.org/core/7_6_0/core/org/apache/lucene/document/StringField.html
        # indexed but not tokenized
        doc.add(StringField('filename', filename, Field.Store.YES))
        doc.add(StringField('fullpath', full_path, Field.Store.YES)) # this is file key
        # https://lucene.apache.org/core/7_6_0/core/org/apache/lucene/document/TextField.html
        # indexed and tokenized
        doc.add(TextField('body', contents, Field.Store.NO))
        return doc
