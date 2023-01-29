# 필요한 모듈 불러오기
import requests
import pandas as pd
from tqdm.notebook import tqdm
from bs4 import BeautifulSoup as bs

tqdm.pandas()
pd.set_option('display.max_row', 500)
pd.set_option('display.max_columns', 150)


# 실시간 검색어 순위 가져오기
def get_top_stock():
    # url 생성
    url = 'https://finance.naver.com/sise/lastsearch2.naver'

    #response 받기
    headers = {'user-agent' : 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)

    # 데이터 프레임 생성
    df_top_stocks = pd.read_html(response.text)[1]
    df_top_stocks = df_top_stocks.dropna(how='all')
    df_top_stocks = df_top_stocks.reset_index(drop=True)

    # 코드를 찾아서 추가하기
    find_tag = bs(response.text, 'html.parser')
    code = []
    for i in find_tag.select('td > a'):
        code.append(i["href"].split("=")[-1])

    # 불필요 데이터 제거 / 추후에 데이터를 추가 예정
    df_top_stocks["업종코드"] = code
    df_top_stocks = df_top_stocks.drop("전일비", axis=1)
    df_top_stocks = df_top_stocks.drop("등락률", axis=1)
    df_top_stocks = df_top_stocks.drop("거래량", axis=1)
    df_top_stocks = df_top_stocks.drop("현재가", axis=1)
    df_top_stocks = df_top_stocks.drop("시가", axis=1)
    df_top_stocks = df_top_stocks.drop("고가", axis=1)
    df_top_stocks = df_top_stocks.drop("저가", axis=1)
    df_top_stocks = df_top_stocks.drop("PER", axis=1)
    df_top_stocks = df_top_stocks.drop("ROE", axis=1)
    df_top_stocks = df_top_stocks[["순위", "업종코드", "종목명", "검색비율"]]

    return df_top_stocks


# 종목코드를 이용하여 시세 데이터 가져오기
def get_stock_sise(stock_code):
    # url 생성
    stock_url = f"https://finance.naver.com/item/sise.naver?code={stock_code}"
    headers = {'user-agent' : 'Mozilla/5.0'}
    
    #response 받기
    response2 = requests.get(stock_url, headers=headers)
    
    # 테이블 생성
    juyo_sise = pd.read_html(response2.text)[1]
    juyo_sise = juyo_sise.dropna()
    juyo_sise = juyo_sise.reset_index(drop=True)
    
    # 테이블 형태 변경
    t1 = juyo_sise[[0, 1]].set_index(0).T
    t2 = juyo_sise[[2, 3]].set_index(2).T
    t2.index = t1.index
    juyo_sise = pd.concat([t1, t2], axis=1)
   
    return juyo_sise
