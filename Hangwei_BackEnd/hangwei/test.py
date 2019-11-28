import sys
sys.path.append('/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/fuzzymatch/')
from main import *
result,maxword = fuzzy_search('yidali')
dish_intro,dish_name = get_dish_intro()
if(maxword!=None):
    print('您是不是想搜：'+maxword)
    for i in range(len(result)):
        print(result[i], dish_intro[result[i]])
else:
    for i in range(len(result)):
        print(dish_intro[result[i]])