import sys
#sys.path.append('/root/Hangwei_BackEnd/')
#sys.path.append('/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/sentiment/')
#from analysis import sentiment
from generate_final import LtpTool
import time
from dbscan import DbscanClustering
import jieba
import pickle
taglist = ['辣子香','辣子真的香', '', '']
dbscan = DbscanClustering(stopwords_path='./library/stop_words.txt')
result = dbscan.dbscan(taglist, eps=0.1, min_samples=2)
result