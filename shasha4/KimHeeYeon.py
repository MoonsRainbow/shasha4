#!/usr/bin/env python
# coding: utf-8

# ## 네이버 금융 많이본 뉴스 일자별 내용 수집하기

# In[1]:


# 페이지 수집 시 필요한 모듈 다운로드

from tqdm.notebook import tqdm
tqdm.pandas()
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from tqdm import trange
import time
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


# In[2]:


# 일자, 페이지 번호 입력해주기

date = 20230120
page_no = 3


# In[3]:


# 페이지 번호를 넘기면 페이지 내용을 수집하는 함수를 만들기(한페이지 스크래핑)

def fn_page_scrapping(date, page_no):
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    
    # 1) 날짜, page 번호로 url 만들기 
    url = "https://finance.naver.com/news/news_list.naver?mode=RANK"
    params = f"mode=RANK&date={date}&page={page_no}"

    # 2) requests.post() 로 요청
    headers = {"user-agent" : "Mozilla/5.0"}
    response = requests.post(url,params=params, headers = headers, verify=False)
   
    # 3) bs 적용
    html = bs(response.text)

    # 4) 테이블 찾기
    df = html.select("#contentarea_left > div > ul > li > ul > li > a")
    page_list = pd.DataFrame(df)
    page_list.columns = ['기사 제목']

    # 5) a 태그 목록 찾기
    a_href = [a["href"] for a in html.select("#contentarea_left > div > ul > li > ul > li > a") ]

    # 6) 내용링크에 a 태그 주소 추가
    page_list["내용링크"] = a_href

    # 7) 데이터 프레임 변환
    return page_list


# In[4]:


# 이전 함수 출력물 중 링크 값 변수 지정
sub_url = fn_page_scrapping(date, page_no).iloc[0]["내용링크"]


# In[77]:


# 내용 스크랩하는 함수 만들기 

def fn_get_conent(sub_url):

    # 1) 수집할 URL 만들기    
    base_url = "https://finance.naver.com"
    url = base_url + sub_url

    # 2) requests로 HTTP 요청하기  
    response = requests.get(url, verify=False)

    # 3) response.text에 BeautifulSoup 적용하기
    html = bs(response.text)

    # 4) 내용 가져오기    
    content = html.find_all("div",{"id":"content"})[0].text

    # 5) time.sleep()
    time.sleep(0.01)

    # 6) 내용 반환하기
    return content[1:-230]


# In[7]:


# 페이지 수집 함수 만들기

def fn_most_viewed_news(date):
    page_list = []

    url = "https://finance.naver.com/news/news_list.naver?mode=RANK" 
    params = f"mode=RANK&date={date}"
    headers = {"user-agent" : "Mozilla/5.0"}
    response = requests.post(url,params=params, headers=headers, verify=False)
    html = bs(response.text)

    last_page = int(html.select("table > tr > td.pgRR > a")[-1]["href"].split("=")[-1])

    for page_no in trange(1, last_page+1):
        result = fn_page_scrapping(date, page_no)
        page_list.append(result)
        time.sleep(0.01)

    pages_list = pd.concat(page_list)
    pages_list = pages_list.reset_index(drop = True)

    contents = []

    for link in pages_list['내용링크']:
        contents.append(fn_get_conent(link))

    pages_list['내용'] = contents
    
    return pages_list


# ## 워드 클라우드 만들기

# In[9]:


# 필요한 모듈 다운로드

get_ipython().system('pip install JPype1')
get_ipython().system('pip install konlpy')
get_ipython().system('pip install wordcloud')

import pandas as pd
from konlpy.tag import Okt # 형태소분석기 : Openkoreatext
from collections import Counter # 빈도 수 세기
from wordcloud import WordCloud, STOPWORDS # wordcloud 만들기
import matplotlib.pyplot as plt # 시각화
import matplotlib as mp

# ### 워드 클라우드1. 기사 [내용]으로 워드 클라우드 만들어 보기

# In[8]:


# 스크래핑 출력물 저장
news = fn_most_viewed_news(date)

# 형태소 분석기를 통해 명사만 추출하기 1글자 명사는 제외
def wc1_get_noun(news):
    
    script = news['내용']
    script.to_csv('word.txt', encoding='utf-8')
    text = open('word.txt', encoding='utf-8').read()
    
    okt=Okt()
    
    return [word for word in okt.nouns(text) if len(word)>1] 

