# -*- coding: utf-8 -*-
"""
Created on Sun Mar 31 16:14:01 2019

@author: xyttttt
"""

def findmin(lst,n):
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
    return minn

l=[5,1,2,5,3,1234,151,0,1,2,1,5,5,1,23,1,45]

print(findmin(l,3))