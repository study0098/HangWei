# -*- coding: utf-8 -*-
"""
Created on Sun Mar 31 15:10:44 2019

@author: xyttttt
"""

import sys
import gensim
import numpy as np
import jieba
from gensim.models.doc2vec import Doc2Vec, LabeledSentence
from sklearn.cluster import KMeans
sys.path.append('/root/Hangwei_BackEnd/')
sys.path.append('/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/fuzzymatch/')
from modelconnection import User_dish
from modelconnection import get_dish
from modelconnection import get_intro
from modelconnection import get_user
from modelconnection import get_dish_name
from modelconnection import get_dish_window
from modelconnection import get_dish_intro
from modelconnection import get_dishid
TaggededDocument = gensim.models.doc2vec.TaggedDocument
import random
import pickle
import json
from django.core.cache import cache
import os,django
import redis
from main import fuzzy_search
from dbscan import DbscanClustering

def get_datasest():
    with open("./corpus.txt", 'r',encoding='utf-8') as cf:
        docs = cf.readlines()
        #print(len(docs))
    x_train = []
    #y = np.concatenate(np.ones(len(docs)))
    for i, text in enumerate(docs):
        word_list = text.split(' ')
        l = len(word_list)
        word_list[l-1] = word_list[l-1].strip()
        document = TaggededDocument(word_list, tags=[i])
        x_train.append(document)
 
    return x_train
 
def train(x_train, size=50, epoch_num=1):
    model_dm = Doc2Vec(x_train,min_count=2, window = 5, size = size, sample=1e-5, negative=5, workers=4)
    model_dm.train(x_train, total_examples=model_dm.corpus_count, epochs=10)
    model_dm.save('./model_dm')
 
    return model_dm
 
def cluster(x_train,n,dishlist):
    infered_vectors_list = []
    #print ("load doc2vec model...")
    model_dm = Doc2Vec.load("./model_dm")
    #print ("load train vectors...")
    i = 0
    for text, label in x_train:
        vector = model_dm.infer_vector(text)
        infered_vectors_list.append(vector)
        i += 1
 
    #print ("train kmean model...")
    kmean_model = KMeans(n_clusters=n)
    kmean_model.fit(infered_vectors_list)
    labels= kmean_model.predict(infered_vectors_list)
    #print(len(labels))
    cluster_centers = kmean_model.cluster_centers_
    dishdict={}
    labeldict={}
    with open("./own_claasify.txt", 'w',encoding='utf-8') as wf:
        for i in range(len(labels)):
            string = ""
            text = x_train[i][0]
            for word in text:
                string = string + word
            dishdict[dishlist[i]]=labels[i]
            if(labels[i] not in labeldict):
                labeldict[labels[i]]=[dishlist[i]]
            else:
                labeldict[labels[i]].append(dishlist[i])
            string = str(i) + '\t'
            string = string + str(labels[i])
            string = string + '\n'
            wf.write(string)
    return cluster_centers,dishdict,labeldict
def dist(l1,l2):
    length=len(l1)
    tot=0
    for i in range(length):
        tot=tot+(l1[i]-l2[i])**2
    return tot
 
def find2min(lst):
    min1=100000
    min2=100000
    i1=0
    i2=0
    for i in range(len(lst)):
        if(lst[i]<min1):
            min1=lst[i]
            i1=i
        elif(lst[i]<min2):
            min2=lst[i]
            i2=i
    return i1,i2
def findmax(lst,n):
    minn=[]
    for i in range(n):
        minn.append(-100000)
    id=[]
    for i in range(n):
        id.append(0)
    for i in range(len(lst)):
        for j in range(n):
            if(minn[j]<lst[i]):
                minn[j]=lst[i]
                id[j]=i
                break
    return id
def toclass(dishdict,dishid):
    dish=[]
    for i in dishid:
        dish.append(dishdict[i])
    return dish
def recommend(dish,judge,n,near):#dish:菜类judge:情感;n:聚类数目;near:最近数
    res=[]
    for i in range(n):
        res.append(0)
    for i in range(len(dish)):
        if(judge[i]==1):
            res[dish[i]]+=1
            res[near[dish[i]][0]]+=1
            res[near[dish[i]][1]]+=1
        else:
            res[dish[i]]-=1
            res[near[dish[i]][0]]-=1
            res[near[dish[i]][1]]-=1
    return findmax(res,3)
