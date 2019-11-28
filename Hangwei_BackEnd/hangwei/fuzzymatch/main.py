# -*- coding: utf-8 -*-
"""
Created on Sun Mar 31 15:10:44 2019

@author: xyttttt
"""
import sys
sys.path.append('/root/Hangwei_BackEnd/')
sys.path.append('/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/fuzzymatch/')
from modelconnection import get_dish_intro
import pandas as pd
from fuzzychinese import FuzzyChineseMatch
from chinese_fuzzy_match import chinese_fuzzy_match
import jieba
from Pinyin2Hanzi import DefaultDagParams
from Pinyin2Hanzi import dag
from pypinyin import pinyin, lazy_pinyin,Style
from Pinyin2Hanzi import is_pinyin
from Pinyin2Hanzi import simplify_pinyin
from xpinyin import Pinyin
import pickle
class TrieNode:
    def __init__(self):
        self.value = None
        self.children = {}
#遍历树
class SearchIndex:
    def __init__(self, index, char=None, parent=None):
        self.index = index
        self.char = char
        self.parent = parent
        
#定义Trie字典树
class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.trie_path = '/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/fuzzymatch/data/pinyin_trie.model'
        self.pinyin_path = '/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/fuzzymatch/data/pinyin.txt'
    #添加树节点
    def insert(self, key):
        node = self.root
        for char in key:
            if char not in node.children:
                child = TrieNode()
                node.children[char] = child
                node = child
            else:
                node = node.children[char]
        node.value = key
    #查找节点
    def search(self, key):
        node = self.root
        matches = []
        for char in key:
            if char not in node.children:
                break
            node = node.children[char]
            if node.value:
                matches.append(node.value)
        return matches

    def build_trie(self):
        trie = Trie()
        for line in open(self.pinyin_path):
            word = line.strip().lower()
            trie.insert(word)
        with open(self.trie_path, 'wb') as f:
            pickle.dump(trie, f)


class PinyinCut:
    def __init__(self):
        self.trie_path = '/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/fuzzymatch/data/pinyin_trie.model'
        self.trie = self.load_trie(self.trie_path)
        
    def load_trie(self, trie_path):
        with open(trie_path, 'rb') as f:
            return pickle.load(f)
    #音节切分
    def cut(self, sent):
        #获取总长度
        len_sent = len(sent)
        #存储切分序列
        chars = []
        #存储候选序列,SearchIndex(0)表示第一个字符
        candidate_index = [SearchIndex(0)]
        #当前单词的最后一个位置
        last_index = None
        while candidate_index:
            p = candidate_index.pop()
            #如果当前字符所在索引为句子长度，那么最后一个index为本身，即直接到句子末尾。
            if p.index == len_sent:
                last_index = p
                break
            matches = self.trie.search(sent[p.index:])
            for m in matches:
                new_index = SearchIndex(len(m) + p.index, m, p)
                candidate_index.append(new_index)
        index = last_index
        while index:
            if index.parent:
                chars.insert(0, index.char)
            index = index.parent

        return chars
def clean(string):
    ext = [' ','￥','!','@','#','$','%','^','&','*','(',')','-','_','+','=','\\','|','/','.',',','?','<','>','\'','"','~','`']
    try:
        nowstr = ''
        for i in range(len(string)):
            if(string[i] not in ext):
                if(string[i] < '0' or string[i] > '9'):
                    nowstr += string[i]
        if(nowstr == ''):
            return None
        return nowstr
    except:
        return None
    
def ispinyin(tmp):
    string = tmp
    string = string.lower()
    for i in range(len(string)):
        if(string[i]<'a' or string[i]>'z'):
            return string,0
    return string,1
