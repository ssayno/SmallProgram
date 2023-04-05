import atexit
import shutil
import aiohttp,asyncio
from aiohttp_socks import ChainProxyConnector
import json
import os
import csv
import sys
import time
import re
import threading
from itertools import islice
from copy import deepcopy
from extract_start_json_from_html import video_main
import resource


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


def try_catch_decorator(fn):
    global error_file

    async def inner(*args, **kwargs):
        try:
            if asyncio.iscoroutinefunction(fn):
                await fn(*args, **kwargs)
            else:
                fn(*args, **kwargs)
        except Exception as e:
            print("Decorator error", e)
            error_file.write(args[1])

    return inner


def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)


DIR_PATH = 'Result'
JSON_PATH = 'JSON'
HTML_PATH = 'HTML'

create_dir(DIR_PATH)
create_dir(JSON_PATH)
create_dir(HTML_PATH)


class GetCommentContent(threading.Thread):
    def __init__(self, continuationItems_list, postfix, api_key, dir_name):
        super().__init__()
        self.name = f'{dir_name.replace(" ", "-")}'
        self.continuationItems_list = continuationItems_list
        self.api_key = api_key
        self.target_dir = os.path.join(DIR_PATH, f"{dir_name.replace(' ', '-')}-{postfix}")
        if not os.path.exists(self.target_dir):
            self.start_or_not = True
            os.mkdir(self.target_dir)
        else:
            self.start_or_not = False
        self.result = []

    def run(self):
        if not self.start_or_not:
            return
        global semaphore
        semaphore.acquire()
        try:
            # print(f'Current thread id {threading.current_thread().name}')
            asyncio.run(self.asyncio_entrance())
        except Exception as e:
            print(e, '|')
        finally:
            # print(f'{threading.current_thread().name} finished!')
            semaphore.release()

    async def get_content_infinite_if_not(self, session, url, data, retry=False):
        try:
            async with session.post(url, data=json.dumps(data), proxy='http://127.0.0.1:7890') as resp:
                resp_text = await resp.text()
                resp_json = json.loads(resp_text)
            if retry:
                pass
            return resp_json
        except Exception:
            await asyncio.sleep(3)
            await self.get_content_infinite_if_not(session, url, data, retry=True)

    @try_catch_decorator
    async def asyncio_entrance(self):
        session_ = aiohttp.ClientSession()
        try:
            for index, single_itme in enumerate(self.continuationItems_list):
                tasks = []
                for continuationItem in single_itme:
                    single_result = {}
                    try:
                        author, content_text = await self.extract_normal_comment_text(continuationItem)
                        single_result[author] = {}
                        single_result[author]['replies'] = []
                        replies = continuationItem['commentThreadRenderer'].get('replies', None)
                        if replies:
                            new_token = replies['commentRepliesRenderer']['contents'][0]['continuationItemRenderer'][
                                'continuationEndpoint'
                            ]['continuationCommand']['token']
                            # add new task
                            tasks.append(
                                self.getReplies(session_, new_token, author, single_result)
                            )
                        single_result[author]['normal'] = content_text
                        self.result.append(single_result)
                    except Exception:
                        continue
                await asyncio.gather(*tasks)
                with open(
                        os.path.join(self.target_dir, f'{index+1}.json'), 'w+'
                ) as f:
                    json.dump(self.result, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print("error", e)
            shutil.rmtree(self.target_dir)
        finally:
            await session_.close()

    async def getReplies(self, session, new_token, father, single_result):
        data = deepcopy(DATA)
        next_comment_url = f'https://www.youtube.com/youtubei/v1/next?key={self.api_key}&prettyPrint=false'
        data['continuation'] = new_token
        resp_json = await self.get_content_infinite_if_not(session, url=next_comment_url, data=data)
        try:
            reply_continuationItems = resp_json['onResponseReceivedEndpoints'][0]['appendContinuationItemsAction'].get(
                'continuationItems', None
            )
        except:
            resp_json = await self.get_content_infinite_if_not(session, url=next_comment_url, data=data)
            reply_continuationItems = resp_json['onResponseReceivedEndpoints'][0]['appendContinuationItemsAction'].get(
                'continuationItems', None
            )
        if reply_continuationItems:
            last_continuationItem = reply_continuationItems[-1]
            if last_continuationItem.get('continuationItemRenderer', None):
                renew_token = last_continuationItem['continuationItemRenderer'][
                    'button'
                ]['buttonRenderer']['command']['continuationCommand']['token']
                await self.getReplies(session, renew_token, father, single_result)
                end = -1
            else:
                end = None
            for reply in reply_continuationItems[:end]:
                author, content_text = await self.extract_reply_text(reply)
                single_result[father]['replies'].append(
                    {
                        author: content_text
                    }
                )

    async def extract_normal_comment_text(self, single_continuationItem):
        comment = single_continuationItem['commentThreadRenderer']['comment']['commentRenderer']
        author = comment['authorText']['simpleText']
        content_text = comment['contentText']['runs']
        return author, content_text

    async def extract_reply_text(self, single_continuationItem):
        comment = single_continuationItem['commentRenderer']
        author = comment['authorText']['simpleText']
        content_text = comment['contentText']['runs']
        return author, content_text


async def requests_get_about_page(session, about_page_url):
    # print(f'Get {about_page_url} about page, now')
    async with session.get(about_page_url, proxy=f'http://127.0.0.1:7890') as resp:
        resp_text = await resp.text()
    # with open(os.path.join(HTML_PATH, 'about.html'), 'w+') as f:
    #     f.write(resp_text)
    about_ytInitialData, about_ytInitialPlayerResponse = await get_ytInitialData_and_ytInitialPlayerResponse(resp_text)
    # with open(os.path.join(JSON_PATH, 'about_page_ytInitialData.json'), 'w+') as f:
    #     json.dump(about_ytInitialData, f, indent=4, ensure_ascii=False)
    channelAboutFullMetadataRenderer_middle = about_ytInitialData['contents'][
        'twoColumnBrowseResultsRenderer'
    ]['tabs'][-2]['tabRenderer']
    if channelAboutFullMetadataRenderer_middle.get('content', None) is None:
        channelAboutFullMetadataRenderer = about_ytInitialData['contents'][
            'twoColumnBrowseResultsRenderer'
        ]['tabs'][-1]['tabRenderer']['content']['sectionListRenderer'][
            'contents'
        ][0]['itemSectionRenderer']['contents'][0]['channelAboutFullMetadataRenderer']
    else:
        channelAboutFullMetadataRenderer = channelAboutFullMetadataRenderer_middle['content']['sectionListRenderer'][
            'contents'
        ][0]['itemSectionRenderer']['contents'][0]['channelAboutFullMetadataRenderer']
    video_all_view_count = channelAboutFullMetadataRenderer['viewCountText']['simpleText'].split(' ')[0]
    join_date_text = '-'.join([
        item['text'] for item in channelAboutFullMetadataRenderer['joinedDateText']['runs']
    ])
    country_group = channelAboutFullMetadataRenderer.get('country', None)
    if country_group is None:
        country = 'UnKnow'
    else:
        country = country_group['simpleText']
    return video_all_view_count, join_date_text, country


async def get_ytInitialData_and_ytInitialPlayerResponse(html_text) -> []:
    csp_nonce = re.search('"cspNonce":"(.*?)","canaryState"', html_text).group(1)
    patten = re.compile(
        f'<script nonce="{csp_nonce}">var (?:ytInitialData|ytInitialPlayerResponse) = (.*?);</script>'
    )
    result = patten.findall(html_text)
    ytInitialData = json.loads(result[0])
    if len(result) == 2:
        ytInitialPlayerResponse = json.loads(result[1])
    else:
        ytInitialPlayerResponse = None
    return ytInitialData, ytInitialPlayerResponse


@try_catch_decorator
async def get_API_KEY_and_continuationCommand(session, video_url):
    postfix = video_url.strip('/').split('/')[-1]
    # print(f'Current url is {video_url}')
    async with session.get(video_url, proxy=f'http://127.0.0.1:7890') as resp:
        text = await resp.text()
    # with open(os.path.join(HTML_PATH, 'example.html'), 'w+', encoding='U8') as f:
    #     f.write(text)
    ytInitialData, ytInitialPlayerResponse = await get_ytInitialData_and_ytInitialPlayerResponse(text)
    #
    ytInitialPlayerResponse_content = ytInitialPlayerResponse['contents']['twoColumnWatchNextResults']['results'][
        'results'
    ]['contents']
    # with open(
    #     os.path.join(JSON_PATH, 'ytInitialData.json'),
    #         'w+', encoding='U8') as f:
    #     json.dump(ytInitialData, f, ensure_ascii=False, indent=4)
    # with open(
    #     os.path.join(JSON_PATH, 'ytInitialPlayerResponse.json'),
    #         'w+', encoding='U8') as f:
    #     json.dump(ytInitialPlayerResponse, f, ensure_ascii=False, indent=4)
    try:
        continuation = ytInitialPlayerResponse_content[-1]['itemSectionRenderer']['contents'][0][
            'continuationItemRenderer'
        ]['continuationEndpoint']['continuationCommand']
    except Exception:
        print("隐私视频")
        return
    token = continuation['token']
    # next_or_break = continuation['request']
    api_key = re.search('"INNERTUBE_API_KEY":"(.*?)",', text).group(1)
    # name
    up_name = re.sub(
        '[/\-]', '-', ytInitialData['microformat']['playerMicroformatRenderer']['ownerChannelName']
    )
    id_link = ytInitialData['microformat']['playerMicroformatRenderer']['ownerProfileUrl'] + '/about'
    publish_time = ytInitialData['microformat']['playerMicroformatRenderer']['publishDate']
    video_all_view_count, join_date_text, country = await requests_get_about_page(session, id_link)
    keywords = ytInitialData['videoDetails'].get('keywords', [])
    #
    main_info = json.loads(
        re.search('"videoDescriptionHeaderRenderer": (\{.*?\})}, \{"expandableVideoDescriptionBodyRenderer',
                  json.dumps(ytInitialPlayerResponse['engagementPanels'])).group(1)
    )
    title = main_info['title']
    factoid = main_info['factoid']
    likes = factoid[0]['factoidRenderer']['value']['simpleText']
    views = factoid[1]['factoidRenderer']['value']['simpleText']
    subscribe = ytInitialPlayerResponse_content[1]['videoSecondaryInfoRenderer']['owner']['videoOwnerRenderer'][
        'subscriberCountText'
    ]['accessibility']['accessibilityData']['label'].split(' ')[0]
    in_file_list = [
        up_name, join_date_text, country, subscribe, views, publish_time, likes, 0, keywords, video_all_view_count,
    ]
    await get_comment_json(session, token, api_key, postfix, up_name, in_file_list, write_=True)


async def get_comment_json(session, token, api_key, postfix, dir_name, in_file_list, continuationItems_list=[], write_=False):
    data = deepcopy(DATA)
    next_comment_url = f'https://www.youtube.com/youtubei/v1/next?key={api_key}&prettyPrint=false'
    data['continuation'] = token
    async with session.post(next_comment_url, data=json.dumps(data), proxy=f'http://127.0.0.1:7890') as resp:
        resp_json = await resp.json()
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
    continuationItems = orre[-1][enter_info_key].get('continuationItems', None)
    # 空评论
    if continuationItems is not None:
        new_continuation = continuationItems[-1]
        if new_continuation.get('continuationItemRenderer', None):
            # start thread
            new_token = new_continuation['continuationItemRenderer']['continuationEndpoint']['continuationCommand'][
                'token']
            # try:
            #     # print('start thread')
            #     start_thread = GetCommentContent(continuationItems[:-1], count, api_key, dir_name)
            #     start_thread.start()
            # except Exception as e:
            #     print(f'Thread {dir_name}-{count} show error like {e}')
            if new_token:
                new_continuationItems_list = [*continuationItems_list, continuationItems[:-1]]
                await get_comment_json(session, new_token, api_key, postfix, dir_name, in_file_list,
                                       continuationItems_list=new_continuationItems_list)
        else:
            try:
                # print('start thread')
                new_continuationItems_list = [*continuationItems_list, continuationItems]
                start_thread = GetCommentContent(new_continuationItems_list, postfix, api_key, dir_name)
                start_thread.start()
            except Exception as e:
                print(f'Thread {dir_name}-{postfix} show error like {e}')
    else:
        print(f'空评论')


async def read_video_link_csv(cf):
    session = aiohttp.ClientSession()
    tasks = []
    with open(cf, 'r', encoding='U8') as f:
        csv_reader_ = csv.reader(f)
        next(csv_reader_)
        for row in islice(csv_reader_, 0, 10):
            url = row[0]
            if not url.startswith('http'):
                continue
            tasks.append(get_API_KEY_and_continuationCommand(session, url))
    await asyncio.gather(*tasks)
    await session.close()


def test():
    video_url = 'https://www.youtube.com/watch?v=CLeZFW4sU_Q'  # 0 comment
    # video_url = 'https://www.youtube.com/watch?v=-gS9G3qKdL8'
    get_API_KEY_and_continuationCommand(video_url)


def get_spend_time(init_time):
    spend_time = time.time() - init_time
    print(f'Speed time {spend_time} seconds')


if __name__ == '__main__':
    # set the max open file count
    _, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    resource.setrlimit(resource.RLIMIT_NOFILE, (4096, hard))
    start_time = time.time()
    data_path = os.path.join(
        os.path.dirname(__file__), 'Data'
    )
    error_file = open('error_url.txt', 'w+', encoding='U8')
    if not os.path.exists(data_path):
        os.mkdir(data_path)
    video_csv_file = os.path.join(data_path, 'video_links.csv')
    if not os.path.exists(video_csv_file):
        search_url_ = 'https://www.youtube.com/results?search_query=anker+2022'
        # search_url_ = 'https://www.youtube.com/results?search_query=shein+2022'
        video_urls = video_main(search_url_)
        useful_urls = [item for item in video_urls if 'short' not in item]
        with open(video_csv_file, 'w+', encoding="utf-8") as f:
            f.writelines('\n'.join(useful_urls))
    print("获取视频链接结束")
    csv_file_path = os.path.join(data_path, 'result.csv')
    result_csv_file = open(csv_file_path, 'w+', encoding='utf-8')
    result_csv_write = csv.writer(result_csv_file)
    result_csv_write.writerow(
        ["id", "注册时间", "位置", "订阅数量", "观看数量", "上传时间", "点赞数", "评论数", "视频标签", "总观看量"]
    )
    # semaphore, Up to three simultaneous threads
    semaphore = threading.Semaphore(10)
    # 正常启动
    asyncio.run(read_video_link_csv(
        video_csv_file
    ))
    # 测试单个
    # test()
    # 关闭文件
    result_csv_file.close()
    error_file.close()
    atexit.register(get_spend_time, start_time=start_time)