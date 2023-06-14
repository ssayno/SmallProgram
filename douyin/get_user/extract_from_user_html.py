import json
import pprint
from os import sysconf

from bs4 import BeautifulSoup
from urllib.parse import unquote
with open('zst.html', 'r') as f:
    resp = f.read()

soup = BeautifulSoup(resp, 'lxml')
read_data = soup.select('#RENDER_DATA')[0].text
# pprint.pprint(
#     json.loads(unquote(read_data))
# )

tcc = None
video_filter_type = None
globalwid = None
web_id = None
enable_recommend_cache = None
recommend_feed_cache = None
after_lcp_execute = None
ff_danmaku_status = 0
danmaku_switch_status = 0


parsed_render_data = json.loads(unquote(read_data))

for render_key in parsed_render_data:
    val = parsed_render_data.get(render_key, {})
    if 'tccConfig' in val:
        tcc = val['tccConfig']
        if tcc and 'enable_recommend_cache' in tcc:
            enable_recommend_cache = tcc['enable_recommend_cache']['enable']
    if 'videoTypeSelect' in val:
        video_filter_type = val['videoTypeSelect']
    if 'recommendFeedCache' in val:
        recommend_feed_cache = val['recommendFeedCache']
    if 'globalwid' in val:
        globalwid = val['globalwid']
    if 'odin' in val and 'user_unique_id' in val['odin']:
        web_id = val['odin']['user_unique_id']
    if 'abTestData' in val:
        after_lcp_execute = val['abTestData']['afterLcpExecute']
    if 'ffDanmakuStatus' in val:
        ff_danmaku_status = 1 if val['ffDanmakuStatus'] and sysconf('SC_NPROCESSORS_ONLN') > 4 else 0
    if 'danmakuSwitchStatus' in val:
        danmaku_switch_status = val['danmakuSwitchStatus']

result = {
    'tcc': tcc,
    'globalwid': globalwid or '',
    'webId': web_id or '',
    'videoFilterType': video_filter_type,
    'enableRecommendCache': enable_recommend_cache,
    'recommendFeedCache': recommend_feed_cache,
    'afterLcpExecute': after_lcp_execute,
    'done': tcc is not None and video_filter_type is not None,
    'ffDanmakuStatus': ff_danmaku_status,
    'danmakuSwitchStatus': danmaku_switch_status
}
print("??????")
pprint.pprint(
    result
)