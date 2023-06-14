def get_kuwo_headers():
    return {
        'Host': 'www.kuwo.cn',
        'Accept': 'application/json, text/plain, */*',
        'csrf': 'Y5JAAJ9GY9',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'Referer': 'https://www.kuwo.cn/',
        'Accept-Language': 'zh,zh-CN;q=0.9',
        # 'Cookie': 'Hm_lvt_cdb524f42f0ce19b169a8071123a4797=1685615670; _ga=GA1.2.93166612.1685615672; _gid=GA1.2.410552104.1685615672; gtoken=fB4wS7mE2pYU; gid=a3feedcf-4b99-4d08-9b0f-40f355978eb6; Hm_lpvt_cdb524f42f0ce19b169a8071123a4797=1685615719; kw_token=Y5JAAJ9GY9; _gat=1',
        'origin': 'https://www.kuwo.cn/',
        'Proxy-Connection': 'keep-alive',
    }