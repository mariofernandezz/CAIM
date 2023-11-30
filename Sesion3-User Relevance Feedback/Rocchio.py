from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

import argparse
import numpy as np
import operator

from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q
from elasticsearch.client import CatClient


def document_term_vector(client, index, id):
    """
    Returns the term vector of a document and its statistics a two sorted list of pairs (word, count)
    The first one is the frequency of the term in the document, the second one is the number of documents
    that contain the term

    :param client:
    :param index:
    :param id:
    :return:
    """
    termvector = client.termvectors(index=index, id=id, fields=['text'],
                                    positions=False, term_statistics=True)

    file_td = {}
    file_df = {}

    if 'text' in termvector['term_vectors']:
        for t in termvector['term_vectors']['text']['terms']:
            file_td[t] = termvector['term_vectors']['text']['terms'][t]['term_freq']
            file_df[t] = termvector['term_vectors']['text']['terms'][t]['doc_freq']
    return sorted(file_td.items()), sorted(file_df.items())


def toTFIDF(client, index, file_id):
    """
    Returns the term weights of a document

    :param file:
    :return:
    """

    # Get the frequency of the term in the document, and the number of documents
    # that contain the term
    file_tv, file_df = document_term_vector(client, index, file_id)

    max_freq = max([f for _, f in file_tv])

    dcount = doc_count(client, index)

    tfidfw = {}
    for (t, w),(_, df) in zip(file_tv, file_df):
        # codigo implementando tfidf, ahora usamos diccionario
        tf = w/max_freq
        idf = np.log2(dcount/df)
        tfidfw[t] = tf*idf
    return tfidfw


def doc_count(client, index):
    """
    Returns the number of documents in an index

    :param client:
    :param index:
    :return:
    """
    return int(CatClient(client).count(index=[index], format='json')[0]['count'])


def queryToDict(query):
    dict = {}
    for t in query:
        if '^' in t:
            term, weight = t.split('^')
            weight = float(weight)
        else:
            term = t
            weight = 1.0
        dict[term] = weight
    return dict

def dictToQuery(dict):
    query = []
    for (term, weight) in dict:
        query.append(term + '^' + str(weight))
    return query


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, help='Index to search')
    parser.add_argument('--nrounds', type=int, help='Number of application of Rocchio Rule')
    parser.add_argument('--k', type=int, help='Number of relevant documents')
    parser.add_argument('--r', type=int, help='Number of relevant terms to keep')    
    parser.add_argument('--query', default=None, nargs=argparse.REMAINDER, help='List of words to search')

    args = parser.parse_args()

    # Argumentos introducidos
    index = args.index
    nrounds = args.nrounds
    rel = args.r
    k = args.k
    query = args.query
    print(query)

    # Valores de aplha y beta
    alpha = 2
    beta = 1

    try:
        client = Elasticsearch()
        s = Search(using=client, index=index)
        if query is not None:
            # se hacen tantas rounds como nrounds 
            for round in range(0, nrounds):
                q = Q('query_string',query=query[0])
                for i in range(1, len(query)):
                    q &= Q('query_string',query=query[i])
                s = s.query(q)
                response = s[0:k].execute()

                qDict = queryToDict(query)

                docs = {}
                print(f"{response.hits.total['value']} Documents")
                for re in response:
                    tfidf = toTFIDF(client, index, re.meta.id)
                    docs = {d: docs.get(d,0) + tfidf.get(d,0) for d in set(tfidf) | set(docs)}

                alphaD = {d: alpha*qDict.get(d, 0) for d in set(qDict)}
                betaD = {d: beta*docs.get(d, 0)/k for d in set(docs)}
                res = {d: betaD.get(d, 0) + alphaD.get(d, 0) for d in set(alphaD)|set(betaD)}
                
                result = sorted(res.items(), key= operator.itemgetter(1), reverse=True)                
                #print(rel)
                result = result[:rel]

                query = dictToQuery(result)
                print(query)

        else:
            print('No query parameters passed')

    except NotFoundError:
        print(f'Index {index} does not exists')