def todish(recdict, labeldict):
    nowdict = {}
    for key in recdict:
        nowrange = range(500)
        aaa = random.sample(nowrange,15)
        iii = 0
        for i,dishclass in enumerate(recdict[key]):
            if(len(labeldict[dishclass]) >= 2):
                rand_dish = random.sample(labeldict[dishclass],2)
                if(key not in nowdict):
                    nowdict[key]=[rand_dish[0]]
                    nowdict[key].append(rand_dish[1])
                else:
                    nowdict[key].append(rand_dish[0])
                    nowdict[key].append(rand_dish[1])
            else:
                if(key not in nowdict):
                    nowdict[key]=[aaa[iii]]
                    nowdict[key].append(aaa[iii+1])
                else:
                    nowdict[key].append(aaa[iii])
                    nowdict[key].append(aaa[iii+1])
                iii+=2
    return nowdict
def main():
    dish_key, window_key = get_dish_window()
    #print(dish_key)
    #print(window_key)
    _a,_b,dishid_name = get_dish_intro()
    namedict,allname=get_dish_name()
    with open('./name.pkl','wb') as f:
        pickle.dump(allname,f)
    #namedict,key是名字值是dishid
    dbscan = DbscanClustering(stopwords_path='/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/opinion/opinion_mining/processing/library/stop_words.txt')
    name_cluster = dbscan.dbscan(allname, eps=0.05, min_samples=3)
    #namecluster:key是类，值是allname的下标序号，
    #需要获得key是dish_id(dish_id是namedict的值)，值是这个菜对应的类的字典
    id_cluster={}
    db_cluster={}
    for key,val in name_cluster.items():
        for name in val:
            id_cluster[namedict[allname[name]]]=key
            if(key not in db_cluster):
                db_cluster[key]=[namedict[allname[name]]]
            else:
                db_cluster[key].append([namedict[allname[name]]])
    nclusters=15
    alldish = get_intro()
    dishlist = []
    nowline = ''
    for key in alldish:
        dishlist.append(key)
        nowline += alldish[key]
        nowline += '\n'
    nowline=nowline[:-1]
    file=open('/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/recommend/training_data.txt','wb')
    file.write(nowline.encode("utf-8"))
    file.close()
    file = open('/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/recommend/training_data.txt','rb+')
    content = file.read()
    words=jieba.lcut(content,cut_all=False)
    stopwords = []  
    for word in open("/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/recommend/stopwords.txt", "r",encoding='utf-8'):  
        stopwords.append(word.strip())  
    stayed_line = "" 
    wordcorpus=[]
    for word in words:  
        if word!=' ' and word not in stopwords:  
            stayed_line += word + ' '   
            wordcorpus.append(word)
    file=open('./corpus.txt','wb')
    file.write(stayed_line.encode("utf-8"))
    file.close()
    x_train = get_datasest()
    model_dm = train(x_train)
    centers,dishdict,labeldict = cluster(x_train,nclusters,dishlist)
    i=0
    near=[]
    for i in range(nclusters):
        dis=[]
        for j in range(nclusters):
            if(i==j):
                continue
            dis.append(dist(centers[i],centers[j]))
        i1,i2=find2min(dis)
        res=[i1,i2]
        near.append(res)
    alluser = get_dish()
    #print(alluser)
    recdict = {}
    sw_dict={}
    scoredict={}
    for key in name_cluster:
        scoredict[key]=0
    for key in alluser:
        dishid=[]
        judge=[]
        rec_window = []
        rec_search = []
        for dish_star in alluser[key]:
            nowid = dish_star.dishid
            nowjudge = dish_star.judge
            nowstar = dish_star.star
            if(nowstar == 10 or nowstar == 8):
                rec_window.append(dish_key[nowid])
            if(nowstar == 10):
                rec_search.append(nowid)
            dishid.append(nowid)
            judge.append(nowjudge)
        nowwindow = []
        rec_window_list=[]
        if(len(rec_window)>=2):
            for ii in range(len(rec_window)):
                l1 = window_key[rec_window[ii]]
                aaaa1 = random.randint(0,len(l1)-1)
                rec_window_list.append(l1[aaaa1])
        elif(len(rec_window)==1):
            aaaa = random.randint(0,len(rec_window)-1)
            nowwindow.append(rec_window[aaaa])
            l1 = window_key[nowwindow[0]]
            aaaa1 = random.randint(0,len(l1)-1)
            rec_window_list=[]
            rec_window_list.append(l1[aaaa1])
        else:
            rec_window_list=[]
        rec_search_list=[]
        if(len(rec_search) >= 4):
            for jj in range(4):
                search_res,_ = fuzzy_search(dishid_name[rec_search[jj]])
                if(len(search_res)!=0):
                    for jjj in range(len(search_res)):
                        if(search_res[jjj]!=rec_search[jj]):
                            rec_search_list.append(search_res[jjj])
        else:
            for jj in range(len(rec_search)):
                search_res,_ = fuzzy_search(dishid_name[rec_search[jj]])
                if(len(search_res)!=0):
                    for jjj in range(len(search_res)):
                        if(search_res[jjj]!=rec_search[jj]):
                            rec_search_list.append(search_res[jjj])
       # print(rec_search_list)
        maxx=0
        maxid=0
        for key1 in scoredict:
            if(scoredict[key1]>maxx):
                maxx=scoredict[key1]
                maxid=key1
        nowreclist = db_cluster[maxid].copy()
        if(len(nowreclist) >= 3):
            tmprec=random.sample(nowreclist,3)
        else:
            tmprec=nowreclist
        dish=toclass(dishdict,dishid)
        nowrecommend = recommend(dish,judge,nclusters,near)
        #Eprint(len(nowrecommend))
        nowrec_5 = []
        realrec=nowrecommend.copy()
        for m in range(len(tmprec)):
            realrec[len(nowrecommend)-m-1]=tmprec[m]
        rec_search_num = 0
        if(len(rec_search_list)!=0):
            for iiii in range(len(rec_search_list)):
                if(rec_search_list[iiii] not in nowrec_5):
                    nowrec_5.append(rec_search_list[iiii])
                else:
                    continue
                rec_search_num+=1
                if(rec_search_num==3):
                    break
        #print(len(nowrec_5))
        rec_window_num = 0 
        if(len(rec_window_list)!=0):
            for iiii in range(len(rec_window_list)):
                if(rec_window_list[iiii] not in nowrec_5):
                    nowrec_5.append(rec_window_list[iiii])
                else:
                    continue
                rec_window_num+=1
                if(rec_window_num==2):
                    break
        #print(len(nowrec_5))
        recdict[key] = nowrecommend
        sw_dict[key] = nowrec_5
        print(key, nowrec_5)
    all_user = get_user()
    all_dish = range(15)
    nowrec = []
    for key in recdict:
        nowrec.append(key)
    for i in all_user:
        if(i not in nowrec):
            recdict[i] = random.sample(all_dish,3)
    recdict = todish(recdict, labeldict)
    print(sw_dict)
    for key in sw_dict:
        nowlen = 6-len(sw_dict[key])
        for ii in range(nowlen):
            nowrecid = recdict[key][ii]
            if(nowrecid not in sw_dict[key]):
                sw_dict[key].append(nowrecid)
            else:
                continue
        if(len(sw_dict[key])!=6):
            allid = get_dishid()
            for jjj in range(6-len(sw_dict[key])):
                aaaa=random.randint(0,len(allid)-1)
                while(allid[aaaa] in sw_dict[key]):
                    aaaa=random.randint(0,len(allid)-1)
                sw_dict[key].append(allid[aaaa])
    recdict = sw_dict
    dictlist = []
    for key in recdict:
        tmpdict = {}
        tmpdict['user_id'] = key
        tmpdict['dish_id'] = recdict[key]
        dictlist.append(tmpdict)
    return dictlist
if __name__ == '__main__':
    reclist = main()
    print(reclist)
    print(len(reclist))
    r = redis.StrictRedis(host='127.0.0.1', port=2666, db=0)
    for item in reclist:
        user_id = item['user_id']
        key = 'user_recommend_' + str(user_id)
        json_data = json.dumps(item['dish_id'])
        r.set(key, json_data)
    
    pass
