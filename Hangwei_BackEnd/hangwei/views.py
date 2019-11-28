import sys
sys.path.append('/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/fuzzymatch/')
sys.path.append('/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/sentiment/')
sys.path.append('/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/flow/')
sys.path.append('/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/goodword/')
from django.http import HttpResponse
from django.conf import settings
import json
from .models import *
import urllib.request
import requests
import base64
import os
import datetime, time
from django.db.models import Avg, Q, F, Sum
from django.db.models.aggregates import Count
from django.core import serializers
import random
from django.core.cache import cache
from .fuzzymatch.main import *
#from .fuzzymatch.main import TrieNode, SearchIndex, Trie, PinyinCut
from .flow.flow import getflow,sig,nsig
from .goodword.filt import filt
from analysis import sentiment
import redis
import math


# Create your views here.
def index(request):
    return HttpResponse("Hello world")


def browse(request):
    """
    browse all dishes
    :param request:
    :return:
    """
    data = dict()
    dish_set = Dish.objects.all().values()
    data["data"] = list(dish_set)
    return HttpResponse(json.dumps(data), content_type='application/json', charset='utf-8')

    # json_data = serializers.serialize('json', dish_set)
    # json_data = json.loads(json_data)
    # return JsonResponse(json_data, safe=False)


def get_canteen_dishs(request):
    canteen_id = request.GET.get('canteen_id')
    page = request.GET.get('page')
    canteen = Canteen.objects.get(canteen_id=canteen_id)
    window_set = canteen.window_set.all()
    windows = list(window_set.values())
    data = dict()
    data["windows"] = windows
    for i in range(len(data["windows"])):
        dish_set = window_set[i].dish_set.all().values()
        dishes = list(dish_set)
        data["windows"][i]["dishes"] = dishes

    return HttpResponse(json.dumps(data), content_type='application/json', charset='utf-8')


def get_window_dishes(request):
    """
    获取窗口下的菜品
    :param request:
    :return:
    """
    window_id = request.GET.get('window_id')
    window = Window.objects.get(window_id=window_id)
    dish_set = window.dish_set.all().values()
    dishes = list(dish_set)
    data = dict()
    data['dishes'] = dishes
    return HttpResponse(json.dumps(data), content_type='application/json', charset='utf-8')


def get_openid(request):
    """
    get user's information
    :param request: code and userInfo
    :return: json with openid
    """
    code = request.GET.get('code')
    user_info = request.GET.get('userInfo')
    user_info = json.loads(user_info)
    url = 'https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&js_code=%s&grant_type=authorization_code' \
          % (settings.APPID, settings.APPSECRET, code)
    response = urllib.request.urlopen(url)
    result = json.loads(response.read().decode('utf-8'))
    openid = result.get('openid')
    if openid:
        users = User.objects.filter(openid=openid)
        update_info(openid, user_info)
        if not users:
            user = User(openid=openid, name=user_info["nickName"], gender=user_info["gender"], city=user_info["city"],
                        province=user_info["province"], country=user_info["country"],
                        avatarUrl=user_info["avatarUrl"])
            user.save()
    else:
        openid = 'None'
    data = dict()
    data["openid"] = openid
    return HttpResponse(json.dumps(data))


def update_info(openid, user_info):
    """
    update the user's information
    :param openid:
    :param user_info:
    :return:
    """
    try:
        user = User.objects.get(openid=openid)
        user.name = user_info["nickName"]
        user.gender = user_info["gender"]
        user.city = user_info["city"]
        user.province = user_info["province"]
        user.country = user_info["country"]
        user.avatarUrl = user_info["avatarUrl"]
        user.save()
    except User.DoesNotExist:
        pass

def search(request):
    """
    search for dishes
    :param request:
    :return:
    """
    keyword = request.GET.get('keyword')
    keyword = clean(keyword)
    dish_id_list, maxword = fuzzy_search(keyword)
    print(dish_id_list)
    if maxword is None:
        if(keyword is not None):
            add_hot_search(keyword)
    else:
        add_hot_search(maxword)
    data = dict()
    dish_set = Dish.objects.none()

    data['data'] = list()
    for id in dish_id_list:
        data['data'].append(Dish.objects.filter(dish_id=id).values()[0])
        
    # dish_set = Dish.objects.filter(dish_id__in=dish_id_list).values()
    # dish_set = dish_set.values() 
    # data["data"] = list(dish_set)
    for dish_i in data["data"]:
        win_list = list(Window.objects.filter(window_id=dish_i['window_id_id']).values())
        dish_i["window_name"] = win_list[0]['name']
        canteen_id = win_list[0]['canteen_id_id']
        canteen_list = list(Canteen.objects.filter(canteen_id=canteen_id).values())
        dish_i["canteen_name"] = canteen_list[0]['name']

    return HttpResponse(json.dumps(data), content_type='application/json', charset='utf-8')


def add_hot_search(keyword):
    hot_search_set = HotSearch.objects.filter(keyword=keyword)
    if hot_search_set:
        hot_search_set.update(frequency=F('frequency') + 1)
    else:
        new_hot_search = HotSearch(keyword=keyword, frequency=0)
        new_hot_search.save()


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return json.JSONEncoder.default(self, obj)


