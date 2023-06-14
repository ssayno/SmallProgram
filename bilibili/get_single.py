import requests
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
import pprint

VIDEO_CONTENTS = {}

ORIGIN_HEADERS = {
    'Host': 'cn-lnsy-cm-01-03.bilivideo.com',
    'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'sec-ch-ua-platform': '"macOS"',
    'accept': '*/*',
    'origin': 'https://www.bilibili.com',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.bilibili.com/',
    'accept-language': 'zh-CN,zh;q=0.9',
    'if-range': 'Thu, 30 Mar 2023 20:40:59 GMT',
}


def get_content_length(url):
    own_header = deepcopy(ORIGIN_HEADERS)
    own_header['range'] = 'bytes=0-10'
    response = requests.get(
        url,
        headers=own_header
    )
    resp_headers = response.headers
    content_length = int(
        resp_headers['Content-Range'].split('/')[1]
    )
    print(content_length)
    return content_length


def split_by_chunk_size(all_length, chunk_size):
    result = []
    start = 0
    end = start + chunk_size
    while end < all_length:
        result.append(
            f'bytes={start}-{end}'
        )
        start += chunk_size + 1
        end = start + chunk_size
    else:
        result.append(f'bytes={start}-{all_length - 1}')
    return result


def get_split_video_url(video_url):
    content_length = get_content_length(video_url)
    chunk_size = 100000
    fragments = split_by_chunk_size(content_length, chunk_size=chunk_size)
    return fragments


def get_outer(url_need, headers_):
    response = requests.get(
        url_need,
        headers=headers_
    )
    return response.status_code, response.content


def get_single_fragment(dict_argument, limit=5):
    base_url = dict_argument['base_url']
    range_ = dict_argument['range_']
    count = dict_argument['count']
    if limit == 0:
        print(f'{count} 在 {limit} 次之后仍然失败')
        return
    try:
        own_header = deepcopy(ORIGIN_HEADERS)
        own_header['range'] = range_
        status_code, resp_content = get_outer(base_url, own_header)
        if status_code not in (206, 200):
            if limit == 5:
                print(f'{count} 初次失误, {status_code}')
            get_single_fragment(dict_argument, limit=limit - 1)
        else:
            if limit != 5:
                print(f'{count} {5 - limit} 次后成功')
            VIDEO_CONTENTS[count] = resp_content
        if count == 482:
            print('aa')
    except Exception as e:
        print(f'{count} 初次失误\n{e}')
        get_single_fragment(dict_argument, limit=limit - 1)


def main(url_):
    video_url = url_
    fragments = get_split_video_url(video_url)
    print(len(fragments), 'All length')
    arguments_for_threadPool = [
        {
            'base_url': url_,
            'range_': item,
            'count': index+1
        }
        for index, item in enumerate(fragments)
    ]
    # pprint.pprint(arguments_for_threadPool)
    with ThreadPoolExecutor(max_workers=40) as executor:
        executor.map(get_single_fragment, arguments_for_threadPool)
    print('get_content_finished')
    video_length = len(VIDEO_CONTENTS)
    with open('audio.mp4', 'wb') as f:
        for i in range(video_length):
            f.write(
                VIDEO_CONTENTS[i + 1]
            )

