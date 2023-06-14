import requests
from .get_cookies import get_kuwo_cookies
from .get_headers import get_kuwo_headers


def get_search_result_with_keyword(keyword):
    cookies = get_kuwo_cookies()

    headers = get_kuwo_headers()

    params = {
        'key': keyword,
        'pn': '1',
        'rn': '20',
        'httpsStatus': '1',
        'reqId': '63cf9100-0082-11ee-9a75-f9ae533cdc6b',
    }

    response = requests.get('http://www.kuwo.cn/api/www/search/searchMusicBykeyWord', params=params, cookies=cookies,
                            headers=headers)

    response_json = response.json()

    data = response_json['data']
    data_total = data['total']
    data_list = data['list']
    current_data_list_length = len(data_list)
    print(f'Total length is {data_total}, current data list length is {current_data_list_length}')
    return data_list
