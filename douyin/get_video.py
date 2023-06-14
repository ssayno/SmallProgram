import requests
from copy import deepcopy

headers = {
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
url = "https://v26-web.douyinvod.com/1220bba1e41750ca1b594d83627f4c0c/64534071/video/tos/cn/tos-cn-ve-15c001-alinc2/oQsdkAIWWgnrgPAwQiiABTUjYNef9UDDvUw7bC/"
params = {
    "a": "6383",
    "ch": "0",
    "cr": "0",
    "dr": "0",
    "er": "0",
    "cd": "0|0|0|0",
    "cv": "1",
    "br": "771",
    "bt": "771",
    "cs": "2",
    "ds": "6",
    "ft": "GN7rKGVVyw3ZRK_8kmo~ySqTeaApH08S6vrKYrYcVmo0g3",
    "mime_type": "video_mp4",
    "qs": "11",
    "rc": "MzxnaWk4aTM7OWlnaDM2NEBpMzR5dGU6ZmZ3azMzNGkzM0A2NGNfNmBgXl8xXi8uXzU0YSNqX2RicjQwXzVgLS1kLWFzcw==",
    "l": "20230504121759C21B861F0DB8B5084211",
    "btag": "e00028000"
}


def extract_info_from_headers(response_header):
    print(response_header)
    query_length = int(response_header['Content-Length'])
    content_range = response_header.get("Content-Range")
    temp_, all_data_length = content_range.split('/')
    leave_data_length = int(temp_.split('-')[0].split(" ")[1]) + query_length
    if_range = response_header['ETag']
    return int(all_data_length), leave_data_length, if_range


def init_get_video(video_name):
    temp_header = deepcopy(headers)
    temp_header["Range"] = "bytes=0-100000"
    response = requests.get(url, headers=temp_header, params=params, proxies={
        "http": "http://localhost:7890"
    })
    response_header = response.headers
    with open(f"{video_name}.mp4", 'wb') as f:
        f.write(response.content)
    return extract_info_from_headers(response_header)


def get_following_video(video_name, start, end, if_range):
    temp_header = deepcopy(headers)
    temp_header["If-Range"] = if_range
    temp_header["Range"] = f"bytes={start}-{end}"
    response = requests.get(url, headers=temp_header, params=params, proxies={
        "http": "http://localhost:7890"
    })
    # print(response.headers)
    with open(f"{video_name}.mp4", 'ab') as f:
        f.write(response.content)
    return extract_info_from_headers(response.headers)


def main():
    video_name = "师傅"
    all_ql, leave_ql, if_range_value = init_get_video(video_name)
    next_ql_start = leave_ql
    next_ql_end = next_ql_start + 100000
    while 1:
        all_ql, leave_ql, if_range_value = get_following_video(video_name, next_ql_start, next_ql_end, if_range_value)
        print(all_ql, leave_ql, if_range_value)
        if all_ql == leave_ql:
            break
        next_ql_start = leave_ql
        next_ql_end = next_ql_start + 100000
        if next_ql_end > all_ql:
            next_ql_end = all_ql


if __name__ == '__main__':
    main()
