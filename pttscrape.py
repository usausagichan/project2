
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

def ptt(page):
    url='https://www.ptt.cc/'+page
    response=requests.get(url)
    soup=BeautifulSoup(response.text,'html.parser')
    next_page=soup.find('div','btn-group-paging').find_all('a')[1]['href'] 
#抓標題和連接
    title=soup.find_all('div',re.compile('title')) #<div class='title'>
    tlist=[]
    linklst=[]
    all=[]
    tags=[]
    for t in title:
        
        if len(t)!=1: #避免出現文章刪除或水桶的錯誤
            if not '公告' in str(t):
                tlist.append(t.text.strip())
                linklst.append('https://www.ptt.cc'+t.a['href'])
#爬文
#若有年滿18歲的限制，ex:gossip，加上header={'cookie':'over18=1'}
#resp=requests.get(url,headers=header)
    header={'cookie':'over18=1'}
    for topic in linklst:
        res=requests.get(topic,headers=header)
        text=BeautifulSoup(res.text,'html.parser')
#抓主文<div id='main-context'>
        maintext=text.find('div',id='main-content')
#抓作者的版、標題、日期 <span class=article-meta-tag>
#<span class="article-meta-value">作者、標題、日期</span>
        try:
            tag=maintext.find_all('span',re.compile('article-meta-value')) 
            author=tag[0].text
            b=tag[1].text
            date=tag[3].text
            ti=tag[2].text
            print(tag)
            tags.append([author,b,date,ti])
        except:
            tags.append(['NA','NA','NA','NA'])
        
#抓主文 待解決：圖片附近的文字爬不到，通常和<div>....</div>一起
        content=str(maintext).split('--\n<span class="f2">※ 發信站')[0]
        content=content.strip()#最後的空行
        content=content.split('</span>')[-1] #取出文章...＋<tag>
        content=content.split('\n')
        context=[]
        for i in content:
            if not '</a>' in i:
                if not '</div>' in i:
                    context.append(i) 
        context='/n'.join(context)

#抓留言
        push=maintext.find_all('div',re.compile('push'))
#抓留言屬性：噓/推 日期
        comment=[]
        for pushs in push:
            push_type=pushs.find('span',re.compile('push-tag')).text.strip(' ') #re.compile:含有...的字串就會被抓出來
            push_user=pushs.find('span',re.compile('push-userid')).text.strip(' ')
            push_content=pushs.find('span',re.compile('push-content')).text.strip(' ')
            push_date=pushs.find('span',re.compile('push-ipdatetime')).text.strip(' \n') #去除前後的空白和後面的換行\n
            try:
                push_date=str(push_date).split(' ')[1]
            except:
                push_date='---'
            #print(topic,pushs,push_date)
            comment.append([push_type,push_user,push_content,push_date])
        attrs=['tag','作者','留言','日期']
        clist=[]
        for c in comment:
            clist.append(dict(zip(attrs,list(c))))
        all.append([context,clist])
    all_1=pd.DataFrame({'標題':tlist,'連結':linklst})
    all_2=pd.DataFrame(all,columns=['本文','留言'])
    all_3=pd.DataFrame(tags,columns=['作者','版','日期','標題(文)'])
    data=pd.concat([all_1,all_2,all_3],axis=1)
    return data,next_page

def scrape(board,page): #board=string, page=int
    datas=[]
    for i in range(page):
        if i==0:
            data,next_page=ptt('bbs/'+board+'/index.html')
            datas.append(data)
        else:
            try:
                data,next_page=ptt(next_page)
                datas.append(data)
            except Exception as e:
                print(e)
                print('error at'+str(i)+'pages before latest page')
                break
    all_df=pd.concat(datas)
    return all_df
#data,next_page=ptt('bbs/E-appliance/index1782.html')
data=scrape('MakeUp',27)
data.to_csv('lipstick/唇.csv')