def get_comment(request):
    """
    get comment of dish
    :param request:
    :return:
    """
    dish_id = request.GET.get('dish_id')
    dishes = Dish.objects.filter(dish_id=dish_id)
    comments = Comment.objects.filter(dish_id=dish_id).order_by('-time')
    openid = request.GET.get('openid')
    if not openid:
        return HttpResponse(json.dumps(dict()), content_type='application/json', charset='utf-8')
    myuser = User.objects.get(openid=openid)
    data = dict()
    if dishes:
        data["comments"] = list(comments.values())
        for i in range(len(data["comments"])):
            user = comments[i].user_id
            data["comments"][i]["nickname"] = user.__str__()
            data["comments"][i]["openid"] = user.openid
            data['comments'][i]['reply_num'] = len(comments[i].commentreply_set.all())
            if CommentLike.objects.filter(comment=comments[i], user=myuser):
                data["comments"][i]["liked"] = True
                # print(user, comments[i])
            else:
                data["comments"][i]["liked"] = False
            imgs = PictureInComment.objects.filter(comment_id=data["comments"][i]['comment_id']).values()  # 获取属性值
            imgs = list(imgs)
            data["comments"][i]["imgs"] = list()
            if imgs:
                for item in imgs:
                    data["comments"][i]["imgs"].append(item["img"])

    return HttpResponse(json.dumps(data, cls=DateEncoder), content_type='application/json', charset='utf-8')


def add_tag(request):
    """
    为菜品添加标签
    TODO:增加审核
    :param request:
    :return:
    """
    dish_id = request.GET.get('dish_id')
    dish = Dish.objects.get(dish_id=dish_id)
    tag = request.GET.get('tag')
    tag_emotion = sentiment(tag,90)
    new_tag = DishTagCache(dish=dish, detail=tag)
#    new_tag.save()
    return HttpResponse(1)


def get_dish(request):
    """
    名称位置评分标签价格描述
    :param request:
    :return:
    """
    dish_id = request.GET.get('dish_id')
    dishes = Dish.objects.filter(dish_id=dish_id)
    dish = dishes[0]
    openid = request.GET.get('openid')
    if not openid:
        return HttpResponse(json.dumps(dict()), content_type='application/json', charset='utf-8')
    window = dish.window_id
    canteen = window.canteen_id
    data = dict()
    data["dish"] = list(dishes.values())[0]
    data["dish"]["window_name"] = window.name
    data["dish"]["canteen_name"] = canteen.name
    data["dish"]["window_img"] = window.img.name
    data['dish']['want_eat_num'] = len(dish.wanteat_set.all())
    data['dish']['have_eaten_num'] = len(dish.haveeaten_set.all())
    data['dish']['want_eat_flag'] = False
    data['dish']['have_eaten_flag'] = False
    users = User.objects.filter(openid=openid)
    if users:
        user = users[0]
        if WantEat.objects.filter(dish=dish, user=user):
            data['dish']['want_eat_flag'] = True
        if HaveEaten.objects.filter(dish=dish, user=user):
            data['dish']['have_eaten_flag'] = True
    tags = list()
    """
    tag = {"tag": "服务态度好", "emotion": 1}
    tags.append(tag)
    tag = {"tag": "上菜太慢了", "emotion": 0}
    tags.append(tag)
    tag = {"tag": "太咸了", "emotion": 0}
    tags.append(tag)
    tag = {"tag": "分量足够大", "emotion": 1}
    tags.append(tag)
    data["dish"]["tags"] = tags
    """
    r = redis.StrictRedis(host='127.0.0.1', port=2666, db=0)
    key = 'dish_tags_' + str(dish_id)
    if r.exists(key):
        tags = json.loads(r.get(key))
    data['dish']['tags'] = tags

    # tag user added
    tag_list = list(dish.dishtagcache_set.values_list('detail', flat=True))
    tags = list()
    for item in tag_list:
        tag = dict()
        tag['tag'] = item
        tag['emotion'] = 1
        tags.append(tag)
    data['dish']['tags'] += tags

    return HttpResponse(json.dumps(data, cls=DateEncoder), content_type='application/json', charset='utf-8')


def add_comment(request):
    """
    add comment for dish
    :param request:
    :return:
    """
    user_id = request.GET.get('user_id')
    if not user_id:
        return HttpResponse(json.dumps({'flag': False}), content_type='application/json', charset='utf-8')
    user = User.objects.get(openid=user_id)
    dish_id = request.GET.get('dish_id')
    dish = Dish.objects.get(dish_id=dish_id)

    # 控制评论频率
    r = redis.StrictRedis(host='127.0.0.1', port=2666, db=0)
    r_key = 'dish_comment_' + str(user_id) + '_' + str(dish_id)
    if r.exists(r_key):
        return HttpResponse(json.dumps({'flag': False}), content_type='application/json', charset='utf-8')
    else:
        r.set(r_key, '1')
        r.expire(r_key, 60)

    detail = request.GET.get('detail')
    # detail = filt(detail)
    star = request.GET.get('star')
    comment = Comment(user_id=user, dish_id=dish, detail=detail, star=star)
    comment.save()

    # update dish's rate when add comment
    comments = Comment.objects.filter(dish_id=dish)
    if comments:
        star__avg = comments.aggregate(Avg('star'))
        dish.rate = int(star__avg['star__avg'])
        dish.save()

    data = dict()
    data["comment_id"] = comment.comment_id
    data['flag'] = True
    return HttpResponse(json.dumps(data))


