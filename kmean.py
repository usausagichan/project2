import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt


similar=pd.read_excel('lipstick/字典.xlsx')
color=pd.read_excel('lipstick/顏色.xlsx')
l=similar['對應'].unique().tolist() #字庫
colors=color['色對'].unique().tolist()
palete=color['色系'].unique().tolist()
#brand=pd.read_csv('除濕機＿品牌.csv')
#brand=brand['牌'].unique().tolist()

w=9 #留言權重
r=1 #kmean's random state
data=pd.read_csv('lipstick/唇.csv')
data['聲量']=data.filter(regex="push_'tag'").sum(axis=1)
data['num']=range(1,len(data)+1)
#拆留言 eval:轉換度不同型態object-> list
quote=[]
for i in data['num']:
    datatmp=data[data['num']==i]
    try:
        q=pd.DataFrame(eval(datatmp['留言'].iloc[0]))
        q['標題']=datatmp['標題'].iloc[0]
        q['本文']=datatmp['本文'].iloc[0]
        q['聲量']=datatmp['聲量'].iloc[0]
        quote.append(q)
    except Exception as e:
        print(e)
data=pd.concat(quote)
data['貼文']=(data['標題']+data['本文'])+w*data['留言']
print(data['貼文'])
for i in l:
    data[i]=0
for i in range(similar.shape[0]):
    c=data['貼文'].str.count(similar['關鍵字'][i])
    key=similar['對應'][i]
    data[key]+=c

for i in colors:
    data[i]=0
for i in range(color.shape[0]):
    c=data['貼文'].str.count(color['顏色'][i])
    key=color['色對'][i]
    data[key]+=c
for i in palete:
    data[i]=0
for i in range(color.shape[0]):
    c=data['貼文'].str.count(color['顏色'][i])
    key=color['色系'][i]
    data[key]+=c
data_clust=data.groupby(['作者']).sum()

#.drop(['tag'],axis=1)

#kmean_find best k
def find_best(data_cluster,n):
    distortion=[]
    K=range(1,n)
    for k in K:
        model=KMeans(n_clusters=k,random_state=r)
        model.fit(data_cluster)
        distortion.append(model.inertia_)

    plt.figure(figsize=(16,8))
    plt.plot(K, distortion, 'bx-')
    plt.xlabel('k')
    plt.ylabel('Distortion')
    plt.title('The Elbow Method showing the optimal k')
    plt.savefig('lipstick/learning_curve.png')

#select n finally
def fit(data_cluster,n):
    model=KMeans(n_clusters=n,random_state=r)
    model.fit(data_cluster)
    data_cluster['群']=model.labels_
    #data_cluster=data_cluster.reset_index()
    return data_cluster
#每群人數
def calculate(data_cluster,l):
    
    market_pop=data_cluster.groupby(['群']).count()
#每群人feature加總
#drop=brand
    feature_count=data_cluster.groupby(['群']).sum()
    feature_count=feature_count[l].T
    return market_pop,feature_count
# for x in drop:
#     feature_count=feature_count.drop(x)
# #market_feature_list = calculate_segment_features(feature_count)
def cat(data_cluster):
    market_pop,feature_count=calculate(data_cluster,l=l)
    d=pd.DataFrame()
    for i in range(feature_count.shape[1]):
        seg=feature_count[i].sort_values(ascending=False)
        seg=pd.DataFrame(seg).reset_index()
        seg['percent']=round(seg[i]/seg[i].sum()*100,2)
        seg['cumsum_percent']=seg['percent'].cumsum()
        
    # market_feature=seg['index'][0:5].tolist()
        seg.to_excel('lipstick/coef'+str(i)+'.xlsx')
        dt=seg[['index','percent']]
        dt=dt.rename(columns={'index':'index'+str(i),'percent':'percent'+str(i)})
        d=pd.concat([d,dt],axis=1)
    market_pop.to_excel('lipstick/groupcount.xlsx')
    d.to_excel('lipstick/data.xlsx')
        
#find_best(data_cluster,15)
data_clust=data_clust.reset_index()
data_cluster=data_clust[l]
data=fit(data_cluster=data_cluster,n=6)
cat(data)
data_clust['群']=data['群']
# l.extend('群')
# colors.append('群')
# palete.append('群')

# data_clust[l].T.to_excel('lipstick/visualization/feature.xlsx')
# data_clust[colors].T.to_excel('lipstick/visualization/colors.xlsx')
# data_clust[palete].T.to_excel('lipstick/visualization/palete.xlsx')

market_pop,f_color=calculate(data_cluster=data_clust,l=colors)
f_color.to_excel('lipstick/color.xlsx')
__,f_palete=calculate(data_cluster=data_clust,l=palete)
f_color.to_excel('lipstick/色系.xlsx')
p=color[['色對','色系']]
p=p.drop_duplicates()

#market_pop.iloc[2,1]
for i in range(6):
    f_color.iloc[:,i]=f_color.iloc[:,i]/market_pop.iloc[i,1]
f_color.rename(columns={'index':'色對'},inplace=True)
dp=f_color.join(p.set_index('色對'))
dp.to_excel('lipstick/色色.xlsx')