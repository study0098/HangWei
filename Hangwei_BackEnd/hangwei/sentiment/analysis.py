import pandas as pd
import jieba 
from sklearn.externals import joblib
from classifier import SVMClassifier
def fenci(train_data):
    words_df = train_data.apply(lambda x:' '.join(jieba.cut(x)))
    return words_df
def sentiment(strings,num):
    classify = SVMClassifier('/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/sentiment/data.csv',num,'positive_prob','items')
    classify.load_model()
    return classify.classify(strings)
    if(senti>0.53):
        return 1
    else:
        return 0
def analysis(path):
    text = pd.read_csv(path+'text.csv')
    r,c = text.shape
    for i in range(5):
        text.iloc[i,1] = str(sentiment(str(text.iloc[i,0]),90))
    text.to_csv(path+'sentiment.csv')
    #print("hello")