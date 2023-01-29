import time
import requests
import pandas as pd
from tqdm import trange
from konlpy.tag import Okt  # 형태소분석기 : Openkoreatext
from tqdm.notebook import tqdm
import matplotlib.pyplot as plt  # 시각화
from collections import Counter  # 빈도 수 세기
from bs4 import BeautifulSoup as bs
from wordcloud import WordCloud, STOPWORDS  # wordcloud 만들기


font_path = './HANBATANG.TTF'
tqdm.pandas()
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


def fn_page_scrapping(date, page_no):
    # 1) 날짜, page 번호로 url 만들기 
    url = "https://finance.naver.com/news/news_list.naver?mode=RANK"
    params = f"mode=RANK&date={date}&page={page_no}"

    # 2) requests.post() 로 요청
    headers = {"user-agent": "Mozilla/5.0"}
    response = requests.post(url, params=params, headers=headers, verify=False)
   
    # 3) bs 적용
    html = bs(response.text, 'html.parser')

    # 4) 테이블 찾기
    df = html.select("#contentarea_left > div > ul > li > ul > li > a")
    page_list = pd.DataFrame(df)
    page_list.columns = ['기사 제목']

    # 5) a 태그 목록 찾기
    a_href = [a["href"] for a in html.select("#contentarea_left > div > ul > li > ul > li > a")]

    # 6) 내용링크에 a 태그 주소 추가
    page_list["내용링크"] = a_href

    # 7) 데이터 프레임 변환
    return page_list


def fn_get_content(link):
    # 1) 수집할 URL 만들기    
    base_url = "https://finance.naver.com"
    url = base_url + link

    # 2) requests로 HTTP 요청하기  
    response = requests.get(url, verify=False)

    # 3) response.text에 BeautifulSoup 적용하기
    html = bs(response.text, 'html.parser')

    # 4) 내용 가져오기    
    content = html.find_all("div", {"id": "content"})[0].text

    # 5) time.sleep()
    time.sleep(0.01)

    # 6) 내용 반환하기
    return content[1:-230]


def fn_most_viewed_news(date):
    page_list = []

    url = "https://finance.naver.com/news/news_list.naver?mode=RANK" 
    params = f"mode=RANK&date={date}"
    headers = {"user-agent": "Mozilla/5.0"}
    response = requests.post(url, params=params, headers=headers, verify=False)
    html = bs(response.text, 'html.parser')

    last_page = int(html.select("table > tr > td.pgRR > a")[-1]["href"].split("=")[-1])

    for page_no in trange(1, last_page+1):
        result = fn_page_scrapping(date, page_no)
        page_list.append(result)
        time.sleep(0.01)

    pages_list = pd.concat(page_list)
    pages_list = pages_list.reset_index(drop=True)

    contents = []

    for link in pages_list['내용링크']:
        contents.append(fn_get_content(link))

    pages_list['내용'] = contents
    
    return pages_list


def wc1_get_noun(date):
    # 스크래핑 출력물 저장
    news = fn_most_viewed_news(date)

    script = news['내용']
    script.to_csv('word.txt', encoding='utf-8')
    text = open('word.txt', encoding='utf-8').read()
    
    okt = Okt()
    
    return [word for word in okt.nouns(text) if len(word) > 1]


# 중복 단어 배제, wordcloud 만들기
def wc1_make_wc(date):
    
    # 함수 출력 값 할당 해주기 
    noun = wc1_get_noun(date)
    
    count = Counter(noun)
    word = dict(count.most_common(200))

    stopwords = set(STOPWORDS)

    wc = WordCloud(max_font_size=200,
                   background_color="white",
                   width=2000, height=500,
                   stopwords=stopwords).generate_from_frequencies(word)
    
    plt.figure(figsize=(40, 40))
    plt.imshow(wc)
    plt.tight_layout(pad=0)
    plt.axis('off')

    return plt.show()


# ### 워드 클라우드2. 기사 [기사 제목]으로 워드 클라우드 만들어 보기

# In[27]:


# 형태소 분석기를 통해 명사만 추출하기 1글자 명사는 제외
def wc2_get_noun(date):
    
    # 스크래핑 출력물 저장
    news = fn_most_viewed_news(date)
    
    script = news['기사 제목']
    script.to_csv('word2.txt', encoding='utf-8')
    text = open('word2.txt', encoding='utf-8').read()
    
    okt = Okt()
    
    return [word for word in okt.nouns(text) if len(word) > 1]


# 중복 단어 배제, wordcloud 만들기
def wc2_make_wc(date):
    
    # 함수 출력 값 할당 해주기 
    noun = wc2_get_noun(date)
    
    count = Counter(noun)
    word = dict(count.most_common(200))

    stopwords = set(STOPWORDS)

    wc = WordCloud(max_font_size=200,
                   background_color="white",
                   width=2000, height=500,
                   stopwords=stopwords).generate_from_frequencies(word)
    
    plt.figure(figsize=(40, 40))
    plt.imshow(wc)
    plt.tight_layout(pad=0)
    plt.axis('off')

    return plt.show()
