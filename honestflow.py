import sys
import os
sys.path.append('/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/flow/')
from flow import *
pwd = os.path.dirname(os.path.realpath(__file__))
sys.path.append(pwd+"/Hangwei_BackEnd")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hangwei_BackEnd.settings")
from tqdm import tqdm

import django
django.setup()

from hangwei.models import *

class Com(object):
    def __init__(self, comment, id):
        self.comment = comment
        self.commentid = id
        self.emotion = 0
class User_dish(object):
    def __init__(self, dish, judge):
        self.dishid = dish
        self.judge = judge
def get_comment():
    comments_set = Comment.objects.all()
    # print(comments)
    #details = list(comments_set.values_list('detail', flat=True))
    #commentid = list(comments_set.values_list('comment_id', flat=True))
    tmp=[]
    for i,text in enumerate(comments_set):
        tmp.append(Com(text.detail,text.comment_id))
    #dish = list(comments_set.values_list('dish_id', flat=True))
    nowdict = {}
    for i,comment in enumerate(comments_set):
        if(comment.dish_id.dish_id not in nowdict):
            nowdict[comment.dish_id.dish_id]=[tmp[i]]
        else:
            nowdict[comment.dish_id.dish_id].append(tmp[i])
    return nowdict


def get_dish():
    comments_set = Comment.objects.all()
    #dish = list(comments_set.values_list('dish_id', flat=True))
    #print(dish)
    #user = list(comments_set.values_list('user_id', flat=True))
    #star = list(comments_set.values_list('star', flat=True))
    nowdict = {}
    for i,comment in enumerate(comments_set):
        if(comment.user_id.user_id not in nowdict):
            if(comment.star>5):
                #print(comment.dish_id.dish_id)
                tmp = User_dish(comment.dish_id.dish_id,1)
            else:
                tmp = User_dish(comment.dish_id.dish_id,0)
            nowdict[comment.user_id.user_id]=[tmp]
        else:
            if(comment.star>5):
                tmp = User_dish(comment.dish_id.dish_id,1)
            else:
                tmp = User_dish(comment.dish_id.dish_id,0)
            nowdict[comment.user_id.user_id].append(tmp)
    return nowdict
def get_intro():
    dish_set = Dish.objects.all()
    #dish_detail = list(dish_set.values_list('detail', flat=True))
    #dishid = list(dish_set.values_list('dish_id', flat=True))
    nowdict = {}
    for i,dish in enumerate(dish_set):
        nowdict[dish.dish_id] = dish.detail
    return nowdict
def get_user():
    user_set = User.objects.all()
    alluser = list(user_set.values_list('user_id', flat=True))
    return alluser
def get_dish_intro_old():
    dish_set = Dish.objects.all()
    print(dish_set.values())
    dish_detail = list(dish_set.values_list('detail', flat=True))
    dish_name = list(dish_set.values_list('name', flat=True))
    dishid = list(dish_set.values_list('dish_id', flat=True))
    print(dishid)
    print(dish_name)
    nowdict = {}
    for i,dish in enumerate(dishid):
        nowdict[dish] = dish_name[i]+','+dish_detail[i]
    return nowdict,dish_name
def get_dish_intro():
    dish_set = Dish.objects.all()
    dish_value = dish_set.values()
    nowdict = {}
    dish_name = []
    namedict = {}
    for dish in dish_set:
        nowdict[dish.dish_id] = dish.name + ',' + dish.detail
        dish_name.append(dish.name)
        namedict[dish.dish_id] = dish.name
    return nowdict, dish_name,namedict
def get_dish_name():
    dish_set = Dish.objects.all()
    dish_value = dish_set.values()
    namedict = {}
    allname=[]
    for dish in dish_set:
        namedict[dish.name] = dish.dish_id
        allname.append(dish.name)
    return namedict,allname

def set_flow():
    canteen_set = Canteen.objects.all()
    print(canteen_set)
    for i in range(len(canteen_set)):
        cap = int(canteen_set[i].capacity)
        if(i==4):
            print(cap)
        for j in tqdm(range(24)):
            for k in range(60):
                pepnum = getflow(cap, j, k)
    #            if(i==4):
     #               print(pepnum)
                #print(j,k,pepnum)
                flow_set = Flow.objects.filter(canteen=canteen_set[i], hour=j * 60 + k)
                if (flow_set):
                    newflow = flow_set[0]
                    newflow.people_num = pepnum
                else:
                    newflow = Flow(canteen=canteen_set[i], hour=j * 60 + k, people_num=pepnum)
                newflow.save()


def main():
    get_dish_intro()
    
    sys.exit(0)
    commentdict = get_comment()
    userdict = get_dish()
    dish = get_intro()
    print(dish)
    
   # print(dish_id)
    #print(rate)


if __name__ == '__main__':
    # main()
    set_flow()
