import numpy as np
from .splitt import split_into_sentences

import pdftotext

def getPDFText2(filename):
    with open(filename, "rb") as file:
        pdf = pdftotext.PDF(file)
        file.close()
    data = ""
    for page in pdf:
        data += page
    return data

def GetTextRankSummary(file, nsentences):
    data = getPDFText2(file)
    data = split_into_sentences(data)

    rank = {}
    for count, sent in enumerate(data):
        rank[sent] = count

    sentences = data
    clean_sentences = []
    for s in range(len(sentences)):
        temp = ''
        for char in sentences[s]:
            if not (char.isalnum() or char == ' '):
                temp += ''
            else:
                temp += char
        clean_sentences.append(temp)
    clean_sentences = [sent.lower() for sent in clean_sentences]
    from nltk.corpus import stopwords
    stop_words = stopwords.words('english')

    # function to remove stopwords
    def remove_stopwords(sen):
        sen_new = " ".join([i for i in sen if i not in stop_words])
        return sen_new

    # remove stopwords from the sentences
    clean_sentences = [remove_stopwords(r.split()) for r in clean_sentences]

    word_embeddings = {}
    f = open('./vectors.txt', encoding='utf-8')
    for line in f:
        values = line.split()
        word = values[0]
        coefs = np.asarray(values[1:], dtype='float32')
        word_embeddings[word] = coefs
    f.close()

    sentence_vectors = []
    for i in clean_sentences:
        if len(i) != 0:
            v = sum([word_embeddings.get(w, np.zeros((50,))) for w in i.split()])/(len(i.split())+0.001)
        else:
            v = np.zeros((50,))
        sentence_vectors.append(v)

    similarity_matrix = np.zeros([len(sentences), len(sentences)])
    from sklearn.metrics.pairwise import cosine_similarity
    for i in range(len(sentences)):
        for j in range(len(sentences)):
            if i != j:
                similarity_matrix[i][j] = cosine_similarity(sentence_vectors[i].reshape(1,50), sentence_vectors[j].reshape(1,50))[0,0]
    import networkx as nx

    nx_graph = nx.from_numpy_array(similarity_matrix)
    scores = nx.pagerank(nx_graph)

    ranked_sentences = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)
    ordered_sents = sorted(ranked_sentences[:nsentences], key = lambda x: rank[x[1]])
    return [sent[1] for sent in ordered_sents]