def add_comment_img(request):
    """
    add image for commengt
    :param request:
    :return:
    """
    img = request.FILES['img']
    comment_id = request.POST.get('comment_id')
    comment_id = Comment.objects.get(comment_id=comment_id)
    p_i_c = PictureInComment(img=img, comment_id=comment_id)
    p_i_c.save()
    return HttpResponse(1)


def add_comment_reply(request):
    """
    add reply to comment
    :param request:
    :return:
    """
    comment_id = request.GET.get('comment_id')
    comment = Comment.objects.get(comment_id=comment_id)
    openid = request.GET.get('commenter_user_id')
    commenter_user = User.objects.get(openid=openid)

    # 控制回复频率
    r = redis.StrictRedis(host='127.0.0.1', port=2666, db=0)
    r_key = 'comment_reply_' + str(openid) + '_' + str(comment_id)
    if r.exists(r_key):
        return HttpResponse(json.dumps({'flag': False}), content_type='application/json', charset='utf-8') 
    else:
        r.set(r_key, '1')
        r.expire(r_key, 60)

    mentioned_user = User.objects.get(user_id=request.GET.get('mentioned_user_id'))
    detail = request.GET.get('detail')
    # detail = filt(detail)
    comment_reply = CommentReply(comment_id=comment, commenter_user_id=commenter_user,
                                 mentioned_user_id=mentioned_user, detail=detail)
    comment_reply.save()

    message = Message(user_mentioned=mentioned_user, user_new=commenter_user,
                      comment=comment, reply_new=comment_reply, read=False)
    message.save()

    data = dict()
    data["comment_id"] = comment_reply.comment_reply_id
    data['flag'] = True
    return HttpResponse(json.dumps(data))


def get_comment_reply(request):
    """
    get comment's reples
    :param request:
    :return:
    """
    comment_id = request.GET.get('comment_id')
    comment = Comment.objects.get(comment_id=comment_id)
    replies_set = comment.commentreply_set.all()
    replies = list(replies_set.values())
    for i in range(len(replies)):
        replies[i]["mentioned_user_name"] = replies_set[i].mentioned_user_id.name
        replies[i]["commenter_user_name"] = replies_set[i].commenter_user_id.name
        replies[i]["commenter_user_openid"] = replies_set[i].commenter_user_id.openid
    # print(replies)

    data = dict()
    data["data"] = replies
    return HttpResponse(json.dumps(data, cls=DateEncoder), content_type='application/json', charset='utf-8')


def add_comment_consent(request):
    """
    点赞，前端会给后端发送评论id以及用户openid
    :param request:
    :return:
    """
    comment_id = request.GET.get('comment_id')
    comment = Comment.objects.get(comment_id=comment_id)

    openid = request.GET.get('openid')
    if not openid:
        return HttpResponse(json.dumps(dict()), content_type='application/json', charset='utf-8')
    user = User.objects.get(openid=openid)

    comment_like_log = CommentLike.objects.filter(comment=comment, user=user)
    if comment_like_log:
        return HttpResponse(0)

    comment.consent += 1
    comment.save()

    comment_like = CommentLike(comment=comment, user=user)
    comment_like.save()

    return HttpResponse(1)


def delete_comment_consent(request):
    """
    取消点赞，前端会给后端发送评论id以及用户openid
    :param request:
    :return:
    """
    comment_id = request.GET.get('comment_id')
    comment = Comment.objects.get(comment_id=comment_id)

    openid = request.GET.get('openid')
    if not openid:
        return HttpResponse(json.dumps(dict()), content_type='application/json', charset='utf-8')
    user = User.objects.get(openid=openid)

    comment_like_log = CommentLike.objects.filter(comment=comment, user=user)
    if not comment_like_log:
        return HttpResponse(0)

    comment.consent -= 1
    comment.save()

    comment_like_log.delete()

    return HttpResponse(1)


def get_user_comment(request):
    """
    用户评论信息，前端给后端发送用户id，返回该用户的所有评论信息（不包括回复，以及评论下的回复）
    :param request:
    :return:
    """
    openid = request.GET.get('openid')
    if not openid:
        return HttpResponse(json.dumps(dict()), content_type='application/json', charset='utf-8')
    user = User.objects.get(openid=openid)
    page = request.GET.get('page')
    data = dict()
    if page is None:
        comments = Comment.objects.filter(user_id=user).order_by('-time')   # -time时间是从近到远，即递减
    else:
        page = int(page)
        comments = Comment.objects.filter(user_id=user).order_by('-time')[page * 10:page * 10 + 10]
        data['page'] = page
    data["data"] = list(comments.values())
    for i in range(len(comments)):
        data["data"][i]["dish_name"] = comments[i].dish_id.name

        imgs = PictureInComment.objects.filter(comment_id=comments[i]).values()  # 获取属性值
        imgs = list(imgs)
        data["data"][i]["imgs"] = list()
        if imgs:
            for item in imgs:
                data["data"][i]["imgs"].append(item["img"])
    # print(comments)
    return HttpResponse(json.dumps(data, cls=DateEncoder), content_type='application/json', charset='utf-8')


