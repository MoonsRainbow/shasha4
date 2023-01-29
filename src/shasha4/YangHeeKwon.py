import time
import requests
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup as bs


# 업종별 순위(rank_upjong()), 요약정보(get_summary()), 세부정보get_detail(), 베스트5워스트5(best5(), worst5_())
# 를 스크래핑 하는 클래스
# 클래스의 목적 : 주식의 정보를 그룹별로 파악하기 쉽게 볼 수 있도록 하는 것
class Upjong:
    def __init__(self, upjong_nm, upjong_num):
        self.upjong_nm = upjong_nm
        self.upjong_num = upjong_num
        plt.rcParams['font.family'] = 'Malgun Gothic'

    @staticmethod
    def get_page_sise_by_upjong():
        '''
        업종별 시세 페이지를 스크래핑하는 함수
        '''
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
        upjong_no = [link['href'].split('&')[-1].replace('no=','') for link in html.select('td > a')[:-5]]
        df['업종번호'] = upjong_no

        today_date = datetime.today().strftime('%Y-%m-%d')
        file_name = f'업종별시세-{today_date}.csv'
        df.to_csv(f'data/{file_name}', index=False)
        df = pd.read_csv(f'data/{file_name}', dtype={'업종번호': object})
        return df

    def rank_upjong(self):
        right_now = datetime.today().strftime('%Y-%m-%d %X')
        sise_by_upjong = Upjong.get_page_sise_by_upjong()
        total_upjong = sise_by_upjong.shape[0]
        today_rank = sise_by_upjong[sise_by_upjong['업종명'] == self.upjong_nm].index[0] + 1
        print(f'{self.upjong_nm}의 {right_now} 현재 전일대비 등락률 순위는 {total_upjong}종목중 {today_rank}위 입니다!')
    
    def get_summary(self):
        right_now = datetime.today().strftime('%Y-%m-%d %X')
        before_summary = Upjong.get_page_sise_by_upjong()
        summary = before_summary[before_summary['업종명'] == self.upjong_nm]
        print(f'{right_now} 현재 {self.upjong_nm} 업종의 요약정보입니다!')
        
        plt.figure(figsize=(6, 6))
        ratio = [summary.iloc[0, 3], summary.iloc[0, 4], summary.iloc[0, 5]]
        labels = ['상승', '보합', '하락']
        explode = [0.40, 0.20, 0.00]
        colors = ['red', 'grey', 'blue']
        patches, texts, autotexts = plt.pie(ratio, explode=explode, colors=colors, autopct='%.1f%%', textprops={'size': 9})
        plt.legend(labels)
        
        for t in autotexts:
            t.set_color("white")
            t.set_fontsize(12)
        plt.show()
        
        plt.show()
        
        return summary
    
    def get_detail(self):
        url_for_detail = 'https://finance.naver.com/sise/sise_group_detail.naver?type=upjong'
        sub_url = f'{url_for_detail}&no={self.upjong_num}'
        response_detail = requests.get(sub_url)
        
        df_for_detail = Upjong.get_page_sise_by_upjong()
        df_detail = pd.read_html(response_detail.text)[-1]
        df_detail = df_detail.dropna(how='all', axis=1)
        df_detail = df_detail.dropna(how='all')
        df_detail['업종명'] = df_for_detail[df_for_detail['업종번호'] == self.upjong_num]['업종명'].iloc[0]
        df_detail = df_detail.reset_index(drop=True)
        cols = [
                '업종명', '종목명', '현재가', '전일비',
                '등락률', '거래량', '거래대금' ,'전일거래량',
                '매수호가', '매도호가'
                ]
        df_detail = df_detail[cols]
        
        cols_int = ['현재가', '전일비', '거래량', '거래대금', '전일거래량', '매수호가', '매도호가']
        df_detail[cols_int] = df_detail[cols_int].astype(int)
        return df_detail
    
    def best5(self):
        right_now = datetime.today().strftime('%Y-%m-%d %X')
        best5 = Upjong.get_detail(self).head(5)
        if best5.shape[0] < 5:
            print('해당 업종 내 기업이 5개 미만 입니다!')
            print(f'{right_now} 현재 {self.upjong_nm} 업종의 모든 기업정보입니다!')
            return best5
        else:
            print(f'{right_now} 현재 {self.upjong_nm} 업종의 전일대비 등락률 best5기업입니다!')
            
            # 막대그래프
            plt.figure(figsize=(9, 6))
            x = best5['종목명']
            y = best5['현재가']
            plt.xlabel('종목명')
            plt.ylabel('현재가')

            plt.bar(x, y, color='red')
            for i, v in enumerate(x):
                plt.text(v, y[i], f'{i+1}위 : ' + best5['등락률'][i],
                         fontsize=12,
                         color="red",
                         horizontalalignment='center',
                         verticalalignment='bottom')

            plt.show()
            return best5
    
    def worst5(self):
        right_now = datetime.today().strftime('%Y-%m-%d %X')
        worst5 = Upjong.get_detail(self)
        r_idx = [i for i in range(worst5.shape[0]-1, -1, -1)]
        worst5 = pd.DataFrame(worst5, index=r_idx).reset_index(drop=True)
        worst5 = worst5.head(5)
        if worst5.shape[0] < 5:
            print('해당 업종 내 기업이 5개 미만 입니다!')
            print(f'{right_now} 현재 {self.upjong_nm} 업종의 모든 기업정보입니다!')
            
            return worst5
        else:
            print(f'{right_now} 현재 {self.upjong_nm} 업종의 전일대비 등락률 worst5기업입니다!')

            # 막대그래프
            plt.figure(figsize=(9, 6))
            x = worst5['종목명']
            y = worst5['현재가']
            plt.xlabel('종목명')
            plt.ylabel('현재가')

            plt.bar(x, y, color = 'blue')
            for i, v in enumerate(x):
                plt.text(v, y[i], f'{i+1}위 : ' + worst5['등락률'][i],
                         fontsize=12,
                         color="blue",
                         horizontalalignment='center',
                         verticalalignment='bottom')

            plt.show()
            
            return worst5


