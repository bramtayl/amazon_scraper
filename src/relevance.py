# build pylucene first
# I used oracle JDK 17
# importing lucene enables a bunch of other imports
import lucene

from bs4 import BeautifulSoup
from java.nio.file import Paths
from os import path
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, StringField, TextField
from org.apache.lucene.index import DirectoryReader, IndexWriter, IndexWriterConfig
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.store import NIOFSDirectory
from pandas import concat, DataFrame


def index_product_pages(lucene_folder, product_pages_folder, product_ids):
    writer = IndexWriter(
        NIOFSDirectory(Paths.get(lucene_folder)), IndexWriterConfig(StandardAnalyzer())
    )
    for product_id in product_ids:
        product_file = path.join(product_pages_folder, product_id + ".html")
        if path.isfile(product_file):
            print(product_id)
            doc = Document()
            doc.add(Field("product_id", product_id, StringField.TYPE_STORED))
            with open(product_file, "r", encoding="UTF-8") as io:
                doc.add(
                    Field(
                        "product_text",
                        BeautifulSoup(io, "lxml", from_encoding="UTF-8").text,
                        TextField.TYPE_STORED,
                    )
                )
            writer.addDocument(doc)
    writer.commit()
    writer.close()


def get_relevance_data(lucene_folder, queries):
    searcher = IndexSearcher(
        DirectoryReader.open(NIOFSDirectory(Paths.get(lucene_folder)))
    )
    parser = QueryParser("product_text", StandardAnalyzer())
    parser.setDefaultOperator(QueryParser.Operator.AND)

    results = []
    for query in queries:
        print(query)
        for score_data in searcher.search(parser.parse(query), 100).scoreDocs:
            results.append(
                DataFrame(
                    {
                        "query": query,
                        "product_id": searcher.doc(score_data.doc)["product_id"],
                        "score": score_data.score,
                    },
                    index=[0],
                )
            )

    del searcher
    return concat(results, ignore_index=True)