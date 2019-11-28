import logging

from gensim.models import Word2Vec

#from corenlp import StanfordCoreNLP

#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
import jieba

if __name__ == '__main__':
    rooot = 'D:\\DeepLearning\\comment\\opinion_mining\\datasets\\'
    with open(rooot+'stopwords.txt', 'r',encoding='utf-8') as f:
        stopwords = set(map(lambda data: data.strip(), f.readlines()))
    with open(rooot+'training_data.txt', 'r',encoding='utf-8') as f:
        comments = map(lambda comment: comment.strip(), f.readlines())
        
    #nlp = StanfordCoreNLP('http://localhost:9000')

    segments = []
    for comment in comments:
        #output = nlp.annotate(comment, properties={'annotators': 'ssplit', 'outputFormat': 'json'})
        tok = jieba.lcut(comment)
        tokens=[]
        for i in tok:
            if(i not in stopwords):
                tokens.append(i)
        segments.append(tokens)

    model = Word2Vec(segments, min_count=3, size=50, window=3)
    model.wv.save_word2vec_format(rooot+"vectors.txt", binary=False)
