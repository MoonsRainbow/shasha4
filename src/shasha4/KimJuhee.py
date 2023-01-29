import time
import requests
import pandas as pd
from bs4 import BeautifulSoup as bs


# 업종 코드 호출
def get_upjong_list_K():
    #requests를 통한 호출
    url = 'https://finance.naver.com/sise/sise_group.naver?type=upjong'
    response = requests.get(url)

    df = pd.read_html(response.text)[0]
    df = df.dropna()
    df = df.reset_index(drop=True)

    cols = ['upjong_name', '전일대비', '전체', '상승', '보합', '하락', '등락그래프']
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
    df['upjong_code'] = temp
    df = df[['upjong_name', 'upjong_code']]
    return df


# 업종코드를 통한 종목 관련 전체 df
def jongmok_df(upjong_cd):
    sel_url = f'https://finance.naver.com/sise/sise_group_detail.naver?type=upjong&no={upjong_cd}'
    sel_respones = requests.get(sel_url)
    table = pd.read_html(sel_respones.text)[2]

    #결측치 제거
    temp = table.drop(['Unnamed: 11', 'Unnamed: 10', '토론실'], axis = 1)
    temp = temp.drop([0])[0:-2]

    #업종코드 컬럼 추가 및 정렬
    temp['upjong_cd'] = upjong_cd
    temp = temp[['upjong_cd', '종목명', '현재가', '전일비', '등락률', '매수호가', '매도호가', '거래량', '거래대금','전일거래량']]
    temp.columns = ['upjong_cd', 'jongmok_name', '현재가', '전일비', '등락률', '매수호가', '매도호가', '거래량', '거래대금','전일거래량']
    return temp


# 업종코드와 종목이름, 종목코드
def jongmok_list():
    jongmok_lists = []
    for i in get_upjong_list_K()['upjong_code'].to_list():
        url_for_detail = 'https://finance.naver.com/sise/sise_group_detail.naver?type=upjong'
        sub_url = f'{url_for_detail}&no={i}'
        response_detail = requests.get(sub_url)
        df_detail = pd.read_html(response_detail.text)[-1]
        df_detail = df_detail.dropna(how='all', axis=1)
        df_detail = df_detail.dropna(how='all')
        df_detail['upjong_code'] = i
        html = bs(response_detail.text, 'html.parser')
        jongmok_codes = html.select('table > tbody > tr > td > div > a')
        jongmok_code_list = []
        for jongmok_code in jongmok_codes:
            jongmok_code = jongmok_code['href'].split('=')[-1]
            jongmok_code_list.append(jongmok_code)
        df_detail['jongmok_code'] = jongmok_code_list
        cols = [
                'upjong_code', '종목명', '현재가', '전일비',
                '등락률', '거래량', '거래대금' ,'전일거래량',
                '매수호가', '매도호가', 'jongmok_code'
                ]
        df_detail = df_detail[cols]
        df_detail = df_detail.rename(columns={'종목명':'jongmok_name'})
        df_detail = df_detail[['upjong_code', 'jongmok_name', 'jongmok_code']]
        jongmok_lists.append(df_detail)
    jongmok_df = pd.concat(jongmok_lists).reset_index(drop = True)
    return jongmok_df


def get_theme_list():
    '''
    1. 끝 페이지를 번호를 얻기위한 기본 url로 끝페이지 정보 얻기
    2. 반복문으로 첫페이지부터 끝페이지까지 스크래핑
    3. 스크래핑 한 데이터 저장 후 불러오기
    '''
    url_for_end = 'https://finance.naver.com/sise/theme.naver'
    response = requests.get(url_for_end)
    html = bs(response.text, 'html.parser')
    end_page = int(html.select('td.pgRR > a')[0]['href'][-1])

    pages_by_theme = []
    for i in range(1, end_page + 1):
        url = f'https://finance.naver.com/sise/theme.naver?&page={i}'
        # 요청
        response = requests.get(url)
        page = pd.read_html(response.text)[0]

        # 결측치 제거
        page = page.dropna()
        page = page.reset_index(drop=True)

        # 이중컬럼 제거
        cols = ['테마명', '전일대비', '최근3일등락률(평균)', '상승', '보합', '하락', '주도주1', '주도주2']
        page.columns = cols

        # 테마번호 컬럼 추가
        html = bs(response.text, 'html.parser')
        theme_num = []
        for link in html.select('tr > td > a')[:-15][::3]:
            theme_num.append(link['href'].split('=')[-1])

        page['테마번호'] = theme_num

        pages_by_theme.append(page)
        time.sleep(0.001)
    pages_by_theme = pd.concat(pages_by_theme).reset_index(drop=True)
    pages_by_theme = pages_by_theme.rename(columns={'테마명': 'theme_name'})
    pages_by_theme = pages_by_theme.rename(columns={'테마번호': 'theme_code'})
    pages_by_theme = pages_by_theme[['theme_name', 'theme_code']]
    return pages_by_theme