main('https://cn-lnsy-cm-01-06.bilivideo.com/upgcxcode/99/88/196018899/196018899_nb2-1-30232.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1680249089&gen=playurlv2&os=bcache&oi=3549362003&trid=0000cf1fd92cd682449f99a012f3233cf0cdu&mid=438162145&platform=pc&upsig=dd4c64cc632d3b03ce42124c4815e5e3&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform&cdnid=3247&bvc=vod&nettype=0&orderid=0,3&buvid=&build=0&agrr=1&bw=16602&logo=80000000')
# main('https://cn-lnsy-cm-01-06.bilivideo.com/upgcxcode/99/88/196018899/196018899_nb2-1-30080.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1680249089&gen=playurlv2&os=bcache&oi=3549362003&trid=0000cf1fd92cd682449f99a012f3233cf0cdu&mid=438162145&platform=pc&upsig=974cf92475c1ce7fffe1e89a04161ff1&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform&cdnid=3247&bvc=vod&nettype=0&orderid=0,3&buvid=&build=0&agrr=1&bw=294641&logo=80000000')
# main('https://cn-jxnc-cm-01-03.bilivideo.com/upgcxcode/71/30/1073313071/1073313071-1-30077.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1680247078&gen=playurlv2&os=bcache&oi=3549362003&trid=00005aa1f1f0686d4652ac29c2f31e6db3ffu&mid=438162145&platform=pc&upsig=32f40af23d50d4b6acfd2fb83d9a605d&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform&cdnid=4202&bvc=vod&nettype=0&orderid=0,3&buvid=E99B81BB-6571-0F50-92BD-53B7D40E6B7032816infoc&build=0&agrr=1&bw=51303&logo=80000000')
# main('https://cn-lnsy-cm-01-06.bilivideo.com/upgcxcode/26/61/1075766126/1075766126-1-100026.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1680246464&gen=playurlv2&os=bcache&oi=3549362003&trid=0000d19a826796164ce8bf01699205d750c9u&mid=0&platform=pc&upsig=def46693511cf8f94c7150a5602e6ae0&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform&cdnid=3247&bvc=vod&nettype=0&orderid=0,3&buvid=&build=0&agrr=1&bw=171700&logo=80000000')
# main('https://cn-lnsy-cm-01-06.bilivideo.com/upgcxcode/26/61/1075766126/1075766126-1-100022.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1680246347&gen=playurlv2&os=bcache&oi=3549362003&trid=0000f342f278a4af40e8b66e2a9d2e7e0408u&mid=0&platform=pc&upsig=4c3cfaf774685be32a5e36e9b1bfb21b&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform&cdnid=3247&bvc=vod&nettype=0&orderid=0,3&buvid=&build=0&agrr=1&bw=20295&logo=80000000')
# main('https://cn-lnsy-cm-01-06.bilivideo.com/upgcxcode/26/61/1075766126/1075766126-1-100026.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1680246464&gen=playurlv2&os=bcache&oi=3549362003&trid=0000d19a826796164ce8bf01699205d750c9u&mid=438162145&platform=pc&upsig=def46693511cf8f94c7150a5602e6ae0&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform&cdnid=3247&bvc=vod&nettype=0&orderid=0,3&buvid=&build=0&agrr=1&bw=171700&logo=80000000')
# main('https://cn-lnsy-cm-01-06.bilivideo.com/upgcxcode/26/61/1075766126/1075766126-1-100026.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1680245032&gen=playurlv2&os=bcache&oi=3549361989&trid=0000f203e675bd1c4be29a8b0a73928ad921u&mid=438162145&platform=pc&upsig=6a2f4c398323c0a573711962fb43ef2e&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform&cdnid=3247&bvc=vod&nettype=0&orderid=0,3&buvid=E99B81BB-6571-0F50-92BD-53B7D40E6B7032816infoc&build=0&agrr=1&bw=171700&logo=80000000')
# main('https://xy183x138x42x253xy.mcdn.bilivideo.cn:4483/upgcxcode/26/61/1075766126/1075766126-1-30033.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1680242842&gen=playurlv2&os=mcdn&oi=1779585369&trid=0000ba697ad526f843a5903122b7c3b2dac4u&mid=0&platform=pc&upsig=539ee6dcb22b76897c7aa95816ad9ab4&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform&mcdnid=9003322&bvc=vod&nettype=0&orderid=0,3&buvid=&build=0&agrr=1&bw=42629&logo=A0000100')
# main('https://xy115x219x12x11xy.mcdn.bilivideo.cn:4483/upgcxcode/26/61/1075766126/1075766126_nb3-1-30032.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1680242842&gen=playurlv2&os=mcdn&oi=1779585369&trid=0000ba697ad526f843a5903122b7c3b2dac4u&mid=0&platform=pc&upsig=dcf7939e4153ac254be15cb122fc50ed&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform&mcdnid=9003322&bvc=vod&nettype=0&orderid=0,3&buvid=&build=0&agrr=1&bw=41920&logo=A0000100')
# content_length = get_content_length('https://xy115x219x12x11xy.mcdn.bilivideo.cn:4483/upgcxcode/26/61/1075766126/1075766126_nb3-1-30032.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1680242842&gen=playurlv2&os=mcdn&oi=1779585369&trid=0000ba697ad526f843a5903122b7c3b2dac4u&mid=0&platform=pc&upsig=dcf7939e4153ac254be15cb122fc50ed&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform&mcdnid=9003322&bvc=vod&nettype=0&orderid=0,3&buvid=&build=0&agrr=1&bw=41920&logo=A0000100')
# print(content_length)
# with open('start.mp4', 'wb') as f:
#     f.write(response.content)
