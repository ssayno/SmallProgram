import requests
from bs4 import BeautifulSoup

headers = {
    "Host": "search.dangdang.com",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Referer": "http://search.dangdang.com/?key=python&SearchFromTop=1&catalog=",
    "Accept-Language": "zh,zh-CN;q=0.9",
    "Proxy-Connection": "keep-alive"
}
cookies = {
    "ddscreen": "2",
    "__permanent_id": "20230429171130828225542237863733452",
    "__ddc_15d": "1682759491%7C!%7C_ddclickunion%3DP-129054",
    "__ddc_15d_f": "1682759491%7C!%7C_ddclickunion%3DP-129054",
    "__visit_id": "20230430210302289132255947777442641",
    "__out_refer": "1682859782%7C!%7Cwww.google.com%7C!%7C",
    "dest_area": "country_id%3D9000%26province_id%3D111%26city_id%3D0%26district_id%3D0%26town_id%3D0",
    "__rpm": "...1682859810817%7Cs_112100.155956512835%2C155956512836..1682860072930",
    "search_passback": "91da83bf7b229c4f29684e64fc0100002aa86400ad664e64",
    "__trace_id": "20230430210753806298993738680917559",
    "pos_9_end": "1682860074018",
    "pos_0_end": "1682860074075",
    "ad_ids": "31898396%2C14129493%2C5066933%7C%233%2C3%2C3",
    "pos_0_start": "1682860303914"
}
url = "http://search.dangdang.com/"
params = {
    "key": "python",
    "SearchFromTop": "1",
    "catalog": "",
    "page_index": "103"
}
response = requests.get(url, headers=headers, cookies=cookies, params=params)

with open('page-3.html', 'w+') as f:
    f.write(response.text)

soup = BeautifulSoup(response.text, 'lxml')
print(soup.select('#component_59 > li'))