# 테마별 순위(rank_theme()), 요약정보(get_summary()), 세부정보get_detail(), 베스트5워스트5(best5(), worst5())
# 를 스크래핑 하는 클래스
# 클래스의 목적 : 주식의 정보를 테마별로 파악하기 쉽게 볼 수 있도록 하는 것
class Theme:
    def __init__(self, theme_nm, theme_num):
        self.theme_nm = theme_nm
        self.theme_num = theme_num
        plt.rcParams['font.family'] = 'Malgun Gothic'

    @staticmethod
    def get_pages_sise_by_theme():
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
        for i in range(1, end_page+1):
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

            #  테마내 전체 기업 수를 알기 위해 전체 컬럼 추가
            page['전체'] = page['상승'] + page['보합'] + page['하락']

            # 컬럼 순서 정리

            cols = ['테마명', '전일대비', '최근3일등락률(평균)', '전체', '상승', '보합', '하락', '주도주1', '주도주2']
            page = page[cols]

            # 상승, 보합, 하락 컬럼 데이터타입 정수형으로 변환
            page[['전체', '상승', '보합', '하락']] = page[['전체', '상승', '보합', '하락']].astype(int)

            # 테마번호 컬럼 추가
            html = bs(response.text, 'html.parser')
            theme_num = []
            for link in html.select('tr > td > a')[:-15][::3]:
                theme_num.append(link['href'].split('=')[-1])

            page['테마번호'] = theme_num

            pages_by_theme.append(page)

            time.sleep(0.001)
        pages_by_theme = pd.concat(pages_by_theme).reset_index(drop=True)    

        today_date = datetime.today().strftime('%Y-%m-%d')
        file_name = f'테마별시세-{today_date}.csv'
        pages_by_theme.to_csv(f'data/{file_name}', index=False)
        pages_by_theme = pd.read_csv(f'data/{file_name}', dtype={'테마번호':object})

        return pages_by_theme
    
    def rank_theme(self):
        right_now = datetime.today().strftime('%Y-%m-%d %X')
        sise_by_theme = Theme.get_pages_sise_by_theme()
        total_theme = sise_by_theme.shape[0]
        today_rank = sise_by_theme[sise_by_theme['테마명'] == self.theme_nm].index[0] + 1
        print(f'{self.theme_nm}의 {right_now} 현재 전일대비 등락률 순위는 {total_theme}종목중 {today_rank}위 입니다!')

    def get_summary(self):
        right_now = datetime.today().strftime('%Y-%m-%d %X')
        before_summary = Theme.get_pages_sise_by_theme()
        summary = before_summary[before_summary['테마명'] == self.theme_nm]
        print(f'{right_now} 현재 {self.theme_nm} 테마의 요약정보입니다!')
        
        # 파이차트
        plt.figure(figsize=(6, 6))
        ratio = [summary.iloc[0, 4], summary.iloc[0, 5], summary.iloc[0, 6]]
        labels = ['상승', '보합', '하락']
        explode = [0.40, 0.20, 0.00]
        colors = ['red', 'grey', 'blue']
        patches, texts, autotexts = plt.pie(ratio, explode=explode, colors=colors, autopct='%.1f%%', textprops={'size': 9})
        plt.legend(labels)
        for t in autotexts:
            t.set_color("white")
            t.set_fontsize(12)
        plt.show()
        
        return summary

    def get_detail(self):
        base_url = 'https://finance.naver.com/sise/sise_group_detail.naver?type=theme&no='
        sub_url = f'{base_url}{self.theme_num}'
        response_detail = requests.get(sub_url)
        
        df_for_detail = Theme.get_pages_sise_by_theme()
        df_detail = pd.read_html(response_detail.text)[-1]
        df_detail = df_detail.dropna(how='all', axis=1)
        df_detail = df_detail.dropna(how='all')
        df_detail['테마명'] = df_for_detail[df_for_detail['테마번호'] == self.theme_num]['테마명'].iloc[0]
        df_detail = df_detail.reset_index(drop=True)
        cols = [
                '테마명', '종목명', '현재가', '전일비',
                '등락률', '거래량', '거래대금','전일거래량',
                '매수호가', '매도호가'
                ]
        df_detail = df_detail[cols]
        
        cols_int = ['현재가', '전일비', '거래량', '거래대금', '전일거래량', '매수호가', '매도호가']
        df_detail[cols_int] = df_detail[cols_int].astype(int)
        return df_detail
        
    def best5(self):
        right_now = datetime.today().strftime('%Y-%m-%d %X')
        best5 = Theme.get_detail(self).head(5)
        if best5.shape[0] < 5:
            print('해당 테마 내 기업이 5개 미만 입니다!')
            print(f'{right_now} 현재 {self.theme_nm} 테마의 모든 기업정보입니다!')
            return best5
        else:
            print(f'{right_now} 현재 {self.theme_nm} 테마의 전일대비 등락률 best5기업입니다!')
            
            # 막대그래프
            plt.figure(figsize=(9, 6))
            x = best5['종목명']
            y = best5['현재가']
            plt.xlabel('종목명')
            plt.ylabel('현재가')

            plt.bar(x, y, color = 'red')
            for i, v in enumerate(x):
                plt.text(v, y[i], f'{i+1}위 : ' + best5['등락률'][i],
                         fontsize=12,
                         color="red",
                         horizontalalignment='center',
                         verticalalignment='bottom')

            plt.show()
            
            return best5
    
    def worst5(self):
        right_now = datetime.today().strftime('%Y-%m-%d %X')
        worst5= Theme.get_detail(self)
        r_idx = [i for i in range(worst5.shape[0]-1, -1, -1)]
        worst5 = pd.DataFrame(worst5, index=r_idx).reset_index(drop=True)
        worst5 = worst5.head(5)
        if worst5.shape[0] < 5:
            print('해당 테마 내 기업이 5개 미만 입니다!')
            print(f'{right_now} 현재 {self.theme_nm} 테마의 모든 기업정보입니다!')
            
            return worst5
        else:
            print(f'{right_now} 현재 {self.theme_nm} 테마의 전일대비 등락률 worst5기업입니다!')
            
            # 막대그래프
            plt.figure(figsize=(9, 6))
            x = worst5['종목명']
            y = worst5['현재가']
            plt.xlabel('종목명')
            plt.ylabel('현재가')

            plt.bar(x, y, color = 'blue')
            for i, v in enumerate(x):
                plt.text(v, y[i], f'{i+1}위 : ' + worst5['등락률'][i],
                         fontsize=12,
                         color="blue",
                         horizontalalignment='center',
                         verticalalignment='bottom')

            plt.show()
            
            return worst5

        
