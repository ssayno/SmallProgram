import math

import json
import os
import csv
import sys
import time
import requests
import re
import threading
from itertools import islice
from copy import deepcopy

DATA = {"context":
            {"client":
                 {"hl": "zh-CN", "gl": "US", "remoteHost": "209.141.62.254", "deviceMake": "Apple",
                  "deviceModel": "",
                  "visitorData": "CgtlcFVXQnhmX1U2MCjYu-ugBg%3D%3D",
                  "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 ("
                               "KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36,gzip(gfe)",
                  "clientName": "WEB", "clientVersion": "2.20230320.07.00", "osName": "Macintosh",
                  "osVersion": "10_15_7",
                  "originalUrl": "https://www.youtube.com/", "platform": "DESKTOP",
                  "clientFormFactor": "UNKNOWN_FORM_FACTOR", "configInfo": {
                     "appInstallData": "CNi766AGEKLsrgUQtpz-EhC_kK8FEMz1rgUQ4pOvBRCpsv4SEOf3rgUQ7YavBRDi1K4FEKKx_hIQzK7-EhD"
                                       "-7q4FELiLrgUQgLP-EhDM364FENuVrwUQ5LP-EhCU"
                                       "-K4FENOs_hIQjfeuBRDloP4SEInorgUQuNSuBRCa2q4FEMyRrwU%3D"},
                  "userInterfaceTheme": "USER_INTERFACE_THEME_DARK", "timeZone": "Asia/Shanghai",
                  "browserName": "Chrome",
                  "browserVersion": "111.0.0.0",
                  "acceptHeader": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,"
                                  "image/webp,image/apng,*/*;q=0.8,"
                                  "application/signed-exchange;v=b3;q=0.7",
                  "deviceExperimentId": "ChxOekU0T1RFNU1ERXpORGswTVRBeE5Ua3hNZz09ENi766AGGNbElJ4G",
                  "screenWidthPoints": 1280, "screenHeightPoints": 1464, "screenPixelDensity": 1,
                  "screenDensityFloat": 1,
                  "utcOffsetMinutes": 480, "connectionType": "CONN_CELLULAR_3G",
                  "memoryTotalKbytes": "8000000",
                  "mainAppWebInfo": {
                      "graftUrl": "https://www.youtube.com/watch?v=gOcQP_Gi9r8&list=RDgOcQP_Gi9r8"
                                  "&start_radio=1",
                      "pwaInstallabilityStatus": "PWA_INSTALLABILITY_STATUS_CAN_BE_INSTALLED",
                      "webDisplayMode": "WEB_DISPLAY_MODE_BROWSER",
                      "isWebNativeShareAvailable": 'false'}
                  }
             }
        }
DIR_PATH = 'Result'
if not os.path.exists(DIR_PATH):
    os.mkdir(DIR_PATH)


