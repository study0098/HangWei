from django.shortcuts import render, redirect, HttpResponse
from .models import *
from django.contrib.admin.views.decorators import user_passes_test


@user_passes_test(lambda u:u.is_staff, login_url='/admin/login')
def index(request):
    content = {}
    dish_cache_list = DishCache.objects.all()
    window_cache_list = WindowCache.objects.all()
    canteen_cache_list = CanteenCache.objects.all()
    content['dish_cache_list'] = dish_cache_list
    content['window_cache_list'] = window_cache_list
    content['canteen_cache_list'] = canteen_cache_list
    return render(request, 'review/check.html', content)


@user_passes_test(lambda u:u.is_staff, login_url='/admin/login')
def dish_cache_check(request):
    dish_cache_id = request.POST.get('data')
    flag = int(request.POST.get('flag'))
    if flag == 0:
        dish_cache = DishCache.objects.get(dish_cache_id=dish_cache_id)
        dish_cache.delete()
    elif flag == 1:
        dish_cache = DishCache.objects.get(dish_cache_id=dish_cache_id)
        dish = Dish.objects.get(dish_id=dish_cache.dish_id)
        dish.name = dish_cache.name
        dish.price = dish_cache.price
        dish.detail = dish_cache.detail
        dish.window_id = dish_cache.window
        # dish.save()
    return render(request, 'review/check.html')


@user_passes_test(lambda u:u.is_staff, login_url='/admin/login')
def window_cache_check(request):
    window_cache_id = request.POST.get('data')
    flag = int(request.POST.get('flag'))
    if flag == 0:
        window_cache = WindowCache.objects.get(window_cache_id=window_cache_id)
        window_cache.delete()
    elif flag == 1:
        window_cache = WindowCache.objects.get(window_cache_id=window_cache_id)
        window = Window.objects.get(window_id=window_cache.window_id)
        window.name = window_cache.name
        window.location = window_cache.location
        window.canteen_id = window_cache.canteen
        # window.save()
    return render(request, 'review/check.html')


@user_passes_test(lambda u:u.is_staff, login_url='/admin/login')
def canteen_cache_check(request):
    canteen_cache_id = request.POST.get('data')
    flag = int(request.POST.get('flag'))
    if flag == 0:
        canteen_cache = CanteenCache.objects.get(canteen_cache_id=canteen_cache_id)
        canteen_cache.delete()
    elif flag == 1:
        canteen_cache = CanteenCache.objects.get(canteen_cache_id=canteen_cache_id)
        canteen = Canteen.objects.get(canteen_id=canteen_cache.canteen_id)
        canteen.name = canteen_cache.name
        canteen.position = canteen_cache.position
        canteen.capacity = canteen_cache.capacity
        canteen.business_hours = canteen_cache.business_hours
        # canteen.save()
    return render(request, 'review/check.html')

