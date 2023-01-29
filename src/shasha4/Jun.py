import time
import platform
import pandas as pd
from matplotlib import rc
from requests import request
from multiprocessing import Pool
from bs4 import BeautifulSoup as bs
from matplotlib import pyplot as plt


try:
    from IPython.display import clear_output
except:
    pass


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}


def get_item(code):
    item_auto_cols = {
        'cd': '종목 코드',
        'nm': '종목 명',
        'mt': '마켓 타입',
        'ms': '마켓 상태',
        'tyn': '거래 가능 여부',
        'aa': '거래 대금',
        'aq': '거래 량',
        'nv': '현재 가격',
        'cr': '등락률',
        'cv': '등락가',
        'hv': '최고가',
        'lv': '최저가',
        'ul': '상한가',
        'll': '하한가',
        'pcv': '전일 종가',
        'sv': '전일가',
        'ov': '시가',
        'bps': 'BPS',
        'eps': 'EPS'
    }
    _uri = ('get', f'https://polling.finance.naver.com/api/realtime?query=SERVICE_ITEM:{code}')
    _headers = {'User-Agent': 'Mozilla/5.0 (Macintosh;'}
    resp = request(*_uri, headers=_headers)
    datas = resp.json()['result']['areas'][0]['datas'][0]
    datas = {v: datas[k] for k, v in item_auto_cols.items()}
    return pd.DataFrame(datas.values(), index=datas.keys()).T


class ControlTower:
    def __init__(self):
        self.__upjong_uri = ('get', 'https://finance.naver.com/sise/sise_group.naver?type=upjong')
        self.__items_uri = 'https://finance.naver.com/sise/sise_group_detail.naver?type=upjong&no={}'
        self.__upjong = self.get_upjong()
        self.__upjong_items = dict()
        self.__plot_items = dict()

    @property
    def upjong(self):
        return self.__upjong

    @property
    def upjong_items(self):
        return self.__upjong_items

    @property
    def plot_items(self):
        return self.__plot_items

    def get_upjong(self):
        resp = request(*self.__upjong_uri, headers=HEADERS)
        df = pd.read_html(resp.text)[0]
        df.columns = [col[1] for col in list(df.columns)]
        df = df.dropna(axis=0, how='all')
        df = df.reset_index(drop=True)
        df = df.astype({'전체': int, '상승': int, '보합': int, '하락': int})
        html = bs(resp.text, 'html.parser')
        df['업종 코드'] = [tag_a['href'].split('=')[-1] for tag_a in html.find('table', {'class': 'type_1'}).find_all('a')]
        return df

    def get_upjong_items(self, upjong_code):
        if upjong_code not in self.__upjong_items:
            resp = request('get', self.__items_uri.format(upjong_code), headers=HEADERS)
            self.__upjong_items[upjong_code] = {tag_a.text: tag_a['href'].split('=')[-1] for tag_a in bs(resp.text, 'html.parser').select('div.name_area > a')}
        return self.__upjong_items[upjong_code]

    def get_items_auto(self, upjong_code):
        print('데이터를 불러오는 중 입니다...')
        for i in range(10):
            pool = Pool(processes=len(self.__upjong_items[upjong_code]))
            item_auto_datas = pool.map(get_item, list(self.__upjong_items[upjong_code].values()))
            for auto_data in item_auto_datas:
                now_code = auto_data['종목 코드'][0]
                if now_code not in self.__plot_items:
                    self.__plot_items[now_code] = {
                        'price': [auto_data['현재 가격'][0]],
                        'volume': [0],
                        'name': auto_data['종목 명'][0],
                        'prev_volume': auto_data['거래 량'][0]
                    }
                else:
                    plot_item = self.__plot_items[now_code]
                    plot_item['price'].append(auto_data['현재 가격'][0])
                    plot_item['volume'].append(auto_data['거래 량'][0] - plot_item['prev_volume'])
                    plot_item['prev_volume'] = auto_data['거래 량'][0]
            clear_output()
            try:
                display(pd.concat(item_auto_datas, ignore_index=True))
            except:
                print('N')
            time.sleep(2)

    def show_plot(self, item_code):
        if item_code not in self.__plot_items:
            print('수집하지 않은 코드입니다.')
        else:
            if platform.system() == 'Darwin':
                rc('font', family='AppleGothic')
            else:
                plt.rcParams['font.family'] = 'Malgun Gothic'
            item = self.__plot_items[item_code]
            price_chart = plt.subplot(2, 1, 1)
            price_chart.title.set_text(item['name'])
            plt.plot(item['price'], 'o-')
            plt.ylabel('Price')
            plt.xticks(range(0, len(item['price'])))
            plt.xticks(visible=False)
            plt.subplot(2, 1, 2, sharex=price_chart)
            plt.bar(range(0, len(item['price'])), item['volume'])
            plt.xlabel('Per 8 Sec')
            plt.ylabel('Volume')
            plt.show()
