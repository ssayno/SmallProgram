import requests
from .get_cookies import get_kuwo_cookies
from .get_headers import get_kuwo_headers


def get_single_music_requests(mid_number):
    cookies = get_kuwo_cookies()

    headers = get_kuwo_headers()

    params = {
        'mid': f'{mid_number}',
        'httpsStatus': '1',
        'reqId': '8599c620-0082-11ee-b3e8-d564c86a031c',
    }

    response = requests.get('http://www.kuwo.cn/api/www/music/musicInfo', params=params, cookies=cookies, headers=headers)
    response_json = response.json()