def get_user_comment_num(request):
    """
    获取用户评价的数量
    :param request:
    :return:
    """
    openid = request.GET.get('openid')
    if not openid:
        return HttpResponse(json.dumps(dict()), content_type='application/json', charset='utf-8')
    user = User.objects.get(openid=openid)
    data = dict()
    data['comment_num'] = len(user.comment_set.all())
    return HttpResponse(json.dumps(data), content_type='application/json', charset='utf-8')


def delete_comment(request):
    """
    评论的删除，前端会给后端发送要删除的评论的id
    :param request:
    :return:
    """
    comment_id = request.GET.get('comment_id')
    Comment.objects.filter(comment_id=comment_id).delete()
    return HttpResponse(1)


def delete_reply(request):
    """
    回复的删除，前端给后端发送要删除的回复的id
    :param request:
    :return:
    """
    comment_reply_id = request.GET.get('comment_reply_id')
    CommentReply.objects.filter(comment_reply_id=comment_reply_id).delete()
    return HttpResponse(1)


def get_personal_recommend(request):
    """
    获取用户个性化推荐
    :param request:
    :return:
    """
    r = redis.StrictRedis(host='127.0.0.1', port=2666, db=0) 
    openid = request.GET.get('openid')
    data = dict()
    if openid:
        user = User.objects.get(openid=openid)
        user_id = user.user_id
        flag = False
        key = 'user_recommend_' + str(user_id)
        if r.exists(key):
            flag = True
            dish_ids = json.loads(r.get(key))
        if flag:
            dish_set = Dish.objects.filter(dish_id__in=dish_ids).values()
        else:
            dish_set = Dish.objects.order_by('-rate')[:6].values()
    else:
        dish_set = Dish.objects.order_by('-rate')[:6].values()
    data["dishes"] = list(dish_set)
    for dish_i in data["dishes"]:
        win = Window.objects.get(window_id=dish_i['window_id_id'])
        dish_i["window_name"] = win.name
        canteen = win.canteen_id
        dish_i["canteen_name"] = canteen.name

    return HttpResponse(json.dumps(data), content_type='application/json', charset='utf-8')


def check_message(request):
    """
    检查是否有新消息
    :param request:
    :return:
    """
    openid = request.GET.get('openid')
    if not openid:
        return HttpResponse(json.dumps(dict()), content_type='application/json', charset='utf-8')
    data = dict()
    try:
        user_mentioned = User.objects.get(openid=openid)
        messages = Message.objects.filter(user_mentioned=user_mentioned, read=False)
        if messages:
            data["have_message"] = True
        else:
            data["have_message"] = False
    except User.DoesNotExist:
        data["have_message"] = False

    return HttpResponse(json.dumps(data), content_type='application/json', charset='utf-8')


def get_message(request):
    """
    获取新消息并设置为已读
    :param request:
    :return:
    """
    openid = request.GET.get('openid')
    if not openid:
        return HttpResponse(json.dumps(dict()), content_type='application/json', charset='utf-8')
    user_mentioned = User.objects.get(openid=openid)
    page = request.GET.get('page')
    data = dict()
    if page is None:
        messages = Message.objects.filter(user_mentioned=user_mentioned, read=False).order_by('-time')
    else:
        page = int(page)
        messages = Message.objects.filter(user_mentioned=user_mentioned, read=False).order_by('-time')[page * 10:page * 10 + 10]
        data['page'] = page
    data["messages"] = list()
    data["messages"] = list(messages.values())
    for i in range(len(messages)):
        data["messages"][i]["dish_id"] = messages[i].comment.dish_id_id
        # data["messages"][i]["user_mentioned_name"] = messages[i].user_mentioned.name
        data["messages"][i]["user_new_name"] = messages[i].user_new.name
        data["messages"][i]["user_new_avator"] = messages[i].user_new.avatarUrl
        data["messages"][i]["comment"] = messages[i].comment.detail
        data["messages"][i]["reply_new"] = messages[i].reply_new.detail
        data["messages"][i]["reply_time"] = messages[i].reply_new.time
    # print(data["messages"])
    messages.update(read=True)
    # jsons = serializers.serialize('json', messages, use_natural_foreign_keys=True)
    return HttpResponse(json.dumps(data, cls=DateEncoder), content_type='application/json', charset='utf-8')


def get_old_message(request):
    """
        获取新消息并设置为已读
        :param request:
        :return:
        """
    openid = request.GET.get('openid')
    if not openid:
        return HttpResponse(json.dumps(dict()), content_type='application/json', charset='utf-8')
    user_mentioned = User.objects.get(openid=openid)
    page = request.GET.get('page')
    data = dict()
    if page is None:
        messages = Message.objects.filter(user_mentioned=user_mentioned, read=True).order_by('-time')
    else:
        page = int(page)
        messages = Message.objects.filter(user_mentioned=user_mentioned, read=True).order_by('-time')[page * 10:page * 10 + 10]
        data['page'] = page
    data["messages"] = list()
    data["messages"] = list(messages.values())
    for i in range(len(messages)):
        data["messages"][i]["dish_id"] = messages[i].comment.dish_id_id
        # data["messages"][i]["user_mentioned_name"] = messages[i].user_mentioned.name
        data["messages"][i]["user_new_name"] = messages[i].user_new.name
        data["messages"][i]["user_new_avator"] = messages[i].user_new.avatarUrl
        data["messages"][i]["comment"] = messages[i].comment.detail
        data["messages"][i]["reply_new"] = messages[i].reply_new.detail
        data["messages"][i]["reply_time"] = messages[i].reply_new.time
    return HttpResponse(json.dumps(data, cls=DateEncoder), content_type='application/json', charset='utf-8')


