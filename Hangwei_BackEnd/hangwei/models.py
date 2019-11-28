from django.db import models
import uuid
import os


# Create your models here.
class Canteen(models.Model):
    """
    食堂表
    """
    canteen_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, default=None)
    position = models.CharField(max_length=256, default=None)
    capacity = models.CharField(max_length=256, default=None)
    business_hours = models.CharField(max_length=256, default=None)

    def __str__(self):
        return self.name


def rename_window_file(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(instance.window_id, ext)
    return os.path.join('img', 'windows', filename)


class Window(models.Model):
    """
    窗口表
    """
    window_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, default=None)
    location = models.CharField(max_length=256, default=None)
    canteen_id = models.ForeignKey(Canteen, on_delete=models.CASCADE, default=None)
    img = models.ImageField(upload_to=rename_window_file, default=None, blank=True)

    def __str__(self):
        return self.canteen_id.name + "-" + self.name


def rename_file(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex[:10], ext)
    return os.path.join('img', str(instance.window_id.window_id), filename)


class Dish(models.Model):
    """
    菜品表
    """
    dish_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, default=None)
    rate = models.FloatField(default=0.0)
    price = models.FloatField(default=0.0)
    detail = models.CharField(max_length=1024, default=None)
    window_id = models.ForeignKey(Window, on_delete=models.CASCADE, default=None)
    img = models.ImageField(upload_to=rename_file, default=None, blank=True)

    def __str__(self):
        return self.name


class User(models.Model):
    """
    用户表
    """
    user_id = models.AutoField(primary_key=True)
    openid = models.CharField(max_length=256)
    name = models.CharField(max_length=256, default=None)
    gender = models.IntegerField(default=0)
    city = models.CharField(max_length=256, default=None)
    province = models.CharField(max_length=256, default=None)
    country = models.CharField(max_length=256, default=None)
    avatarUrl = models.CharField(max_length=1024, default='https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1553269747858&di=bf518acca5f758415bc173ecbe7fbea8&imgtype=0&src=http%3A%2F%2Fpic.51yuansu.com%2Fpic3%2Fcover%2F01%2F69%2F80%2F595f67c3a6eb1_610.jpg')

    def __str__(self):
        return self.name


class Comment(models.Model):
    """
    菜品评论表
    """
    comment_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, default=None)    # openid
    dish_id = models.ForeignKey(Dish, on_delete=models.CASCADE, default=None)
    detail = models.CharField(max_length=256, default=None)
    star = models.IntegerField(default=0)
    consent = models.IntegerField(default=0)
    opposition = models.IntegerField(default=0)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.detail

    # natual_key的序列化
    def natural_key(self):
        data = dict()
        data["detail"] = self.detail
        return data

    # natual_keys的解序列化
    class Meta:
        unique_together = (('detail', ),)


class CommentReply(models.Model):
    """
    评论回复表
    """
    comment_reply_id = models.AutoField(primary_key=True)
    comment_id = models.ForeignKey(Comment, on_delete=models.CASCADE, default=None)
    commenter_user_id = models.ForeignKey(User, related_name='comment_user',
                                          on_delete=models.DO_NOTHING, default=None)  # openid
    mentioned_user_id = models.ForeignKey(User, related_name='mentioned_user',
                                          on_delete=models.DO_NOTHING, default=None)
    detail = models.CharField(max_length=256, default=None)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.detail


def rename_comment_file(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex[:10], ext)
    return os.path.join('img', str(instance.comment_id.dish_id.window_id.window_id), filename)


class PictureInComment(models.Model):
    """
    评论中的图片
    """
    picture_in_comment_id = models.AutoField(primary_key=True)
    comment_id = models.ForeignKey(Comment, on_delete=models.SET_NULL, default=None, null=True)
    img = models.ImageField(upload_to=rename_comment_file, default=None, blank=True)


