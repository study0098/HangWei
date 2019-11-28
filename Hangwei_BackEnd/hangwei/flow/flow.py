import math
import time
import random
import json
import urllib

def glue(cur_y,cur_m,cur_d):
    if(cur_m<10):
        strm='0'+str(cur_m)
    else:
        strm=str(cur_m)
    stry = str(cur_y)
    if(cur_d<10):
        strd='0'+str(cur_d)
    else:
        strd=str(cur_d)
    strr = stry+strm+strd
    return strr
def sig(x):
    tmp = 1+math.e**(-(x-4))
    return 1.0/tmp
def nsig(x):
    tmp = 1+math.e**(x-12)
    return 1.0/tmp
def getflow(tot,cur_hour,cur_min):
    cur_y = time.localtime().tm_year
    cur_m = time.localtime().tm_mon
    cur_d = time.localtime().tm_mday
    date = glue(cur_y,cur_m,cur_d)
    #server_url = "http://api.goseek.cn/Tools/holiday?date="
 
    #vop_url_request = urllib.request.Request(server_url+date)
    #vop_response = urllib.request.urlopen(vop_url_request)
    
    #vop_data= json.loads(vop_response.read())
    vop_data={}
    vop_data['data']=0
    if(vop_data['data']==0):
        if 9 <= cur_hour < 11 or (13 <= cur_hour<14 and cur_min >30) or  14<=cur_hour< 17 or 19 <= cur_hour <= 24 or 0 <= cur_hour < 7:
            people_num = random.randint(0, 5)
            if(0 <= cur_hour < 7):
                people_num=0
        else:
            if(cur_hour >=7 and cur_hour < 9):
                nowmin = cur_min
                jd=0
                if(cur_hour==8):
                    nowmin+=60
                    jd=1
                nownum = nowmin*16/120
                co = random.randint(tot - 30,tot - 15)
                if(jd==0):
                    people_num = int(co * sig(nownum))+random.randint(-5,15)
                else:
                    people_num = int(co * nsig(nownum))+random.randint(-5,15)
                if(people_num) <=0:
                    people_num =random.randint(5,10)
            if(cur_hour >=11 and cur_hour < 14):
                nowmin = cur_min
                jd=0
                if(cur_hour==12):
                    nowmin+=60
                    if(cur_min==15):
                        jd=1
                elif(cur_hour==13):
                    jd=1
                    nowmin+=120
                nownum = nowmin*16/150
                co = random.randint(tot-20,tot)
                if(jd==0):
                    people_num = int(co * sig(nownum))+random.randint(-5,15)
                else:
                    people_num = int(co * nsig(nownum))+random.randint(-5,15)
                if(people_num) <=0:
                    people_num =random.randint(5,10)
            if(cur_hour >=17 and cur_hour < 19):
                nowmin = cur_min
                jd=0
                if(cur_hour==18):
                    nowmin+=60
                    jd=1
                nownum = nowmin*16/120
                co = random.randint(tot-25,tot-10)
                if(jd==0):
                    people_num = int(co * sig(nownum))+random.randint(-5,15)
                else:
                    people_num = int(co * nsig(nownum))+random.randint(-5,15)
                if(people_num) <=0:
                    people_num =random.randint(5,10)
    elif(vop_data['data']==1):
        if 9 <= cur_hour < 11 or (13 <= cur_hour<14 and cur_min >30) or  14<=cur_hour< 17 or 19 <= cur_hour <= 24 or 0 <= cur_hour < 7:
            people_num = random.randint(0, 2)
        else:
            if(cur_hour >=7 and cur_hour < 9):
                nowmin = cur_min
                jd=0
                if(cur_hour==8):
                    nowmin+=60
                    jd=1
                nownum = nowmin*16/120
                co = random.randint(tot-40,tot-20)
                if(jd==0):
                    people_num = int(co * sig(nownum))+random.randint(-15,8)
                else:
                    people_num = int(co * nsig(nownum))+random.randint(-15,8)
                if(people_num) <=0:
                    people_num =random.randint(5,10)
            if(cur_hour >=11 and cur_hour < 14):
                nowmin = cur_min
                jd=0
                if(cur_hour==12):
                    nowmin+=60
                    if(cur_min==15):
                        jd=1
                elif(cur_hour==13):
                    jd=1
                    nowmin+=120
                nownum = nowmin*16/180
                co = random.randint(tot-30,tot)
                if(jd==0):
                    people_num = int(co * sig(nownum))+random.randint(-15,8)
                else:
                    people_num = int(co * nsig(nownum))+random.randint(-15,8)
                if(people_num) <=0:
                    people_num =random.randint(5,10)
            if(cur_hour >=17 and cur_hour < 19):
                nowmin = cur_min
                jd=0
                if(cur_hour==18):
                    nowmin+=60
                    jd=1
                nownum = nowmin*16/120
                co = random.randint(tot-35,tot-15)
                if(jd==0):
                    people_num = int(co * sig(nownum))+random.randint(-15,8)
                else:
                    people_num = int(co * nsig(nownum))+random.randint(-15,8)
                if(people_num) <=0:
                    people_num =random.randint(5,10)
    else:
        if 9 <= cur_hour < 11 or (13 <= cur_hour<14 and cur_min >30) or  14<=cur_hour< 17 or 19 <= cur_hour <= 24 or 0 <= cur_hour < 7:
            people_num = random.randint(0, 5)
        else:
            if(cur_hour >=7 and cur_hour < 9):
                nowmin = cur_min
                jd=0
                if(cur_hour==8):
                    nowmin+=60
                    jd=1
                nownum = nowmin*16/120
                co = random.randint(tot-40,tot-20)
                if(jd==0):
                    people_num = int(co * sig(nownum) * 0.618)+random.randint(-15,15)
                else:
                    people_num = int(co * nsig(nownum) * 0.618)+random.randint(-15,15)
                if(people_num) <=0:
                    people_num =random.randint(5,10)
            if(cur_hour >=11 and cur_hour < 14):
                nowmin = cur_min
                jd=0
                if(cur_hour==12):
                    nowmin+=60
                    if(cur_min==15):
                        jd=1
                elif(cur_hour==13):
                    jd=1
                    nowmin+=120
                nownum = nowmin*16/180
                co = random.randint(tot-30,tot)
                if(jd==0):
                    people_num = int(co * sig(nownum) * 0.618)+random.randint(-15,15)
                else:
                    people_num = int(co * nsig(nownum) * 0.618)+random.randint(-15,15)
                if(people_num) <=0:
                    people_num =random.randint(5,10)
            if(cur_hour >=17 and cur_hour < 19):
                nowmin = cur_min
                jd=0
                if(cur_hour==18):
                    nowmin+=60
                    jd=1
                nownum = nowmin*16/120
                co = random.randint(tot-35,tot-14)
                if(jd==0):
                    people_num = int(co * sig(nownum) * 0.618)+random.randint(-15,15)
                else:
                    people_num = int(co * nsig(nownum) * 0.618)+random.randint(-15,15)
                if(people_num) <=0:
                    people_num =random.randint(5,10)
    return people_num