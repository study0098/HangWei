import pickle
with open('comment_tag.pkl','rb') as f:
     dishdict = pickle.load(f)
for i in dishdict:
    print(i)