def add_dish_cache(request):
    if request.method == 'POST':
        dish_id = request.POST.get('dish_id')
        name = request.POST.get('name')
        price = request.POST.get('price')
        detail = request.POST.get('detail')
        window_id = request.POST.get('window_id')
        window = Window.objects.get(window_id=window_id)
        img = request.FILES['img']
        dish_cache = DishCache(dish_id=dish_id, name=name, price=price, detail=detail, window=window, img=img)
        dish_cache.save()
    elif request.method == 'GET':
        dish_id = request.GET.get('dish_id')
        name = request.GET.get('name')
        price = request.GET.get('price')
        detail = request.GET.get('detail')
        window_id = request.GET.get('window_id')
        window = Window.objects.get(window_id=window_id)
        dish_cache = DishCache(dish_id=dish_id, name=name, price=price, detail=detail, window=window)
        dish_cache.save()
        
    return HttpResponse(1)


def add_window_cache(request):
    window_id = request.GET.get('window_id')
    name = request.GET.get('name')
    location = request.GET.get('location')
    canteen_id = request.GET.get('canteen_id')
    canteen = Canteen.objects.get(canteen_id=canteen_id)

    window_cache = WindowCache(window_id=window_id, name=name, location=location, canteen=canteen)
    window_cache.save()
    return HttpResponse(1)


def add_canteen_cache(request):
    canteen_id = request.GET.get('canteen_id')
    name = request.GET.get('name')
    position = request.GET.get('position')
    capacity = request.GET.get('capacity')
    business_hours = request.GET.get('business_hours')
    canteen_cache = CanteenCache(canteen_id=canteen_id, name=name, position=position,
                                 capacity=capacity, business_hours=business_hours)
    canteen_cache.save()
    return HttpResponse(1)


# TODO:用户意见反馈接口
def add_feedback(request):
    if request.method == 'POST':
        openid = request.POST.get('openid')
        if not openid:
            return HttpResponse(1)

        # 控制反馈频率
        r = redis.StrictRedis(host='127.0.0.1', port=2666, db=0)
        r_key = 'feedback_' + str(openid)
        if r.exists(r_key):
            return HttpResponse(json.dumps({'flag': False}), content_type='application/json', charset='utf-8')
        else:
            r.set(r_key, '1')
            r.expire(r_key, 60)

        detail = request.POST.get('detail')
        user = User.objects.get(openid=openid)
        img = request.FILES['img']
        if detail:
            feedback = Feedback(user=user, detail=detail, img=img)
            feedback.save()

    elif request.method == 'GET':
        openid = request.GET.get('openid')
        if not openid:
            return HttpResponse(1)
            
        # 控制反馈频率
        r = redis.StrictRedis(host='127.0.0.1', port=2666, db=0)
        r_key = 'feedback_' + str(openid)
        if r.exists(r_key):
            return HttpResponse(json.dumps({'flag': False}), content_type='application/json', charset='utf-8')
        else:
            r.set(r_key, '1')
            r.expire(r_key, 60)
            
        detail = request.GET.get('detail')
        user = User.objects.get(openid=openid)
        if detail:
            feedback = Feedback(user=user, detail=detail)
            feedback.save()

    return HttpResponse(json.dumps({'flag': True}), content_type='application/json', charset='utf-8')


def add_want_eat(request):
    openid = request.GET.get('openid')
    if not openid:
        return HttpResponse(json.dumps(dict()), content_type='application/json', charset='utf-8')
    user = User.objects.get(openid=openid)
    dish_id = request.GET.get('dish_id')
    dish = Dish.objects.get(dish_id=dish_id)
    if not WantEat.objects.filter(user=user, dish=dish):
        want_eat = WantEat(user=user, dish=dish)
        want_eat.save()
    return HttpResponse(1)


def add_have_eaten(request):
    openid = request.GET.get('openid')
    if not openid:
        return HttpResponse(json.dumps(dict()), content_type='application/json', charset='utf-8')
    user = User.objects.get(openid=openid)
    dish_id = request.GET.get('dish_id')
    dish = Dish.objects.get(dish_id=dish_id)
    if not HaveEaten.objects.filter(user=user, dish=dish):
        have_eaten = HaveEaten(user=user, dish=dish)
        have_eaten.save()
    return HttpResponse(1)


def delete_want_eat(request):
    openid = request.GET.get('openid')
    if not openid:
        return HttpResponse(json.dumps(dict()), content_type='application/json', charset='utf-8')
    user = User.objects.get(openid=openid)
    dish_id = request.GET.get('dish_id')
    dish = Dish.objects.get(dish_id=dish_id)
    WantEat.objects.filter(user=user, dish=dish).delete()
    return HttpResponse(1)


