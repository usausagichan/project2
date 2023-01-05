import pandas as pd
import numpy as np
import jieba_fast as jieba 
data=pd.read_csv('lipstick/文.csv')
#資料前處理
data['貼文']=data['本文']+data['留言']
data=data.drop_duplicates()
data['日期']=pd.to_datetime(data['日期'],errors='ignore')
# 繁體中文專用
jieba.set_dictionary('dict.txt.big.txt')
dic=pd.read_excel('lipstick/關鍵字1.0.xlsx')
feature=dic['關鍵字'].tolist()
for f in feature:
    jieba.add_word(f)
useless=open('stopwords.txt','r')
useless=useless.read()
useless=useless.split('\n')
l=['作者','買','會','開','n','nn','文章','水桶','刪除','置頂','推','日期','留言']
useless=useless+l
removeword = ['span','class','f3','https','imgur','h1','_   blank','href','rel','nofollow','target','cdn','cgi','b4','jpg','hl','b1','f5','f4',
            'goo.gl','f2','email','map','f1','f6','__cf___','data','bbs''html','cf','f0','b2','b3','b5','b6','原文內容','原文連結','作者'
            '標題','時間','看板','<','>','，','。','？','—','閒聊','・','/',' ','=','\"','\n','」','「','！','[',']','：','‧','╦','╔','╗','║'
            ,'╠','╬','╬',':','╰','╩','╯','╭','╮','│','╪','─','《','》' ,'.','、','（','）','　','*','※','~','○','”','“','～','@','＋','\r'
            ,'▁',')','(','-','═','?',',','!','…','&',';','『','』','#','＝','＃','\\','\\n', '"', '的', '^', '︿','＠','$','＄','%','％',
            '＆','＊','＿','+',"'",'{','}','｛','｝','|','｜','．','‵','`','；','●','§','※','○','△','▲','◎','☆','★','◇','◆','□','■','▽',
            '▼','㊣','↑','↓','←','→','↖','XD','XDD','QQ','【','】'
            ]
removeword=removeword
#去除無意義字眼
for word in removeword:
    data['貼文'] = data['貼文'].str.replace(word,'')
#去除空值
data=data.dropna(subset=['貼文'])
data=data[data['貼文']!='']
data['關鍵字']=data['貼文'].apply(lambda x: list(jieba.cut(x))) 
#篩選有除濕機的貼文
data['標＋文']=data['標題']+['本文']
data = data[data['標＋文'].str.contains('唇', na=False)]
# 計算推/噓/中立數
for push in ["'tag': '推'","'tag': '→'","'tag': '噓''" ]:
    data['push_'+push] = data['留言'].str.count(push)

data=data.drop(['標＋文'],axis=1)
def datacsv():
    data.to_csv('lipstick/唇.csv',  encoding='UTF-8-sig')

#存關鍵字
data['貼文']=data['貼文'].astype(str)
data['貼文']=data['貼文'].fillna('')
#各筆資料合併成大字串
string=''.join(data['貼文'].tolist())
word=list(jieba.cut(string))

tag=pd.DataFrame({'tag':word})
tag=pd.DataFrame(tag['tag'].value_counts())
tag=tag.reset_index()
tag.columns=['關鍵字','count']
tag=tag.set_index('關鍵字')
for u in useless:
    try:
        tag=tag.drop(u)
    except:
        pass
def find_tag():
    tag.to_excel('lipstick/tag.xlsx',encoding='UTF-8-sig')
def findclose(word,data):
    select_tags=pd.DataFrame()
    data=data.reset_index()
    densfea=word
    densfea=densfea['關鍵字'].tolist()
    for w in densfea:
        print(w)
        select=data[data['關鍵字'].str.contains(w,na=True)]
        select['對應']=w
        select_tags=pd.concat([select,select_tags],axis=0)
    select_tags.to_csv('lipstick/相似關鍵字.csv',encoding='UTF-8-sig')
cord=pd.read_excel('lipstick/cord.xlsx')
findclose(cord,tag)
datacsv()
find_tag()