class GetCommentContent(threading.Thread):
    def __init__(self, continuationItems, count, api_key, dir_name):
        super().__init__()
        self.setName(f'{dir_name}-{count}')
        self.continuationItems = continuationItems
        self.count = count
        self.api_key = api_key
        self.target_dir = os.path.join(DIR_PATH, dir_name.replace(' ', '-'))
        if not os.path.exists(self.target_dir):
            os.mkdir(self.target_dir)

    def run(self):
        global semaphore
        semaphore.acquire()
        result = []
        for continuationItem in self.continuationItems:
            single_result = {}
            try:
                author, content_text = self.extract_normal_comment_text(continuationItem)
                single_result[author] = {}
                single_result[author]['replies'] = []
                replies = continuationItem['commentThreadRenderer'].get('replies', None)
                if replies:
                    new_token = replies['commentRepliesRenderer']['contents'][0]['continuationItemRenderer'][
                        'continuationEndpoint'
                    ]['continuationCommand']['token']
                    self.getReplies(new_token, author, single_result)
                single_result[author]['normal'] = content_text
                result.append(single_result)
            except Exception:
                break
        with open(
                os.path.join(self.target_dir, f'{self.count}.json'), 'w+'
        ) as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        semaphore.release()

    def getReplies(self, new_token, father, single_result):
        data = deepcopy(DATA)
        next_comment_url = f'https://www.youtube.com/youtubei/v1/next?key={self.api_key}&prettyPrint=false'
        data['continuation'] = new_token
        resp = requests.post(next_comment_url, data=json.dumps(data))
        resp_json = resp.json()
        reply_continuationItems = resp_json['onResponseReceivedEndpoints'][0]['appendContinuationItemsAction'].get(
            'continuationItems', None
        )
        if reply_continuationItems:
            last_continuationItem = reply_continuationItems[-1]
            if last_continuationItem.get('continuationItemRenderer', None):
                renew_token = last_continuationItem['continuationItemRenderer'][
                    'button'
                ]['buttonRenderer']['command']['continuationCommand']['token']
                self.getReplies(renew_token, father, single_result)
                end = -1
            else:
                end = None
            for reply in reply_continuationItems[:end]:
                author, content_text = self.extract_reply_text(reply)
                single_result[father]['replies'].append(
                    {
                        author: content_text
                    }
                )

    def extract_normal_comment_text(self, single_continuationItem):
        comment = single_continuationItem['commentThreadRenderer']['comment']['commentRenderer']
        author = comment['authorText']['simpleText']
        content_text = comment['contentText']['runs']
        return author, content_text

    def extract_reply_text(self, single_continuationItem):
        comment = single_continuationItem['commentRenderer']
        author = comment['authorText']['simpleText']
        content_text = comment['contentText']['runs']
        return author, content_text


def requests_get_about_page(about_page_url):
    resp = requests.get(about_page_url)
    text = resp.text
    video_all_view_count = re.search('"viewCountText":\{"simpleText":"(.*?) views"\},', text).group(1)
    join_date_text = re.search('"joinedDateText":\{"runs":\[\{"text":"Joined "\},\{"text":"(.*?)"\}\]\}', text).group(1)
    country_group = re.search('"country":\{"simpleText":"(.*?)"\}', text)
    if country_group:
        country = country_group.group(1)
    else:
        country = ""
    return video_all_view_count, join_date_text, country


def get_API_KEY_and_continuationCommand(video_url):
    next_count = 1
    resp = requests.get(video_url)
    text = resp.text
    # with open('example.html', 'w+', encoding='U8') as f:
    #     f.write(text)
    try:
        continuation = json.loads(
            re.search('"continuationCommand":(\{.*?\})', text).group(1)
        )
    except Exception:
        print("隐私视频")
        return
    token = continuation['token']
    # next_or_break = continuation['request']
    api_key = re.search('"INNERTUBE_API_KEY":"(.*?)",', text).group(1)
    name_and_id_groups = re.search('"item": \{"@id": "(.*?)", "name": "(.*?)"\}', text)
    id_link = name_and_id_groups.group(1).replace('\\', "") + "/about"
    video_all_view_count, join_date_text, country = requests_get_about_page(id_link)
    up_name = name_and_id_groups.group(2)
    try:
        keywords = re.search('"keywords":(\[.*?\])', text).group(1)
    except Exception:
        keywords = []
    publish_time = re.search('"publishDate":"(.*?)"', text).group(1)
    likes = re.search(
        '\{"factoidRenderer":\{"value":\{"simpleText":"(.*?)"\},"label":\{"simpleText":"Likes"\},"accessibilityText":"(.*?) likes"\}\}',
        text).group(2)
    views = re.search(
        '\{"factoidRenderer":\{"value":\{"simpleText":"(.*?)"\},"label":\{"simpleText":"Views"\},"accessibilityText":"(.*?) views"\}\}',
        text).group(2)
    subscribe = re.search(
        '"subscriberCountText":\{"accessibility":\{"accessibilityData":\{"label":"(.*?) subscribers"\}\},"simpleText":"(.*?) subscribers"\},',
        text).group(2)
    in_file_list = [
        up_name, join_date_text, country, subscribe, views, publish_time, likes, 0, keywords, video_all_view_count,
    ]
    # print
    # print(likes, subscribe, views)
    # print(publish_time)
    # print(keywords)
    # print(f'API KEY is {api_key}\nToken is {continuation}\nUP Name {up_name}\nId link is {id_link}')
    get_comment_json(token, api_key, next_count, up_name, in_file_list, write_=True)