# 함수 출력 값 할당 해주기 
noun = wc1_get_noun(news)

# 중복 단어 배제, wordcloud 만들기

def wc1_make_wc(noun):
    
    count = Counter(noun)
    word = dict(count.most_common(200))

    stopwords = set(STOPWORDS)

    wc = WordCloud(max_font_size=200,
        font_path = 'C:/Users/user/AppData/Local/Microsoft/Windows/Fonts/HANBatang.ttf',
        background_color="white",
        width=2000, height=500,
        stopwords =stopwords ).generate_from_frequencies(word) 
    
    plt.figure(figsize = (40,40))
    plt.imshow(wc)
    plt.tight_layout(pad=0)
    plt.axis('off')

    return plt.show()


# ### 워드 클라우드2. 기사 [기사 제목]으로 워드 클라우드 만들어 보기

# In[92]:


# 스크래핑 출력물 저장
news = fn_most_viewed_news(date)

# 형태소 분석기를 통해 명사만 추출하기 1글자 명사는 제외
def wc2_get_noun(news):
    
    script = news['기사 제목']
    script.to_csv('word.txt', encoding='utf-8')
    text = open('word.txt', encoding='utf-8').read()
    
    okt=Okt()
    
    return [word for word in okt.nouns(text) if len(word)>1] 

# 함수 출력 값 할당 해주기 
noun = wc2_get_noun(news)

# 중복 단어 배제, wordcloud 만들기

def wc2_make_wc(noun2):
    
    count = Counter(noun)
    word = dict(count.most_common(200))

    stopwords = set(STOPWORDS)

    wc = WordCloud(max_font_size=200,
        font_path = 'C:/Users/user/AppData/Local/Microsoft/Windows/Fonts/HANBatang.ttf',
        background_color="white",
        width=2000, height=500,
        stopwords =stopwords ).generate_from_frequencies(word) 
    
    plt.figure(figsize = (40,40))
    plt.imshow(wc)
    plt.tight_layout(pad=0)
    plt.axis('off')

    return plt.show()


# ## 뉴스 내용 스크래핑 확인 작업

# ### 1. 페이지 스크래핑 함수 작동 확인 
# ![image.png](attachment:image.png)

# In[14]:


# 1. 페이지 스크래핑 함수 

fn_page_scrapping(20230128, 3)


# ### 2. 내용 스크래핑 함수 작동 확인
# ![image-2.png](attachment:image-2.png)

# In[80]:


# 2. 내용 스크래핑 함수

sub_url = fn_page_scrapping(20230122, 3).iloc[0]["내용링크"]
fn_get_conent(sub_url)


# ### 3. 페이지 수집 함수 확인
# 
# ![image.png](attachment:image.png)

# In[81]:


# 3. 페이지 수집함수

fn_most_viewed_news(20230126)


# ## 워드 클라우드 확인작업

# ### 워드 클라우드 1. [내용]기준 작업물 확인
# 
# #### 결과 값을 통해 2023.01.26 네이버 증권 이슈 키워드는 '미국', '하락', '넷플릭스' 등이 있음을 알 수 있음. 

# In[94]:


# 내용 출력물 저장
news = fn_most_viewed_news(date)

# 명사만 추출, 1글자 명사는 제외
wc1_get_noun(news)

# 함수 출력 값 할당 해주기 
noun = wc1_get_noun(news)

# 중복 단어 배제, wordcloud 만들기
wc1_make_wc(noun)


# ### 워드 클라우드 2. [기사 제목]기준 작업물 확인
# 
# #### 결과 값을 통해 2023.01.26 네이버 증권 이슈 키워드는 '넷플릭스', '하락', '중국', '금리' 등이 있음을 알 수 있음. 그리고, [내용]을 이용한 워드클라우드 보다 [기사 제목]을 이용한 워드클라우드가 핵심 정보를 전달하는데 용이한 것 같다.

# In[93]:


# 내용 출력물 저장
news = fn_most_viewed_news(date)

# 명사만 추출, 1글자 명사는 제외
wc2_get_noun(news)

# 함수 출력 값 할당 해주기 
noun = wc2_get_noun(news)

# 중복 단어 배제, wordcloud 만들기
wc2_make_wc(noun)