def delete_have_eaten(request):
    openid = request.GET.get('openid')
    if not openid:
        return HttpResponse(json.dumps(dict()), content_type='application/json', charset='utf-8')
    user = User.objects.get(openid=openid)
    dish_id = request.GET.get('dish_id')
    dish = Dish.objects.get(dish_id=dish_id)
    HaveEaten.objects.filter(user=user, dish=dish).delete()
    return HttpResponse(1)


def get_want_eat(request):
    openid = request.GET.get('openid')
    if not openid:
        return HttpResponse(json.dumps(dict()), content_type='application/json', charset='utf-8')
    user = User.objects.get(openid=openid)
    page = request.GET.get('page')
    data = dict()
    if page is None:
        want_eat_set = WantEat.objects.filter(user=user).order_by('-time')
    else:
        page = int(page)
        want_eat_set = WantEat.objects.filter(user=user).order_by('-time')[page * 10:page * 10 + 10]
        data['page'] = page
    data["dishes"] = list()
    for item in want_eat_set:
        dish = dict()
        dish['dish_id'] = item.dish.dish_id
        dish['name'] = item.dish.name
        dish['num'] = len(item.dish.wanteat_set.all()) - 1
        dish['window_name'] = item.dish.window_id.name
        dish['canteen_name'] = item.dish.window_id.canteen_id.name
        dish['img'] = item.dish.img.name
        dish['time'] = item.time
        data['dishes'].append(dish)
    return HttpResponse(json.dumps(data, cls=DateEncoder), content_type='application/json', charset='utf-8')


def get_have_eaten(request):
    openid = request.GET.get('openid')
    if not openid:
        return HttpResponse(json.dumps(dict()), content_type='application/json', charset='utf-8')
    user = User.objects.get(openid=openid)
    page = request.GET.get('page')
    data = dict() 
    if page is None:
        have_eaten_set = HaveEaten.objects.filter(user=user).order_by('-time')
    else:
        page = int(page)
        have_eaten_set = HaveEaten.objects.filter(user=user).order_by('-time')[page * 10:page * 10 + 10]
        data['page'] = page 
    data["dishes"] = list()
    for item in have_eaten_set:
        dish = dict()
        dish['dish_id'] = item.dish.dish_id
        dish['name'] = item.dish.name
        dish['num'] = len(item.dish.haveeaten_set.all()) - 1
        dish['window_name'] = item.dish.window_id.name
        dish['canteen_name'] = item.dish.window_id.canteen_id.name
        dish['img'] = item.dish.img.name
        dish['time'] = item.time
        data['dishes'].append(dish)
    return HttpResponse(json.dumps(data, cls=DateEncoder), content_type='application/json', charset='utf-8')


def get_canteen_windows(request):
    canteen_id = request.GET.get('canteen_id')
    canteen = Canteen.objects.get(canteen_id=canteen_id)
    windows_set = canteen.window_set.all()
    windows = list(windows_set.values())
    data = dict()
    data['windows'] = list()
    for window in windows_set:
        data['windows'].append({'name': window.name, 'window_id': window.window_id})
    return HttpResponse(json.dumps(data), content_type='application/json', charset='utf-8')


def get_user_activity(request):
    """
    获取用户活跃度, split by (0, 1, 3, 6)
    :param request:
    :return:
    """
    openid = request.GET.get('openid')
    if not openid:
        return HttpResponse(json.dumps(dict()), content_type='application/json', charset='utf-8')
    user = User.objects.get(openid=openid)
    comments = user.comment_set.all()
    checkins = user.usercheckin_set.all()
    wanteats = user.wanteat_set.all()
    haveeatens = user.haveeaten_set.all()
    replys = user.comment_user.all()
    today = datetime.datetime.now().date()
    activity = [0 for i in range(365)]
    for comment in comments:
        delta = (today - comment.time.date()).days
        activity[delta] += 1
    for checkin in checkins:
        delta = (today - checkin.date).days
        activity[delta] += 1
    for wanteat in wanteats:
        delta = (today - wanteat.time.date()).days
        activity[delta] += 1
    for haveeaten in haveeatens:
        delta = (today - haveeaten.time.date()).days
        activity[delta] += 1
    for reply in replys:
        delta = (today - reply.time.date()).days
        activity[delta] += 1
    for i in range(365):
        if activity[i] >= 6:
            activity[i] = 3
        elif activity[i] >= 3:
            activity[i] = 2
        elif activity[i] >= 1:
            activity[i] = 1
    data = dict()
    # data['start_day'] = (today - datetime.timedelta(days=365)).__str__()
    data['activity'] = activity
    return HttpResponse(json.dumps(data, cls=DateEncoder), content_type='application/json', charset='utf-8')