def fuzzy_search(string):
    string = clean(string)
    emp = []
    if(string == None):
        return emp,None
    nowstring,jd = ispinyin(string)
    if(jd == 0):
        dish_intro,dish_name,namedict = get_dish_intro()
        dishid = []
        dish_detail = []
        name = []
        for key in dish_intro:
            dishid.append(key)
            dish_detail.append(dish_intro[key])
        for key in namedict:
            name.append(namedict[key])
        test_dict =  pd.Series(dish_detail)
        allname = pd.Series(name)
        raw_word = pd.Series([nowstring])
        fcm1 = FuzzyChineseMatch(ngram_range=(3, 3), analyzer='stroke')
        fcm1.fit(test_dict)
        top_similar_stroke = fcm1.transform(raw_word, n=len(test_dict)//2)
        index_stroke = fcm1.get_index()
        score_stroke = fcm1.get_similarity_score()
        fcm2 = FuzzyChineseMatch(ngram_range=(3, 3), analyzer='stroke')
        fcm2.fit(allname)
        top_similar_char = fcm2.transform(raw_word, n=len(test_dict)//2)
        index_char = fcm2.get_index()
        score_char = fcm2.get_similarity_score()
        res_list = []
        if(score_char[0][0] >= 0.4 or score_stroke[0][0] > 0.4):
            print('0.4')
            for i,score in enumerate(score_char[0]):
                if(score >= 0.4 and dishid[index_char[0][i]] not in res_list):
                    res_list.append(dishid[index_char[0][i]])
                else:
                    break
            for i,score in enumerate(score_stroke[0]):
                if(score > 0.4 and dishid[index_char[0][i]] not in res_list):
                    res_list.append(dishid[index_stroke[0][i]])
                else:
                    break
            #print('----------------------------------')
            #for i in res_list:
                #print(namedict[i])
            wword = jieba.lcut(string)
            
            #for i in res_list:
                #print(namedict[i])
            finallist=res_list[:]
            for word in wword:
                for i in res_list:
                    if(word in namedict[i]):
                        tmpp = i
                        finallist.remove(i)
                        finallist.insert(0,tmpp)
            for key in namedict:
                if(nowstring in namedict[key] and key not in finallist):
                    finallist.insert(0,key)
            #finallist=res_list[:]
            retlist = finallist[:]
            for i in finallist:
                jd = 0
                for word in nowstring:
                    if(word in namedict[i]):
                        pass
                    else:
                        jd = 1
                        break
                if(jd == 0):
                    tmpp = i
                    retlist.remove(i)
                    retlist.insert(0,tmpp)
            #print('----------------------------------')
            #for i in finallist:
               # print(namedict[i])
            #print(nowstring)
            return list(set(retlist)),None
        else:
            print('not 0.4')
            for i in range(len(dish_name)):
                result = chinese_fuzzy_match(string,dish_name[i])
                #print(result)
                if(result['match_type'] != 'not_match'):
                    jd = 1
                    res_list.append(dishid[i])
            for key in namedict:
                if(string in namedict[key] and key not in res_list):
                    res_list.insert(0,key)
            worddict = {}
            stopwords=[]
            for word in open("/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/recommend/stopwords.txt", "r",encoding='utf-8'):  
                stopwords.append(word.strip())  
            for i,intro in enumerate(res_list):
                nowword = jieba.lcut(dish_intro[intro])
                for j in nowword:
                    if(j not in stopwords):
                        if(j not in worddict):
                            worddict[j]=1
                        else:
                            worddict[j]+=1
            max = 0
            maxword = ''
            for key in worddict:
                if(worddict[key]>max):
                    max = worddict[key]
                    maxword = key
            return list(set(res_list)),maxword
    else:
        res_list = []
        dish_intro,dish_name,namedict = get_dish_intro()
        dishid = []
        dish_detail = []

        with open('/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/fuzzymatch/worddict.pkl','rb') as f:
            dishdict = pickle.load(f)
        if(nowstring not in dishdict):
            return res_list,'NULL'
        res_list = dishdict[nowstring]
        worddict = {}
        stopwords=[]
        for word in open("/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/recommend/stopwords.txt", "r",encoding='utf-8'):  
            stopwords.append(word.strip())  
        for i,intro in enumerate(res_list):
            nowword = jieba.lcut(dish_intro[intro])
            for j in nowword:
                if(j not in stopwords):
                    if(j not in worddict):
                        worddict[j]=1
                    else:
                        worddict[j]+=1
        max = 0
        maxword = ''
        for key in worddict:
            if(worddict[key]>max):
                max = worddict[key]
                maxword = key
        return list(set(res_list)),maxword
if __name__ == '__main__':
    #result,maxword = fuzzy_search('(*)')
    pin = Pinyin()
    dish_intro,dish_name,namedict = get_dish_intro()
    with open('/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/fuzzymatch/wordname.pkl','wb') as f:
        pickle.dump(namedict, f)
    with open('/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/fuzzymatch/iddict.pkl','wb') as f:
        pickle.dump(dish_intro, f)
    alldict = {}
    stopwords = []
    for word in open("/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/recommend/stopwords.txt", "r",encoding='utf-8'):  
        stopwords.append(word.strip()) 
    for key in dish_intro:
        nowline = dish_intro[key]
        nowword = jieba.lcut(nowline,cut_all=True)

        #strrr = ''.join(lazy_pinyin(namedict[key]))
        strrr = pin.get_pinyin(namedict[key]).replace('-','')
        if(strrr not in alldict):
            alldict[strrr]=[key]
        else:
            alldict[strrr].append(key)
        for word in nowword:
            if(word in stopwords):
                continue
            strr = ''.join(lazy_pinyin(word))
            if(strr not in alldict):
                alldict[strr]=[key]
            else:
                alldict[strr].append(key)
    
    with open('./worddict.pkl','wb') as f:
        pickle.dump(alldict,f, pickle.HIGHEST_PROTOCOL)
    '''
    dish_intro,dish_name,namedict = get_dish_intro()
    if(maxword!=None):
        print('您是不是想搜：'+maxword)
        for i in range(len(result)):
            print(result[i], dish_intro[result[i]])
    else:
        for i in range(len(result)):
            print(dish_intro[result[i]])
    '''
    pass


