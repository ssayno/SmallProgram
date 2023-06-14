import requests
import json

headers = {
    'Host': 'www.douyin.com',
    'Cookie': 'douyin.com; csrf_session_id=ac09441a0363780e12cf4bfd628099ff; n_mh=BLcApAJyDWG0xwZfiZl8GXR4GDSJyJhMmvIui04m6B4; LOGIN_STATUS=1; store-region=cn-hn; store-region-src=uid; my_rd=1; passport_csrf_token=23a0209e2181c9e854ed8eb05074c6bb; passport_csrf_token_default=23a0209e2181c9e854ed8eb05074c6bb; ttwid=1%7CGZldnMxhnHJODhbmLRtY9da54DtBzHabMxb8Qb8RRGk%7C1679756615%7C9dde9a5f5db2fc659b5a17ebc8b71f1e19f513f4ca2bd12232ed9a133e8d385e; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtY2xpZW50LWNlcnQiOiItLS0tLUJFR0lOIENFUlRJRklDQVRFLS0tLS1cbk1JSUNGVENDQWJ1Z0F3SUJBZ0lWQU1rNER4OXlsOVd2bnZxYmRSZEluSEdhaGtxVE1Bb0dDQ3FHU000OUJBTUNcbk1ERXhDekFKQmdOVkJBWVRBa05PTVNJd0lBWURWUVFEREJsMGFXTnJaWFJmWjNWaGNtUmZZMkZmWldOa2MyRmZcbk1qVTJNQjRYRFRJek1ETXdNakV6TVRRek1sb1hEVE16TURNd01qSXhNVFF6TWxvd0p6RUxNQWtHQTFVRUJoTUNcblEwNHhHREFXQmdOVkJBTU1EMkprWDNScFkydGxkRjluZFdGeVpEQlpNQk1HQnlxR1NNNDlBZ0VHQ0NxR1NNNDlcbkF3RUhBMElBQkg1OFpVdFl6bUg5N210NDdmOXB5bkNpcnk1SHRYV2RBaFNvMnQwK01qTHcvdkgzdDdzNktQRFFcbjF0RC9SSHVPdDBOZ3Vua1B2Z1Q0SEtndGthY0EyY3VqZ2Jrd2diWXdEZ1lEVlIwUEFRSC9CQVFEQWdXZ01ERUdcbkExVWRKUVFxTUNnR0NDc0dBUVVGQndNQkJnZ3JCZ0VGQlFjREFnWUlLd1lCQlFVSEF3TUdDQ3NHQVFVRkJ3TUVcbk1Da0dBMVVkRGdRaUJDQkNmbEZ2eG9qWndMSUE0WnJiL2lGZDVkeGNRVlFtWWloM0hhYlR5d3VqUVRBckJnTlZcbkhTTUVKREFpZ0NBeXBXZnFqbVJJRW8zTVRrMUFlM01VbTBkdFUzcWswWURYZVpTWGV5SkhnekFaQmdOVkhSRUVcbkVqQVFnZzUzZDNjdVpHOTFlV2x1TG1OdmJUQUtCZ2dxaGtqT1BRUURBZ05JQURCRkFpQjh6NkVvcHlqV1NEN1Jcbk5sTTNJbEZqczBCQmFPQTVsSjRtdGZtNDJ4K2sxZ0loQU9SYmhGUDh1Q1BKZTFiOU5CdXhRVzltbHZYTUtwUEhcblZtOWVPcDAvTFVCWVxuLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLVxuIn0=; pwa2=%223%7C0%22; d_ticket=cd0a3c45ea22dda0eb9d0cd662afadf581c18; passport_assist_user=CkFaGGalJgWNEopf9mT6zqZ1qTmA_FNul-UMzbSt1TWm5qvKRwWClO1YN6-_XXyUwy2VjBZX5HN60_6b079g85E7sBpICjzhL0og2lcjKKIrwlm0EqwVmGP_In2fwhkpk_qQcA2XmMNhPwgVeZkf4Ihro4HsCietbF_KCaQMkk9UGssQmpeuDRiJr9ZUIgEDOgnmOg%3D%3D; sso_auth_status=5564f71cbf3d90e5c3e02dda8f185c55; sso_auth_status_ss=5564f71cbf3d90e5c3e02dda8f185c55; sso_uid_tt=c8c76c12eea4227789073943a53016b2; sso_uid_tt_ss=c8c76c12eea4227789073943a53016b2; toutiao_sso_user=0575a4f4b481fa8954a1d1913264bfbb; toutiao_sso_user_ss=0575a4f4b481fa8954a1d1913264bfbb; sid_ucp_sso_v1=1.0.0-KGEwY2MwYzQwOGU2YjdjMDNkMzM2Yzc3Mjg0ZDg0OGM0NzE1NDVlNzYKHwiHnPGXmPTDBhC5rdOhBhjvMSAMMPje4PgFOAJA8QcaAmxxIiAwNTc1YTRmNGI0ODFmYTg5NTRhMWQxOTEzMjY0YmZiYg; ssid_ucp_sso_v1=1.0.0-KGEwY2MwYzQwOGU2YjdjMDNkMzM2Yzc3Mjg0ZDg0OGM0NzE1NDVlNzYKHwiHnPGXmPTDBhC5rdOhBhjvMSAMMPje4PgFOAJA8QcaAmxxIiAwNTc1YTRmNGI0ODFmYTg5NTRhMWQxOTEzMjY0YmZiYg; odin_tt=a9fcad05f517126bacc16d61cb9c9335d946b24076b19d6ade699ae8882dd1f302d8ad050cdde14c152729acf75297dde01ccecb2bdf3ee836a73ee4af2ba4e1; passport_auth_status=7a13eda100dbf44a87ed5f49122f43ca%2Cacb8d6b9a910fc8307050679c4bba75d; passport_auth_status_ss=7a13eda100dbf44a87ed5f49122f43ca%2Cacb8d6b9a910fc8307050679c4bba75d; uid_tt=6700ae6f51be78be000b9005e4b9fb17; uid_tt_ss=6700ae6f51be78be000b9005e4b9fb17; sid_tt=7d42acd90a064e40dd669b0864548d29; sessionid=7d42acd90a064e40dd669b0864548d29; sessionid_ss=7d42acd90a064e40dd669b0864548d29; bd_ticket_guard_server_data=; sid_guard=7d42acd90a064e40dd669b0864548d29%7C1681184444%7C5184000%7CSat%2C+10-Jun-2023+03%3A40%3A44+GMT; sid_ucp_v1=1.0.0-KGNlYTljMmIxMzAyMjJkYWJlMTQzNmM1M2JhZmU0MjQ0MzlkNTc4OGUKGwiHnPGXmPTDBhC8rdOhBhjvMSAMOAJA8QdIBBoCaGwiIDdkNDJhY2Q5MGEwNjRlNDBkZDY2OWIwODY0NTQ4ZDI5; ssid_ucp_v1=1.0.0-KGNlYTljMmIxMzAyMjJkYWJlMTQzNmM1M2JhZmU0MjQ0MzlkNTc4OGUKGwiHnPGXmPTDBhC8rdOhBhjvMSAMOAJA8QdIBBoCaGwiIDdkNDJhY2Q5MGEwNjRlNDBkZDY2OWIwODY0NTQ4ZDI5; download_guide=%223%2F20230427%22; s_v_web_id=verify_lh5r8c39_t2qhW0hg_pk36_4h74_8pgf_wbE3IWKmXQmU; SEARCH_RESULT_LIST_TYPE=%22single%22; passport_fe_beating_status=true; publish_badge_show_info=%220%2C0%2C0%2C1683174130961%22; strategyABtestKey=%221683174161.466%22; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAAUk3PzAQOgaWgNbUQfb8aM37EWvkA0IGP4VTE-7e3TPjW3YFpdqVihxgQjXaqi4Hy%2F1683216000000%2F0%2F0%2F1683178639810%22; VIDEO_FILTER_MEMO_SELECT=%7B%22expireTime%22%3A1683791009515%2C%22type%22%3A1%7D; tt_scid=APkZzRWkM5n2Zdge2ukbPMpnOZIvT1l1bBHW7VFQIDfPjfaVz68clShrGWJ0bBeJ68ef; msToken=0xDIk_Cmj782kKA33iMk6GeioICNbfbbDAuj6xqnxnzh1g42VctaVKqjU12Ff225HbCc4uxQzoNuj09NN_ug3Mw1O8fiAKJCxOWKUNDQfRc557nwGHDINQ==; msToken=jh4WPpyA6QTPjYPaEQzeNKfa6vDv9e2eWQ5I77wKTF37NwxfUOG5oYg5wWZqvGai_qLG6FUVgFgSSZFMEzcUu7NCKuAWJhAxWIC7RdU5vYV9N4FGjkE4cQ==; __ac_nonce=064537a2500c1d3d61530; __ac_signature=_02B4Z6wo00f017qahOAAAIDA6u3AGnGi6fe6uoBAAIr-2jjSStkmul3hvj2aYAjz5D7aWlvIRF7E-w-fxsgXuNBIx15dV2nJ-H3NyQ7WJ2D03vTtz4SbCM8eWDSVv6aC.mYl7DbGpBp6UKKbe3; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAAUk3PzAQOgaWgNbUQfb8aM37EWvkA0IGP4VTE-7e3TPjW3YFpdqVihxgQjXaqi4Hy%2F1683216000000%2F0%2F0%2F1683192960644%22; home_can_add_dy_2_desktop=%220%22',
    'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
    'accept': 'application/json, text/plain, */*',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.douyin.com/user/MS4wLjABAAAAR8QnhkZE2vfsBSpz6NeFqW2iKVyYOjTU2-PM8g3Dypo?showTab=post&vid=7225582677540343052',
    'accept-language': 'zh,zh-CN;q=0.9',
}