def get_flow(request):
    """
    获取人流量
    """
    canteens = Canteen.objects.all()
    cap = []
    for can in canteens:
        cap.append(can.capacity)
    data = dict()
    data['canteens'] = list(canteens.values())
    cur_hour = time.localtime().tm_hour
    cur_min = time.localtime().tm_min
    for i in range(len(canteens)):
        people_num = Flow.objects.get(canteen=canteens[i], hour=cur_hour * 60 + cur_min).people_num
        # people_num = getflow(int(cap[i]),cur_hour,cur_min)
        if(cur_hour==11 and (cur_min>=15 and cur_min<=59)):
            people_num += int(int(cap[i])*0.6)
        if(cur_hour==17 and (cur_min>=15 and cur_min<=45)):
            people_num += int(int(cap[i])*0.6)
        print(people_num,cap[i])
        #if(people_num >= int(cap[i])):
            # people_num =  int(cap[i])+random.randint(-5,0)
        people_num = int(people_num * 1.1)
        if(people_num < 10):
            people_num = 0

        if people_num >= int(int(cap[i]) * 1.3):
            people_num = int(int(cap[i]) * 1.3) + random.randint(-5, 0)
        data['canteens'][i]['people_num'] = people_num
    return HttpResponse(json.dumps(data), content_type='application/json', charset='utf-8')


def checkin(request):
    """
    用户签到
    :param request:
    :return:
    """
    openid = request.GET.get('openid')
    if not openid:
        return HttpResponse(json.dumps(dict()), content_type='application/json', charset='utf-8')
    user = User.objects.get(openid=openid)
    user_checkin = UserCheckin(user=user)
    user_checkin.save()
    return HttpResponse(1)


def check_checkin(request):
    """
    检查用户是否签到
    :param request:
    :return:
    """
    openid = request.GET.get('openid')
    if not openid:
        return HttpResponse(json.dumps(dict()), content_type='application/json', charset='utf-8')
    user = User.objects.get(openid=openid)
    date = datetime.datetime.now().date()
    data = dict()
    if UserCheckin.objects.filter(user=user, date=date):
        data['have_checkin'] = True
    else:
        data['have_checkin'] = False
    return HttpResponse(json.dumps(data), content_type='application/json', charset='utf-8')


def get_hot_search(request):
    """
    获取校园热搜
    :param request:
    :return:
    """
    data = dict()
    hot_search_set = HotSearch.objects.filter(frequency__gt=10).order_by('frequency')
    data['hot_search'] = list(hot_search_set.values())
    return HttpResponse(json.dumps(data), content_type='application/json', charset='utf-8')


def tolevel(num,cap):
    if(num/cap<0.25):
        return 0
    if(num/cap<0.5):
        return 1
    if(num/cap<0.75):
        return 2
    return 3


def update_flow(request):
    """
    四种程度向0.1, 0.3, 0.6, 1.0靠拢
    :param request:
    :return:
    """
    # 控制反馈频率
    openid = request.GET.get('openid')
    r = redis.StrictRedis(host='127.0.0.1', port=2666, db=0)
    r_key = 'update_flow' + str(openid)
    if r.exists(r_key):
        return HttpResponse(0)
    else:
        r.set(r_key, '1')
        r.expire(r_key, 60)

    canteen_id = request.GET.get('canteen_id')
    adjustment = int(request.GET.get('flow'))
    canteen = Canteen.objects.get(canteen_id=canteen_id)
    capacity = int(canteen.capacity)
    cur_hour = time.localtime().tm_hour
    cur_min = time.localtime().tm_min
    try:
        flow = Flow.objects.get(canteen=canteen, hour=cur_hour * 60 + cur_min)
        flow1 = Flow.objects.get(canteen=canteen, hour=cur_hour * 60 + cur_min + 1)
        flow2 = Flow.objects.get(canteen=canteen, hour=cur_hour * 60 + cur_min + 2)
        flow3 = Flow.objects.get(canteen=canteen, hour=cur_hour * 60 + cur_min + 3)
        people_num = flow.people_num
        nowlevel = tolevel(people_num,capacity)
        new_num = people_num
        if(adjustment-nowlevel==-3):
            new_num = int(people_num*0.2)+random.randint(-10,0)
        if(adjustment-nowlevel==-2):
            if(nowlevel==3):
                new_num = int(people_num*0.5)+random.randint(-10,0)
            elif(nowlevel==2):
                new_num = int(people_num*0.6)+random.randint(-10,0)
        if(adjustment-nowlevel==-1):
            new_num = people_num-random.randint(0,10)-capacity * 0.098
        if(adjustment-nowlevel==0):
            pass
        if(adjustment-nowlevel==1):
            new_num = people_num+random.randint(-10,0)+capacity * 0.098
        if(adjustment-nowlevel==2):
            if(nowlevel==1):
                new_num = int(people_num*1.6)+random.randint(0,20)
            elif(nowlevel==0):
                new_num = int(people_num*2)+random.randint(0,20)
        if(adjustment-nowlevel==3):
            new_num = int(people_num*2.5)+random.randint(0,20)
        print(adjustment,nowlevel,people_num,new_num,capacity)
        if(new_num > int(capacity * 1.3)):
            new_num = int(capacity * 1.25)
        flow.people_num = int(new_num)
        flow1.people_num = int(new_num)+random.randint(-10,10)
        flow2.people_num = int(new_num)+random.randint(-10,10)
        flow3.people_num = int(new_num)+random.randint(-10,10)
        flow.save()
        flow1.save()
        flow2.save()
        flow3.save()
    except Flow.DoesNotExist:
        pass
    return HttpResponse(1)


