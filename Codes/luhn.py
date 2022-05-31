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

def GetLuhnSummary(file, nsentences):
    data = getPDFText2(file)
    sentences = split_into_sentences(data)

    def top_words(sentences):
        record = {}
        for line in sentences:
            words = line.split()
            for word in words:
                w = word.strip('.!?,()\n').lower()
                if w in record:
                    record[w] += 1
                else:
                    record[w] = 1
        occur = [key for key in record.keys()]
        occur.sort(reverse=True, key=lambda x: record[x])
        return set(occur[:int(len(occur)/10)])

    def calculate_score(sentence, metric):
        words = sentence.split()
        imp_words, total_words, begin_unimp, end, begin = [0]*5
        for word in words:
            w = word.replace('.!?,();', ' ').lower()
            end += 1
            if w in metric:
                imp_words += 1
                begin = total_words
                end = 0
            total_words += 1
        unimportant = total_words - begin - end
        if(unimportant != 0):
            return float(imp_words**2) / float(unimportant)
        return 0.0

    def summarize(sentences, nsenteces):
        metric = top_words(sentences)
        scores = {}
        for sentence in sentences:
            scores[sentence] = calculate_score(sentence, metric)
        top_sentences = list(sentences)                                # make a copy
        top_sentences.sort(key=lambda x: scores[x], reverse=True)      # sort by score
        top_sentences = top_sentences[:nsentences] 
        top_sentences.sort(key=lambda x: sentences.index(x))           # sort by occurrence
        return top_sentences

    return summarize(sentences, nsentences)
