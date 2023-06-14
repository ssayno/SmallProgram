import json

import requests

cookies = {
    'buvid3': 'E99B81BB-6571-0F50-92BD-53B7D40E6B7032816infoc',
    'b_nut': '1670581032',
    'i-wanna-go-back': '-1',
    '_uuid': '3A12B965-8FC4-D7FB-5FF6-48C27AFA4BF736048infoc',
    'buvid4': '2B6A1135-0EC4-9EE4-00E6-979547D1411438734-022120918-w5t72nCohojWwSIokURtDg%3D%3D',
    'nostalgia_conf': '-1',
    'LIVE_BUVID': 'AUTO9316706721368393',
    'PVID': '1',
    'rpdid': "|(JlRmJYummk0J'uY~|~YJmRJ",
    'bsource': 'search_google',
    'buvid_fp_plain': 'undefined',
    'DedeUserID': '438162145',
    'DedeUserID__ckMd5': 'e5b24933eabd685d',
    'b_ut': '5',
    'CURRENT_QUALITY': '80',
    'header_theme_version': 'CLOSE',
    'CURRENT_PID': '058791b0-af3d-11ed-9b19-2f4d36471575',
    'fingerprint': 'c582e2fa716beab1c233389ef9eb7b40',
    'buvid_fp': '74be26d4fcf2e3e3e04a8f3384a52601',
    'CURRENT_BLACKGAP': '0',
    'CURRENT_FNVAL': '4048',
    'bp_video_offset_438162145': '771071544692572200',
    'home_feed_column': '4',
    'SESSDATA': 'c73585d9%2C1695740224%2Cc461f%2A31',
    'bili_jct': '6d5ad6d4e70a58a7400f1fc684059c6e',
    'sid': '5jex1q33',
    'theme_style': 'light',
    'innersign': '1',
    'b_lsid': 'A1010AFDE8_18735F15495',
}

headers = {
    'Host': 'api.bilibili.com',
    # 'Cookie': "buvid3=E99B81BB-6571-0F50-92BD-53B7D40E6B7032816infoc; b_nut=1670581032; i-wanna-go-back=-1; _uuid=3A12B965-8FC4-D7FB-5FF6-48C27AFA4BF736048infoc; buvid4=2B6A1135-0EC4-9EE4-00E6-979547D1411438734-022120918-w5t72nCohojWwSIokURtDg%3D%3D; nostalgia_conf=-1; LIVE_BUVID=AUTO9316706721368393; PVID=1; rpdid=|(JlRmJYummk0J'uY~|~YJmRJ; bsource=search_google; buvid_fp_plain=undefined; DedeUserID=438162145; DedeUserID__ckMd5=e5b24933eabd685d; b_ut=5; CURRENT_QUALITY=80; header_theme_version=CLOSE; CURRENT_PID=058791b0-af3d-11ed-9b19-2f4d36471575; fingerprint=c582e2fa716beab1c233389ef9eb7b40; buvid_fp=74be26d4fcf2e3e3e04a8f3384a52601; CURRENT_BLACKGAP=0; CURRENT_FNVAL=4048; bp_video_offset_438162145=771071544692572200; home_feed_column=4; SESSDATA=c73585d9%2C1695740224%2Cc461f%2A31; bili_jct=6d5ad6d4e70a58a7400f1fc684059c6e; sid=5jex1q33; theme_style=light; innersign=1; b_lsid=A1010AFDE8_18735F15495",
    'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
    'accept': 'application/json, text/plain, */*',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'sec-ch-ua-platform': '"macOS"',
    'origin': 'https://www.bilibili.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.bilibili.com/',
    'accept-language': 'zh-CN,zh;q=0.9',
}

params = {
    'avid': '441645868',
    'bvid': 'BV1GL411Q7Ky',
    'cid': '1073313071',
    'qn': '80',
    'fnver': '0',
    'fnval': '4048',
    'fourk': '1',
    'gaia_source': '',
    'session': '89e47db896613c9ef170eb5362d38530',
    'w_rid': '2048e19828ea422ccda2d26e0369487e',
    'wts': '1680239591',
}

response = requests.get('https://api.bilibili.com/x/player/wbi/playurl', params=params, cookies=cookies, headers=headers)
with open('quality.json', 'w') as f:
    json.dump(response.json(), f, ensure_ascii=False, indent=4)