class CommentLike(models.Model):
    """
    用户评论点赞表
    """
    comment_like_id = models.AutoField(primary_key=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, default=None)
    user = models.ForeignKey(User, related_name='user',
                             on_delete=models.DO_NOTHING, default=None)  # openid
    time = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    """
    新消息提醒表
    """
    user_mentioned = models.ForeignKey(User, on_delete=models.CASCADE, default=None, related_name='user_mentioned')
    user_new = models.ForeignKey(User, on_delete=models.CASCADE, default=None, related_name='user_new')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, default=None, related_name='comment')
    reply_new = models.ForeignKey(CommentReply, on_delete=models.CASCADE, default=None, related_name='reply_new')
    read = models.BooleanField(default=True)
    time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.reply_new.detail


def rename_cachefile(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex[:10], ext)
    return os.path.join('img', str(instance.window.window_id), filename)


class DishCache(models.Model):
    """
    众包信息缓存菜品
    """
    dish_cache_id = models.AutoField(primary_key=True)
    dish_id = models.IntegerField(default=-1)
    name = models.CharField(max_length=256, default=None)
    price = models.FloatField(default=0.0)
    detail = models.CharField(max_length=512, default=None)
    window = models.ForeignKey(Window, on_delete=models.CASCADE, default=None)
    img = models.ImageField(upload_to=rename_cachefile, default=None, blank=True)

    def __str__(self):
        return self.name


class WindowCache(models.Model):
    """
    众包信息缓存窗口表
    """
    window_cache_id = models.AutoField(primary_key=True)
    window_id = models.IntegerField(default=-1)
    name = models.CharField(max_length=256, default=None)
    location = models.CharField(max_length=256, default=None)
    canteen = models.ForeignKey(Canteen, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.canteen.name + "-" + self.name


class CanteenCache(models.Model):
    """
    众包信息缓存食堂表
    """
    canteen_cache_id = models.AutoField(primary_key=True)
    canteen_id = models.IntegerField(default=-1)
    name = models.CharField(max_length=256, default=None)
    position = models.CharField(max_length=256, default=None)
    capacity = models.CharField(max_length=256, default=None)
    business_hours = models.CharField(max_length=256, default=None)

    def __str__(self):
        return self.name


def rename_feedback_file(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(instance.feedback_id, ext)
    return os.path.join('img', 'feedback', filename)


class Feedback(models.Model):
    """
    用户反馈表
    """
    feedback_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, default=None)
    detail = models.CharField(max_length=512, default=None)
    img = models.ImageField(upload_to=rename_feedback_file, default=None, blank=True)

    def __str__(self):
        return self.detail


class WantEat(models.Model):
    """
    用户想吃表
    """
    want_eat_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, default=None)
    time = models.DateTimeField(auto_now_add=True)


class HaveEaten(models.Model):
    """
    用户吃过表
    """
    have_eaten_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, default=None)
    time = models.DateTimeField(auto_now_add=True)


class UserCheckin(models.Model):
    """
    用户每日签到表
    """
    user_checkin_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    date = models.DateField(auto_now_add=True)


class HotSearch(models.Model):
    """
    热搜表
    """
    keyword = models.CharField(max_length=128, default=None)
    frequency = models.IntegerField(default=0)

    def __str__(self):
        return self.keyword


class Flow(models.Model):
    """
    人流量
    """
    canteen = models.ForeignKey(Canteen, on_delete=models.CASCADE, default=None)
    hour = models.IntegerField(default=0)   # 每个食堂共23个，表示当前是第几小时
    people_num = models.IntegerField(default=0)


def rename_announcement_file(instance, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(instance.announcement_id, ext)
    return os.path.join('img', 'announcement', filename)


class Announcement(models.Model):
    """
    公告
    """
    announcement_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=256, default=None)
    detail = models.TextField(default=None)
    announcer = models.CharField(max_length=256, default=None)
    time = models.DateTimeField(auto_now_add=True)
    img = models.ImageField(upload_to=rename_announcement_file, default=None, blank=True)

    def __str__(self):
        return self.detail


class DishTag(models.Model):
    dish_tag_id = models.AutoField(primary_key=True)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, default=None)
    detail = models.CharField(max_length=256, default=None)

    def __str__(self):
        return self.detail


class DishTagCache(models.Model):
    dish_tag_cache_id = models.AutoField(primary_key=True)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, default=None)
    detail = models.CharField(max_length=256, default=None)

    def __str__(self):
        return self.detail
