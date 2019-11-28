from django.contrib import admin
from .models import *


# Register your models here.
admin.site.register(User)
admin.site.register(Canteen)
admin.site.register(Window)
admin.site.register(Dish)
admin.site.register(Comment)
admin.site.register(CommentReply)
admin.site.register(PictureInComment)
admin.site.register(Message)
admin.site.register(DishCache)
admin.site.register(WindowCache)
admin.site.register(CanteenCache)
admin.site.register(Feedback)
admin.site.register(UserCheckin)
admin.site.register(HotSearch)
admin.site.register(Announcement)
admin.site.register(DishTag)
admin.site.register(DishTagCache)

