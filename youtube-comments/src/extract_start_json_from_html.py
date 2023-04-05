import math
import os
import time

import json
import re
from copy import deepcopy
import requests

GET_VIDEO_URL_DATA = {"context":
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
API_KEY = None
VIDEO_URLS = []


def extract_basic_json_from_html(html_text):
    global API_KEY
    csp_nonce = re.search('"cspNonce":"(\w*?)","canaryState"', html_text).group(1)
    patten = re.compile(
        f'<script nonce="{csp_nonce}">var ytInitialData = (.*?);</script><script nonce="{csp_nonce}">'
    )
    API_KEY = re.search('"INNERTUBE_API_KEY":"(.*?)"', html_text).group(1)
    result = patten.search(html_text)
    start_json = json.loads(result.group(1))
    # with open('basic-from-html.json', 'w+', encoding='U8') as f:
    #     json.dump(start_json, f, ensure_ascii=False, indent=4)
    video_infos_json, next_search_result = extract_from_json(start_json)
    new_token = get_new_token_from_init_search(next_search_result)
    get_next_video_url_json(new_token)
    extract_video_info(video_infos_json)


def extract_from_json(json_data):
    useful_contents = json_data['contents']['twoColumnSearchResultsRenderer']['primaryContents'][
        'sectionListRenderer'
    ]['contents']
    inner_video_infos_json = useful_contents[0]['itemSectionRenderer']['contents']
    if len(useful_contents) == 2:
        inner_next_search_result = useful_contents[1]
    else:
        inner_next_search_result = {}
    return inner_video_infos_json, inner_next_search_result


def extract_video_info(video_infos_json):
    for single_video_json in video_infos_json:
        videoRenderer = single_video_json.get('videoRenderer', None)
        if videoRenderer is None:
            continue
        video_link = 'https://www.youtube.com' + \
                     videoRenderer['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url']
        VIDEO_URLS.append(video_link)
    print('--' * 10)


def get_new_token_from_init_search(json_data: json):
    new_token = json_data['continuationItemRenderer']['continuationEndpoint']['continuationCommand']['token']
    return new_token


def get_next_video_url_json(new_token):
    global API_KEY
    data = deepcopy(GET_VIDEO_URL_DATA)
    next_search_result_url = f'https://www.youtube.com/youtubei/v1/search?key={API_KEY}&prettyPrint=false'
    data['continuation'] = new_token
    resp = requests.post(next_search_result_url, data=json.dumps(data))
    resp_json = resp.json()
    orre_ = resp_json['onResponseReceivedCommands']
    orre_length = len(orre_)
    if orre_length == 2:
        enter_info_key = 'reloadContinuationItemsCommand'
    else:
        enter_info_key = 'appendContinuationItemsAction'
    continuationItems = orre_[-1][enter_info_key]['continuationItems']
    video_info_contents = continuationItems[0]['itemSectionRenderer']['contents']
    # extract video information
    extract_video_info(video_info_contents)
    new_continuation = continuationItems[-1]
    if new_continuation.get('continuationItemRenderer', None):
        # start thread
        next_token = new_continuation['continuationItemRenderer']['continuationEndpoint']['continuationCommand'][
            'token']
        if next_token:
            get_next_video_url_json(new_token=next_token)


def main(search_url):
    start_time = time.time()
    with requests.get(search_url) as resp:
        # with open('search_result---.html', 'w+') as f:
        #     f.write(resp.text)
        html_content = resp.text
        extract_basic_json_from_html(html_content)
    print(f'Get video url spend {math.floor(time.time() - start_time)}')
    print(f'Length of video urls is {len(VIDEO_URLS)}')
    return VIDEO_URLS

    # with open(os.path.join(
    #         os.path.dirname(__file__), 'Data', 're_video_link.csv'
    # ), 'w+', encoding='utf-8') as f:
    #     f.writelines('\n'.join(VIDEO_URLS))


if __name__ == '__main__':
    search_url_ = 'https://www.youtube.com/results?search_query=shein+2022'
    main(search_url=search_url_)