def get_comment_json(token, api_key, count, dir_name, in_file_list, write_=False):
    data = deepcopy(DATA)
    next_comment_url = f'https://www.youtube.com/youtubei/v1/next?key={api_key}&prettyPrint=false'
    data['continuation'] = token
    resp = requests.post(next_comment_url, data=json.dumps(data))
    resp_json = resp.json()
    # with open(f'{count}.json', 'w+') as f:
    #     json.dump(resp_json, f, ensure_ascii=False, indent=4)
    orre = resp_json['onResponseReceivedEndpoints']
    orre_length = len(orre)
    if orre_length == 2:
        comment_count = orre[0]['reloadContinuationItemsCommand']['continuationItems'][0][
            'commentsHeaderRenderer'
        ]['countText']['runs'][0]['text']
        if write_:
            in_file_list[7] = comment_count
            result_csv_write.writerow(in_file_list)
        enter_info_key = 'reloadContinuationItemsCommand'
    else:
        enter_info_key = 'appendContinuationItemsAction'
    continuationItems = orre[-1][enter_info_key]['continuationItems']
    new_continuation = continuationItems[-1]
    if new_continuation.get('continuationItemRenderer', None):
        # start thread
        new_token = new_continuation['continuationItemRenderer']['continuationEndpoint']['continuationCommand']['token']
        try:
            start_thread = GetCommentContent(continuationItems[:-1], count, api_key, dir_name)
            start_thread.start()
        except Exception:
            print(f'Thread {dir_name}-{count} show error')
        if new_token:
            count += 1
            get_comment_json(new_token, api_key, count, dir_name, in_file_list)
    else:
        try:
            start_thread = GetCommentContent(continuationItems, count, api_key, dir_name)
            start_thread.start()
        except Exception:
            print(f'Thread {dir_name}-{count} show error')


def read_video_link_csv(cf):
    error_file = open('../error_url.txt', 'w+', encoding='U8')
    with open(cf, 'r', encoding='utf-8') as f:
        csv_reader = csv.reader(f)
        next(csv_reader)
        for row in islice(csv_reader, 0, 15):
            url = row[0]
            if not url.startswith('http'):
                continue
            try:
                print(f'Current url is {url}')
                start_time = time.time()
                get_API_KEY_and_continuationCommand(url)
                print(f'花费时间为 {math.floor(time.time() - start_time)} 秒')
            except Exception as e:
                error_file.write(f'{url}\n')
                print(f'Current url is {url}, show error like {e}')
            # print('sleep 30 seconds')
            # time.sleep(30)
    error_file.close()


def test():
    video_url = 'https://www.youtube.com/watch?v=bTz1Pltk3W8'
    get_API_KEY_and_continuationCommand(video_url)


if __name__ == '__main__':
    data_path = os.path.join(
        os.path.dirname(__file__), os.path.pardir, 'Data'
    )
    if not os.path.exists(data_path):
        print("请将链接数据文件(video_links.csv)放入到 Data 文件夹")
        sys.exit()
    result_csv_file = open('result.csv', 'w+', encoding='utf-8')
    result_csv_write = csv.writer(result_csv_file)
    result_csv_write.writerow(
        ["id", "注册时间", "位置", "订阅数量", "观看数量", "上传时间", "点赞数", "评论数", "视频标签", "总观看量"]
    )
    csv_file = os.path.join(data_path, 'video_links.csv')
    # semaphore, Up to three simultaneous threads
    semaphore = threading.Semaphore(10)
    # 正常启动
    read_video_link_csv(csv_file)
    # 测试单个
    # test()
    # 关闭文件
    result_csv_file.close()
