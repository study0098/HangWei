import sys
sys.path.append('/root/Hangwei_BackEnd/')
sys.path.append('/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/sentiment/')
from analysis import sentiment
from modelconnection import Com
from modelconnection import get_comment
from generate_final import LtpTool
import time
from dbscan import DbscanClustering
import jieba
import pickle
import json
import redis
import random
def isempty(taglist):
    for i in taglist:
        if(i!=''):
            return 0
    return 1
def empty(taglist):
    if(len(taglist)==0):
        return 1
    return 0
def isone(taglist):
    if(len(taglist)<=1):
        return 1
    return 0
def process(tag):
    tagword = jieba.lcut(tag)
    jd = 0
    for i in range(len(tagword)-1):
        if(tagword[i]==tagword[i+1]):
            jd=1
            repeat = i
            break
    if(jd == 0):
        return tag
    else:
        newtag = ''
        for j in range(len(tagword)):
            if(j!=repeat):
                newtag+=tagword[j]
        return newtag
def findmin(taglist,realm):
    min = 100
    id = 0
    for i in realm:
        if(len(taglist[i]) < min):
            min = len(taglist[i])
            id = i
    return id,min
def main():
    model = LtpTool()
    commentdict = get_comment()
    dict_list = []
    tmpdict = {}
    tot = 0
    tag_haochi=['非常好吃','很好吃','太好吃啦','太好了','挺不错','不错','太好吃了']
    tag_nanchi=['太难吃了','太难吃啦','真难吃','不好吃','没法吃','好难吃','黑暗料理','太差了','嚼不烂','膻味大','膻味太大','太膻了']
    tag_la=['太辣了','好辣啊','有点辣','怎么这么辣']
    tag_xian=['太咸了','好咸啊','有点咸','怎么这么咸']
    tag_tian=['太甜了','好甜啊','有点甜','怎么这么甜']
    tag_ku=['有点发苦','很苦','太苦了','怎么这么苦']
    dbscan = DbscanClustering(stopwords_path='/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/opinion/opinion_mining/processing/library/stop_words.txt')
    for dishid in commentdict:
        taglist = []
        for com in commentdict[dishid]:
            if((tot+1) % 3 ==0):
                time.sleep(1)
            nowtag = model.generate_tag(com.comment, 4)        
            taglist.append(nowtag)
            for i in tag_haochi:
                if(i in com.comment):
                    taglist.append('这菜好吃')
            for i in tag_nanchi:
                if(i in com.comment):
                    taglist.append('菜品难吃')
            for i in tag_la:
                if(i in com.comment):
                    taglist.append('太辣')
            for i in tag_xian:
                if(i in com.comment):
                    taglist.append('太咸')
            for i in tag_ku:
                if(i in com.comment):
                    taglist.append('太苦')
            for i in tag_tian:
                if(i in com.comment):
                    taglist.append('太甜')
            if('好吃' in com.comment and '不' not in com.comment):
                taglist.append('东西好吃')
            if('不错' in com.comment):
                taglist.append('菜品好吃')
            if('分量' in com.comment and '足' in com.comment and '不' not in com.comment):
                taglist.append('分量足')
            if('分量' in com.comment and ('不足' in com.comment or '不够' in com.comment or '不太够' in com.comment)):
                aaa = random.randint(0,2)
                if(aaa==2):
                    taglist.append('分量不够')
                elif(aaa==1):
                    taglist.append('吃不饱')
                else:
                    taglist.append('不够吃')
            tot+=1
        if(isempty(taglist) or empty(taglist)):
            continue
        print(taglist)
        tmptag = taglist[:]
        for i,tag in enumerate(tmptag):
            tag=process(tag)
            taglist[i]=tag
            if(tag=='东西好吃'):
                a=random.randint(0,2)
                if(a==0):
                    pass
                if(a==1):
                    taglist[i]='菜品不错'
                if(a==2):
                    taglist[i]='挺好吃'
            if(tag=='东西香'):
                a=random.randint(0,4)
                if(a==1 or a==2):
                    taglist[i]='菜品挺香'
                if(a==3 or a==4):
                    taglist[i]='香气四溢'
            if(tag=='东西难吃'):
                a=random.randint(0,4)
                if(a==1 or a==2):
                    taglist[i]='菜品难吃'
                if(a==3 or a==4):
                    taglist[i]='不好吃'
            if('香' in tag and '不' not in tag):
                taglist.append('这菜很好吃')
        if(isone(taglist)):
            result = {}
            result[0]=[0]
        else:
            result = dbscan.dbscan(taglist, eps=0.05, min_samples=1)
        #print(result)
        for key in result:
            if(taglist[result[key][0]]==''):
                break
        result.pop(key)
        tmptot=0
    #    tmpdict={}
        for key in result:
            if(key != -1):
                for i in result[key]:
    #                tmpdict={}
                    nowid, nowstr = findmin(taglist,result[key])
    #                tmpdict['dish'] = dishid
                    if dishid in tmpdict.keys():
                        tags = tmpdict[dishid]
                    else:
                        tags = list()
                    tagg = process(taglist[nowid])
                    newdict = {}
                    newdict['tag'] = tagg
    #                tmpdict['comment'] = commentdict[dishid][i].comment
    #               tmpdict['commentid'] = commentdict[dishid][i].commentid
                    if(tmptot%3 == 0):
                        time.sleep(1)
                    newdict['emotion'] = sentiment(tagg, 90)
        #         dict_list.append(tmpdict)
                    tags.append(newdict)
                    tmpdict[dishid] = tags
                    tmptot+=1
                    #print(dict_list)
                    #print('编号:'+str(commentdict[dishid][i].commentid)+':'+commentdict[dishid][i].comment+':'+process(taglist[nowid]))
            else:
                for i in result[key]:
                    if dishid in tmpdict.keys():
                        tags = tmpdict[dishid]
                    else:
                        tags = list()
                    tagg = process(taglist[i])
                    newdict = {}
                    newdict['tag'] = tagg
    #                tmpdict['comment'] = commentdict[dishid][i].comment
    #               tmpdict['commentid'] = commentdict[dishid][i].commentid
                    if(tmptot%3 == 0):
                        time.sleep(1)
                    newdict['emotion'] = sentiment(tagg, 90)
        #         dict_list.append(tmpdict)
                    tags.append(newdict)
                    tmpdict[dishid] = tags
                    tmptot+=1
#    return dict_list
    
    return tmpdict
#print(dict_list[3])
if __name__ == '__main__':
    dic = main()
    r = redis.StrictRedis(host='127.0.0.1', port=2666, db=0)
    print(dic)
    for dishid, tags in dic.items():
        key = 'dish_tags_' + str(dishid)
        json_data = json.dumps(tags)
        r.set(key, json_data)
    #with open('/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/opinion/opinion_mining/processing/commenttag_list.pkl','wb') as f:
     #   pickle.dump(dic, f, pickle.HIGHEST_PROTOCOL)