# 그룹사별 순위(rank_groupsa()), 요약정보(get_summary()), 세부정보get_detail(), 베스트3워스트3(best3(), worst3())
# 를 스크래핑 하는 클래스
# 클래스의 목적 : 주식의 정보를 그룹사별로 파악하기 쉽게 볼 수 있도록 하는 것
class Groupsa:
    def __init__(self, group_nm, group_num):
        self.group_nm = group_nm
        self.group_num = group_num
        plt.rcParams['font.family'] = 'Malgun Gothic'

    @staticmethod
    def get_page_sise_by_group():
        '''
        그룹사별 시세 페이지를 스크래핑하는 함수
        '''
        url = 'https://finance.naver.com/sise/sise_group.naver?type=group'
        response = requests.get(url)
        df = pd.read_html(response.text)[0]
        df = df.dropna()
        df = df.reset_index(drop=True)
        cols = ['그룹명', '전일대비', '전체', '상승', '보합', '하락', '등락그래프']
        df.columns = cols
        df = df.drop('등락그래프', axis=1)
        df[['전체', '상승', '보합', '하락']] = df[['전체', '상승', '보합', '하락']].astype(int)

        html = bs(response.text, 'html.parser')
        group_no = [link['href'].split('&')[-1].replace('no=','') for link in html.select('td > a')[:-5]]
        df['그룹번호'] = group_no

        today_date = datetime.today().strftime('%Y-%m-%d')
        file_name = f'그룹별시세-{today_date}.csv'
        df.to_csv(f'data/{file_name}', index=False)
        df = pd.read_csv(f'data/{file_name}', dtype={'그룹번호': object})
        return df

    def rank_groupsa(self):
        right_now = datetime.today().strftime('%Y-%m-%d %X')
        sise_by_group = Groupsa.get_page_sise_by_group()
        total_group = sise_by_group.shape[0]
        today_rank = sise_by_group[sise_by_group['그룹명'] == self.group_nm].index[0] + 1
        print(f'{self.group_nm}의 {right_now} 현재 전일대비 등락률 순위는 {total_group}그룹중 {today_rank}위 입니다!')
    
    def get_summary(self):
        right_now = datetime.today().strftime('%Y-%m-%d %X')
        before_summary = Groupsa.get_page_sise_by_group()
        summary = before_summary[before_summary['그룹명'] == self.group_nm]
        print(f'{right_now} 현재 {self.group_nm} 그룹의 요약정보입니다!')
        
        plt.figure(figsize=(6, 6))
        ratio = [summary.iloc[0, 3], summary.iloc[0, 4], summary.iloc[0, 5]]
        labels = ['상승', '보합', '하락']
        explode = [0.40, 0.20, 0.00]
        colors = ['red', 'grey', 'blue']
        patches, texts, autotexts = plt.pie(ratio, explode=explode, colors=colors, autopct='%.1f%%', textprops={'size': 9})
        plt.legend(labels)
        
        for t in autotexts:
            t.set_color("white")
            t.set_fontsize(12)
        plt.show()
        
        plt.show()
        
        return summary
    
    def get_detail(self):
        url_for_detail = 'https://finance.naver.com/sise/sise_group_detail.naver?type=group'
        sub_url = f'{url_for_detail}&no={self.group_num}'
        response_detail = requests.get(sub_url)
        
        df_for_detail = Groupsa.get_page_sise_by_group()
        df_detail = pd.read_html(response_detail.text)[-1]
        df_detail = df_detail.dropna(how='all', axis=1)
        df_detail = df_detail.dropna(how='all')
        df_detail['그룹명'] = df_for_detail[df_for_detail['그룹번호'] == self.group_num]['그룹명'].iloc[0]
        df_detail = df_detail.reset_index(drop=True)
        cols = [
                '그룹명', '종목명', '현재가', '전일비',
                '등락률', '거래량', '거래대금','전일거래량',
                '매수호가', '매도호가'
                ]
        df_detail = df_detail[cols]
        
        cols_int = ['현재가', '전일비', '거래량', '거래대금', '전일거래량', '매수호가', '매도호가']
        df_detail[cols_int] = df_detail[cols_int].astype(int)
        return df_detail
    
    def best3(self):
        right_now = datetime.today().strftime('%Y-%m-%d %X')
        best3 = Groupsa.get_detail(self).head(3)
        if best3.shape[0] < 3:
            print('해당 그룹 내 기업이 3개 미만 입니다!')
            print(f'{right_now} 현재 {self.group_nm} 그룹의 모든 기업정보입니다!')
            return best3
        else:
            print(f'{right_now} 현재 {self.group_nm} 그룹의 전일대비 등락률 best3기업입니다!')
            
            # 막대그래프
            plt.figure(figsize=(9, 6))
            x = best3['종목명']
            y = best3['현재가']
            plt.xlabel('종목명')
            plt.ylabel('현재가')

            plt.bar(x, y, color = 'red')
            for i, v in enumerate(x):
                plt.text(v, y[i], f'{i+1}위 : ' + best3['등락률'][i],
                         fontsize=12,
                         color="red",
                         horizontalalignment='center',
                         verticalalignment='bottom')

            plt.show()
            return best3
    
    def worst3(self):
        right_now = datetime.today().strftime('%Y-%m-%d %X')
        worst3= Groupsa.get_detail(self)
        r_idx = [i for i in range(worst3.shape[0]-1, -1, -1)]
        worst3 = pd.DataFrame(worst3, index=r_idx).reset_index(drop=True)
        worst3 = worst3.head(3)
        if worst3.shape[0] < 3:
            print('해당 그룹 내 기업이 3개 미만 입니다!')
            print(f'{right_now} 현재 {self.group_nm} 그룹의 모든 기업정보입니다!')
            
            return worst3
        else:
            print(f'{right_now} 현재 {self.group_nm} 그룹의 전일대비 등락률 worst3기업입니다!')
            
            # 막대그래프
            plt.figure(figsize=(9, 6))
            x = worst3['종목명']
            y = worst3['현재가']
            plt.xlabel('종목명')
            plt.ylabel('현재가')

            plt.bar(x, y, color = 'blue')
            for i, v in enumerate(x):
                plt.text(v, y[i], f'{i+1}위 : ' + worst3['등락률'][i],
                         fontsize=12,
                         color="blue",
                         horizontalalignment='center',
                         verticalalignment='bottom')

            plt.show()
            
            return worst3