url = "https://www.douyin.com/aweme/v1/web/aweme/post/"
params = {
    "device_platform": "webapp",
    "aid": "6383",
    "channel": "channel_pc_web",
    "sec_user_id": "MS4wLjABAAAAR8QnhkZE2vfsBSpz6NeFqW2iKVyYOjTU2-PM8g3Dypo",
    "max_cursor": "1678963841000",
    "locate_item_id": "7225582677540343052",
    "locate_query": "false",
    "show_live_replay_strategy": "1",
    "count": "10",
    "publish_video_strategy_type": "2",
    "pc_client_type": "1",
    "version_code": "170400",
    "version_name": "17.4.0",
    "cookie_enabled": "true",
    "screen_width": "2560",
    "screen_height": "1600",
    "browser_language": "zh",
    "browser_platform": "MacIntel",
    "browser_name": "Chrome",
    "browser_version": "112.0.0.0",
    "browser_online": "true",
    "engine_name": "Blink",
    "engine_version": "112.0.0.0",
    "os_name": "Mac OS",
    "os_version": "10.15.7",
    "cpu_core_num": "8",
    "device_memory": "8",
    "platform": "PC",
    "downlink": "1.75",
    "effective_type": "4g",
    "round_trip_time": "250",
    "webid": "7214499669790213664",
    "msToken": "jh4WPpyA6QTPjYPaEQzeNKfa6vDv9e2eWQ5I77wKTF37NwxfUOG5oYg5wWZqvGai_qLG6FUVgFgSSZFMEzcUu7NCKuAWJhAxWIC7RdU5vYV9N4FGjkE4cQ==",
    "X-Bogus": "DFSzswVOwUbANt0TtCACffok/RBa"
}
string_params = '?'
for key, value in params.items():
    string_params += f'{key}={value.replace(" ", "+")}&'
print(string_params)
url += string_params[:-1]
print(url)
response = requests.get(url, headers=headers)

with open('zst.json', 'w+') as f:
    json.dump(response.json(), f)
