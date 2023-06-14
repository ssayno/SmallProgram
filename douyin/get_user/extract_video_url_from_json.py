import asyncio
import json
import os
import time
from copy import deepcopy
import requests
import threading
import aiohttp

Result_path = 'Result'
if not os.path.exists(Result_path):
    os.mkdir(Result_path)

HEADERS = {
    "Host": "v26-web.douyinvod.com",
    "sec-ch-ua": "\"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "sec-ch-ua-platform": "\"macOS\"",
    "Accept": "*/*",
    "Origin": "https://www.douyin.com",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "video",
    "Referer": "https://www.douyin.com/",
    "Accept-Language": "zh,zh-CN;q=0.9",
}


class DownLoadThread(threading.Thread):
    def __init__(self, video_url, video_name):
        super().__init__()
        self.video_url = video_url
        self.video_name = video_name.replace('\n', "").replace(' ', '-')
        self.chunk_size = 100000
        self.queue = {}

    def run(self) -> None:
        full_length, leave_ql, if_range_value = self.init_get_video()
        ranger_headers = self.split_with_chunk_size(full_length,
                                                    leave_ql, if_range_value)
        asyncio.run(self.async_crawl_video_fragment(ranger_headers))
        print(f'Finished crawl video {self.video_name} fragment')
        sort_data = sorted(self.queue.items(), key=lambda x: x[0])
        with open(os.path.join(Result_path, f"{self.video_name}.mp4"), 'ab') as f:
            for _, ssd in sort_data:
                f.write(ssd)

    async def async_crawl_video_fragment(self, range_headers):
        task = []
        session = aiohttp.ClientSession()

        for index_, range_header in enumerate(range_headers):
            task.append(
                self.get_video_fragment(session, index_, range_header)
            )
            # if index_ == 100:
            #     break
        await asyncio.gather(*task)
        await session.close()

    async def get_video_fragment(self, session, task_number, header_dict):
        temp_header = deepcopy(HEADERS)
        for key, value in header_dict.items():
            temp_header[key] = value
        async with session.get(self.video_url, headers=temp_header, proxy=f'http://127.0.0.1:7890') as resp:
            await asyncio.sleep(0.5)
            self.queue[task_number] = await resp.read()
        # print(f"Task {task_number} finished")

    def split_with_chunk_size(self, full_length, start_range, irv):
        header_ranges = []

        while start_range < full_length:
            end_range = start_range + self.chunk_size
            if end_range > full_length:
                end_range = full_length
            header_ranges.append({
                "Range": f'bytes={start_range}-{end_range}',
                "If-Range": irv
            })
            start_range = end_range + 1
        return header_ranges

    def init_get_video(self):
        temp_header = deepcopy(HEADERS)
        temp_header["Range"] = "bytes=0-100000"
        response = requests.get(self.video_url, headers=temp_header, proxies={
            "http": "http://localhost:7890"
        })
        response_header = response.headers
        with open(os.path.join(Result_path, f"{self.video_name}.mp4"), 'wb') as f:
            f.write(response.content)
        return self.extract_info_from_headers(response_header)

    @staticmethod
    def extract_info_from_headers(response_header):
        query_length = int(response_header['Content-Length'])
        content_range = response_header.get("Content-Range")
        temp_, all_data_length = content_range.split('/')
        leave_data_length = int(temp_.split('-')[0].split(" ")[1]) + query_length
        if_range = response_header['ETag']
        return int(all_data_length), leave_data_length, if_range


def extract_from_json(json_data_):
    result_urls = []
    aweme_list = json_data_['aweme_list']
    for item in aweme_list:
        url_list = item['video']['play_addr']['url_list']
        url_title = item['preview_title']
        for url_ in url_list:
            if 'v26' in url_:
                result_urls.append({
                    "title": url_title,
                    "url": url_
                })
                break
    return result_urls


# def download_single_video(video_url, video_name):
#     all_ql, leave_ql, if_range_value = init_get_video(video_url, video_name)
#     next_ql_start = leave_ql
#     next_ql_end = next_ql_start + 100000
#     while 1:
#         all_ql, leave_ql, if_range_value = get_following_video(video_url, video_name, next_ql_start,
#                                                                next_ql_end, if_range_value)
#         print(all_ql, leave_ql, if_range_value)
#         if all_ql == leave_ql:
#             break
#         next_ql_start = leave_ql
#         next_ql_end = next_ql_start + 100000
#         if next_ql_end > all_ql:
#             next_ql_end = all_ql


if __name__ == '__main__':
    with open('zst.json', 'rb') as f:
        json_data = json.load(f)
    result_urls = extract_from_json(json_data)
    # download_single_video(result_urls[0], "ok")
    for i in result_urls:
        print(i.get('url'))
        dt = DownLoadThread(i.get('url'), i.get('title'))
        dt.start()
        dt.join()
        time.sleep(10)
