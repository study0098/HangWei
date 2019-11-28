import sys
sys.path.append('/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/opinion/opinion_mining/processing/')
sys.path.append('/root/Hangwei_BackEnd/Hangwei_BackEnd/hangwei/recommend/')
import produce
import recommend
def commentlabel():
    labeldict = produce.main()
    return labeldict
def dishrecommend():
    recdict = recommend.main()
    return recdict
if __name__ == '__main__':
    print(commentlabel())
    print(dishrecommend())