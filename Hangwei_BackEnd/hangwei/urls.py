from django.urls import path
from . import views
from . import labs
from . import reviews

app_name = 'hangwei'
urlpatterns = [
    path('index/', views.index),
    path('browse/', views.browse),
    path('get_openid/', views.get_openid),
    path('search/', views.search),
    path('get_dish/', views.get_dish),
    path('add_tag/', views.add_tag),
    path('get_comment/', views.get_comment),
    path('add_comment/', views.add_comment),
    path('add_comment_img/', views.add_comment_img),
    path('add_reply/', views.add_comment_reply),
    path('get_reply/', views.get_comment_reply),
    path('get_user_comment/', views.get_user_comment),
    path('del_comment/', views.delete_comment),
    path('del_reply/', views.delete_reply),
    path('add_comment_like/', views.add_comment_consent),
    path('del_comment_like/', views.delete_comment_consent),
    path('get_canteen_dishes/', views.get_canteen_dishs),
    path('get_personal_recommend/', views.get_personal_recommend),
    path('check_message/', views.check_message),
    path('get_old_message/', views.get_old_message),
    path('get_message/', views.get_message),
    path('get_canteen_windows/', views.get_canteen_windows),
    path('get_window_dishes/', views.get_window_dishes),
    path('add_dish_cache/', views.add_dish_cache),
    path('add_window_cache/', views.add_window_cache),
    path('add_canteen_cache/', views.add_canteen_cache),
    path('add_feedback/', views.add_feedback),
    path('add_want_eat/', views.add_want_eat),
    path('add_have_eaten/', views.add_have_eaten),
    path('del_want_eat/', views.delete_want_eat),
    path('del_have_eaten/', views.delete_have_eaten),
    path('get_want_eat/', views.get_want_eat),
    path('get_have_eaten/', views.get_have_eaten),
    path('get_user_activity/', views.get_user_activity),
    path('get_flow/', views.get_flow),
    path('checkin/', views.checkin),
    path('check_checkin/', views.check_checkin),
    path('get_hot_search/', views.get_hot_search),
    path('update_flow/', views.update_flow),
    path('add_prefer/', views.add_prefer),
    path('get_prefer/', views.get_prefer),
    path('get_user_comment_num/', views.get_user_comment_num),
    path('get_user_uncomment_dishes/', views.get_user_uncomment_dishes),
    path('get_announcement/', views.get_announcement),
    path('get_user_statistics/', views.get_user_statistics),
    path('get_ranklist/', views.get_ranklist),

    path('review/check/', reviews.index),
    path('review/dish_cache_check/', reviews.dish_cache_check),
    path('review/window_cache_check/', reviews.window_cache_check),
    path('review/canteen_cache_check/', reviews.canteen_cache_check),

    path('lab_identify_dish/', labs.lab_identify_dish),

    path('test/', views.test),
]