def add_prefer(request):
    """
    添加用户偏好
    :param request:
    :return:
    """
    openid = request.GET.get('openid')
    if not openid:
        return HttpResponse(json.dumps(dict()), content_type='application/json', charset='utf-8')
    key = 'user_prefer_' + openid
    preferences = request.GET.get('preferences')
    json_data = json.loads(preferences)
    cache.set(key, json_data, timeout=None)
    return HttpResponse(1)


def get_prefer(request):
    """
    获取用户偏好
    :param request:
    :return:
    """
    openid = request.GET.get('openid')
    if not openid:
        return HttpResponse(json.dumps(dict()), content_type='application/json', charset='utf-8')
    key = 'user_prefer_' + openid
    json_data = cache.get(key)
    data = dict()
    data['preferences'] = json_data
    return HttpResponse(json.dumps(data), content_type='application/json', charset='utf-8')


def get_user_uncomment_dishes(request):
    """
    随机获取用户未评价的5个菜品
    :param request:
    :return:
    """
    openid = request.GET.get('openid')
    if not openid:
        return HttpResponse(json.dumps(dict()), content_type='application/json', charset='utf-8')
    key = request.GET.get('key')
    user = User.objects.get(openid=openid)
    comments_set = user.comment_set.all()
    dish_ids = list(comments_set.values_list('dish_id', flat=True))
    ret_dish_ids = list()
    num = 0
    while num < 5:
        id = random.randint(3, 654)
        if id not in dish_ids:
            if Dish.objects.filter(dish_id=id):
                ret_dish_ids.append(id)
                num += 1
    dish_set = Dish.objects.filter(dish_id__in=ret_dish_ids)
    data = dict()
    data['dishes'] = list(dish_set.values())
    for temp_index, dish in enumerate(data["dishes"]):
        dish["window_name"] = dish_set[temp_index].window_id.name
        dish["canteen_name"] = dish_set[temp_index].window_id.canteen_id.name
    return HttpResponse(json.dumps(data), content_type='application/json', charset='utf-8')


def get_announcement(request):
    """
    获取最近的十条公告
    :param request:
    :return:
    """
    page = int(request.GET.get('page'))
    announcement_set = Announcement.objects.all().order_by('-time')[page * 10:page * 10 + 10]
    data = dict()
    data['announcements'] = list(announcement_set.values())
    data['page'] = page
    return HttpResponse(json.dumps(data, cls=DateEncoder), content_type='application/json', charset='utf-8')


def user_statistics_comment_num(openid):
    user = User.objects.get(openid=openid)
    data = dict()
    data['comment_num'] = len(user.comment_set.all())
    return data


def user_statistics_like_num(openid):
    user = User.objects.get(openid=openid)
    data = dict()
    like_num = user.comment_set.aggregate(Sum('consent'))
    data['likes_num'] = like_num
    return data


def user_statistics_continuous_checkin(openid):
    user = User.objects.get(openid=openid)
    data = dict()
    today = datetime.datetime.now().date()
    checkins = user.usercheckin_set.all()
    if not checkins:
        data['continuous_checkin_days'] = 0
        return data
    count = 1
    max_count = 1
    last_date = checkins[0].date
    for checkin in checkins:
        if checkin.date == last_date + datetime.timedelta(days=1):
            count += 1
        else:
            max_count = max(count, max_count)
            count = 1
        last_date = checkin.date
    max_count = max(count, max_count)

    data['continuous_checkin_days'] = max_count
    return data


def get_user_statistics(request):
    """
    用户画像统计，用于成就记录
    :param request:
    :return:
    """
    openid = request.GET.get('openid')
    if not openid:
        return HttpResponse(json.dumps(dict()), content_type='application/json', charset='utf-8')
    type = int(request.GET.get('type'))
    data = dict()
    if type == 1:
        data = user_statistics_comment_num(openid)
    elif type == 2:
        data = user_statistics_like_num(openid)
    elif type == 3:
        data = user_statistics_continuous_checkin(openid)

    return HttpResponse(json.dumps(data, cls=DateEncoder), content_type='application/json', charset='utf-8')


def get_ranklist(request):
    type = int(request.GET.get('type'))
    data = dict()
    if type == 0:
        dish_set = Dish.objects.all().order_by('-rate')[0:15].values()
        data["list"] = list(dish_set)
    elif type == 1:
        dish_set = Dish.objects.annotate(comment_num=Count('comment')).order_by('-comment_num')[0:15].values()
        data["list"] = list(dish_set)
    elif type == 2:
        dish_set = Dish.objects.annotate(want_eat_num=Count('wanteat')).order_by('-want_eat_num')[0:15].values()
        data["list"] = list(dish_set)
    elif type == 3:
        dish_set = Dish.objects.annotate(have_eaten_num=Count('haveeaten')).order_by('-have_eaten_num')[0:15].values()
        data["list"] = list(dish_set)
    else:
        data['list'] = []
    return HttpResponse(json.dumps(data, cls=DateEncoder), content_type='application/json', charset='utf-8')


def test(request):
    """
    后端临时测试接口
    :param request:
    :return:
    """
    key = 'user_recommend_16'
    r = redis.StrictRedis(host='127.0.0.1', port=2666, db=0)
    if r.exists(key):
        value = r.get(key)
    else:
        value = 1
    return HttpResponse(value)
