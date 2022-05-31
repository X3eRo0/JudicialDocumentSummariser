from sumy.summarizers.lsa import LsaSummarizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import pdftotext

def getPDFText2(filename):
    with open(filename, "rb") as file:
        pdf = pdftotext.PDF(file)
        file.close()
    data = ""
    for page in pdf:
        data += page
    return data

def GetLsaSummary(filename, nsentences):
    data = getPDFText2(filename)
    parser = PlaintextParser.from_string(data, Tokenizer("english"))
    stemmer = Stemmer("english")
    summarizer = LsaSummarizer(stemmer)
    summarizer.stop_words = get_stop_words("english")
    text = [a._text for a in summarizer(parser.document, nsentences)]
    return text
