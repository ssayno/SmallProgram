import json
import os.path
import threading
import xlwt
import random
import time

import requests

BASE_URL = 'https://www.shenzhenfupin.com/api/product/selectviewproductpage?offset={offset}&limit={limit}&productName=&hotProduct=&isPromotion=&isNew=&isReleaseCMall=1&managementName=&platformClassIdStr=%5B%22{id}%22%5D&isSalesSort=1'
URL_CATEGORY = {}
CURRENT_IMAGE_DIR = os.path.join(
    os.path.abspath(''), 'Images'
)
SIMPLE_HEADER = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E217 MicroMessenger/6.8.0(0x16080000) NetType/WIFI Language/en Branch/Br_trunk MiniProgramEnv/Mac',
}


class ThreadDownloadImage(threading.Thread):
    def __init__(self, urls, ids, _path):
        super().__init__()
        self.urls = urls
        self.ids = ids
        self._path = _path

    def run(self) -> None:
        for image_url, image_path in zip(self.urls, self.ids):
            self.crawl_single_image(image_url, image_path)

    def crawl_single_image(self, url, id_):
        image_path = os.path.join(self._path, f'{id_}.jpg')
        with requests.get(url, headers=SIMPLE_HEADER) as response:
            content = response.content
            with open(image_path, 'wb') as f:
                f.write(content)


def request_usage(url):
    __headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E217 MicroMessenger/6.8.0(0x16080000) NetType/WIFI Language/en Branch/Br_trunk MiniProgramEnv/Mac',
        'Cookie': 'jcloud_alb_route=000a8be438b560575f4102cf63925eee',
        'Content-Type': 'application/x-www-form-urlencoded',
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://servicewechat.com/wxc22ddcffd7cf0d4c/65/page-frame.html",
        "Accept-Language": "zh-CN,zh-Hans;q=0.9",
        "X-Requested-With": "XMLHttpRequest"
    }
    resp = requests.get(url, headers=__headers)
    resp_json = resp.json()
    success = resp_json['success']
    if success:
        total = resp_json['total']
    else:
        total = 0
    return resp_json, success, total


def get_single_product(id_, pid, offset=0, limit=10):
    global excel_row
    result = {
        "pid": pid,
        'rows': []
    }
    url = BASE_URL.format(
        offset=offset, limit=limit, id=id_
    )
    print(f'Current first url is {url}')
    resp_json, success, total = request_usage(url)
    if total != 0:
        limit = (total // 10 + 1) * 10
        url = BASE_URL.format(
            offset=offset, limit=limit, id=id_
        )
        print(f'Current changed limit url is {url}')
    resp_json, success, total = request_usage(url)

    print("状态为", success)
    result['rows'] = resp_json['rows']
    target_dir = os.path.join(CURRENT_IMAGE_DIR, f'{pid}', f'{id_}')
    if not os.path.exists(target_dir):
        try:
            os.makedirs(target_dir, exist_ok=False)
        except Exception as e:
            print(e)
            print(f'{target_dir} is exists')
    image_urls = []
    product_ids = []
    for row in resp_json['rows']:
        product_name = row['productName']
        product_image = row['mainImg']
        image_urls.append(product_image)
        #
        product_price = row['productPrice']
        product_advice_price = row['adviceRetailPrice']
        #
        product_id = row['productId']
        product_ids.append(product_id)
        #
        image_path = os.path.join(target_dir, f'{product_id}.jpg')
        data_sheet.write(excel_row, 0, image_path)
        data_sheet.write(excel_row, 1, product_name)
        data_sheet.write(excel_row, 2, product_price)
        data_sheet.write(excel_row, 3, product_advice_price)
        excel_row += 1
    thread = ThreadDownloadImage(image_urls, product_ids, target_dir)
    thread.start()
    print(f'产品数量为 {len(result["rows"])}')
    # with open(target_file, 'w+', encoding='u8') as f:
    #     json.dump(result, f, ensure_ascii=False, indent=4)


def get_all_categories():
    _headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E217 MicroMessenger/6.8.0(0x16080000) NetType/WIFI Language/en Branch/Br_trunk MiniProgramEnv/Mac',
        'Cookie': 'jcloud_alb_route=135521239454c605aff7304a50f23d87',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    url = 'https://www.shenzhenfupin.com/api/productclass/indexproductclass'
    resp = requests.get(url, headers=_headers)
    return resp.json()


def extract_url_from_json():
    data = get_all_categories()
    categories = data['ext']
    for category in categories:
        pid = category['id']
        URL_CATEGORY[pid] = []
        children_of_category = category['children']
        if not children_of_category:
            print("ok")
        for children in children_of_category:
            URL_CATEGORY[pid].append(children["id"])
    with open('url.json', 'w+', encoding='utf-8') as f:
        json.dump(URL_CATEGORY, f, ensure_ascii=False, indent=4)

def crawl():
    for pid, value in URL_CATEGORY.items():
        for _id in value:
            get_single_product(_id, pid)
            time.sleep(random.uniform(0.2, 0.5))
        time.sleep(10)


if __name__ == '__main__':
    extract_url_from_json()
    excel_book = xlwt.Workbook(encoding='utf-8')
    data_sheet = excel_book.add_sheet('数据 1')
    excel_row = 0
    data_sheet.write(excel_row, 0, '产品图片路径')
    data_sheet.write(excel_row, 1, '产品名称')
    data_sheet.write(excel_row, 2, '产品原价')
    data_sheet.write(excel_row, 3, '产品零售价')
    excel_row += 1
    crawl()
    excel_book.save('圳帮扶.xls')
