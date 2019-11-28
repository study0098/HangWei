import sys
import os

# 获取当前文件的目
pwd = os.path.dirname(os.path.realpath(__file__))
# 获取项目名的目录(因为我的当前文件是在项目名下的文件夹下的文件.所以是../)
sys.path.append(pwd+"/Hangwei_BackEnd")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Hangwei_BackEnd.settings")

import django
django.setup()

from hangwei.models import *

class Com(object):
    def __init__(self, comment, id):
        self.comment = comment
        self.commentid = id
        self.emotion = 0
class User_dish(object):
    def __init__(self, dish, judge, star):
        self.dishid = dish
        self.judge = judge
        self.star = star
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
                tmp = User_dish(comment.dish_id.dish_id,1,comment.star)
            else:
                tmp = User_dish(comment.dish_id.dish_id,0,comment.star)
            nowdict[comment.user_id.user_id]=[tmp]
        else:
            if(comment.star>5):
                tmp = User_dish(comment.dish_id.dish_id,1,comment.star)
            else:
                tmp = User_dish(comment.dish_id.dish_id,0,comment.star)
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
def get_dishid():
    dish_set = Dish.objects.all()
    dish_value = dish_set.values()
    idlist=[]
    for dish in dish_set:
        idlist.append(dish.dish_id)
    return idlist
def get_dish_name():
    dish_set = Dish.objects.all()
    dish_value = dish_set.values()
    namedict = {}
    allname=[]
    for dish in dish_set:
        namedict[dish.name] = dish.dish_id
        allname.append(dish.name)
    return namedict,allname
def get_dish_window():
    dish_set = Dish.objects.all()
    dish_value = dish_set.values()
    #window_set = Window.objects.all()
    #window_value = window_set.values()
    dish_key={}
    window_key={}
    for dish in dish_set:
        dish_key[dish.dish_id] = dish.window_id.window_id
        if(dish.window_id.window_id not in window_key):
            window_key[dish.window_id.window_id] = [dish.dish_id]
        else:
            window_key[dish.window_id.window_id].append(dish.dish_id)
    return dish_key, window_key
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
    main()
