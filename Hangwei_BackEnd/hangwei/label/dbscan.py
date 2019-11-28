import jieba
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA


class DbscanClustering():
    def __init__(self, stopwords_path=None):
        self.stopwords = self.load_stopwords(stopwords_path)
        self.vectorizer = CountVectorizer()
        self.transformer = TfidfTransformer()

    def load_stopwords(self, stopwords=None):
        if stopwords:
            with open(stopwords, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f]
        else:
            return []

    def preprocess_data(self, corpus_path):
        corpus = []
        with open(corpus_path, 'r', encoding='utf-8') as f:
            for line in f:
                corpus.append(' '.join([word for word in jieba.lcut(line.strip()) if word not in self.stopwords]))
        return corpus

    def get_text_tfidf_matrix(self, corpus):
        tfidf = self.transformer.fit_transform(self.vectorizer.fit_transform(corpus))
        weights = tfidf.toarray()
        return weights

    def pca(self, weights, n_components=2):
        pca = PCA(n_components=n_components)
        return pca.fit_transform(weights)

    def dbscan(self, corpus_path, eps=0.1, min_samples=3, fig=False):
        corpus = self.preprocess_data(corpus_path)
        weights = self.get_text_tfidf_matrix(corpus)

        pca_weights = self.pca(weights)

        clf = DBSCAN(eps=eps, min_samples=min_samples)

        y = clf.fit_predict(pca_weights)

        result = {}
        for text_idx, label_idx in enumerate(y):
            if label_idx not in result:
                result[label_idx] = [text_idx]
            else:
                result[label_idx].append(text_idx)
        return result


if __name__ == '__main__':
    dbscan = DbscanClustering(stopwords_path='./stop_words.txt')
    result = dbscan.dbscan('D:\\DeepLearning\\comment\\opinion_mining\\datasets\\test.txt', eps=0.1, min_samples=2)
    print(result)