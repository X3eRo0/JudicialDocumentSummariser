import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
import pdftotext

NLP = spacy.load('en_core_web_sm')

stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

def stem_tokens(tokens):
    return [stemmer.stem(item) for item in tokens]

'''remove punctuation, lowercase, stem'''
def normalize(text):
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))

vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')

def cosine_sim(text1, text2):
    tfidf = vectorizer.fit_transform([text1, text2])
    return ((tfidf * tfidf.T).A)[0,1]


def getPDFText2(filename):
    with open(filename, "rb") as file:
        pdf = pdftotext.PDF(file)
        file.close()
    data = ""
    for page in pdf:
        data += page
    return data

def GetSimilarity(file1, file2):
    doc1 = getPDFText2(file1)
    doc2 = getPDFText2(file2)
    return cosine_sim(doc1, doc2)
