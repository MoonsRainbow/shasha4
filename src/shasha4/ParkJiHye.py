import requests
import pandas as pd
from datetime import date
from bs4 import BeautifulSoup as bs


# 업종별 시세 페이지 호출
def get_upjong_list_P():
    #requests를 통한 호출
    url = 'https://finance.naver.com/sise/sise_group.naver?type=upjong'
    response = requests.get(url)

    df = pd.read_html(response.text)[0]
    df = df.dropna()
    df = df.reset_index(drop=True)

    cols = ['업종명', '전일대비', '전체', '상승', '보합', '하락', '등락그래프']
    df.columns = cols
    df = df.drop('등락그래프', axis=1)
    df[['전체', '상승', '보합', '하락']] = df[['전체', '상승', '보합', '하락']].astype(int)

    html = bs(response.text, 'html.parser')
    link_list = html.select('td > a')
    link_list = link_list[:-5]
    temp = []

    for i in link_list :
        temp.append(i['href'].split("=")[2])

    # 업종코드 추가
    df["업종코드"] = temp
    return df


# 각 업종별 URL 추출 함수
def get_url(upjong_cd):
    '''
    1. 기본 URL 생성
    2. 파라미터를 통해 URL 변경
    3. return URL
    '''
    URL = 'https://finance.naver.com/sise/sise_group_detail.naver?type=upjong&no='
    return URL + upjong_cd


# 각 업종별 페이지 스크래핑 함수

def get_scrap_upjongcd(upjong_cd):
    '''
    1. URL 생성
    2. request 요청
    3. response를 데이터프레임으로 생성
    4. return 데이터프레임
    '''

    # requests를 통한 호출
    url = get_url(upjong_cd)
    response = requests.get(url)

    df = pd.read_html(response.text)[2]
    df = df.dropna(how='all')
    df = df.dropna(how='all')
    df = df.dropna(axis=1)
    df = df.reset_index(drop=True)
    cols = ['종목명', '현재가', '전일비', '등락률', '매수호가', '매도호가', '거래량', '거래대금', '전일거래량']
    df.columns = cols

    # 업종별 호출
    # 79rows
    return df


# 결과값 csv 파일로 저장
def save_file_csv(df, code=0):
    '''
    1. 파일명 설정
    2. 파일 저장
    3. 파일 확인
    '''

    today = date.today()
    dt = today.strftime("%y%m%d")

    # 업종리스트, 업종별에 따라 파일명 설정
    if (code == 0) & (df.columns[0] == '업종명'):
        file_name = f"industry_{dt}.csv"
    elif (code != 0) & (df.columns[0] == '종목명'):
        file_name = f"sector{code}_{dt}.csv"
    else:
        file_name = f"noname_{dt}.csv"

    # 파일 저장
    df.to_csv(file_name, index=False)

    # 파일 확인
    try:
        display(pd.read_csv(file_name))
    except:
        pass
