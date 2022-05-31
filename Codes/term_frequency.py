import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import string
from .splitt import split_into_sentences
from nltk.stem import WordNetLemmatizer
import pdftotext
NLP = spacy.load('en_core_web_sm')

def getPDFText2(filename):
    with open(filename, "rb") as file:
        pdf = pdftotext.PDF(file)
        file.close()
    data = ""
    for page in pdf:
        data += page
    return data

def GetTermFrequencySummary(file, nsentences):
    data = getPDFText2(file)
    sentences = split_into_sentences(data)
    text = data

    doc = NLP(text)
    tokens = [token.text for token in doc]

    wordnet_lemmatizer = WordNetLemmatizer()
    tokens = [wordnet_lemmatizer.lemmatize(word, pos="v") for word in tokens]

    punctuation = string.punctuation + '\n'
    from collections import defaultdict
    word_frequencies = defaultdict(int)
    for word in tokens:
        new_word = word.lower()
        if new_word not in STOP_WORDS and new_word not in punctuation:
            word_frequencies[new_word] += 1
        
    max_freq = max(word_frequencies.values())
    for w in word_frequencies:
        word_frequencies[w] /= max_freq
        
    sentence_tokens = {}
    rank = 1
    for sent in sentences:
        sentence_tokens[sent] = rank
        rank += 1

    sentence_scores = defaultdict(int)
    n = len(sentence_tokens)

    for sent in sentence_tokens:
        for word in sent.split():
            sentence_scores[sent] += word_frequencies[word.lower()]

    from heapq import nlargest
    top_sentences = nlargest(nsentences, sentence_scores, key = sentence_scores.get)
    summary = sorted(top_sentences, key = sentence_tokens.get)
    return summary
