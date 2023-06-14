import pprint

from src.get_search_result_with_api import get_search_result_with_keyword
from src.get_music_uri import get_single_music_url


def extract_all_rid(music_list):
    rids = []
    for item in music_list:
        rids.append(item['rid'])
        info = get_single_music_url(item['rid'])
        print(info)
    return rids


if __name__ == '__main__':
    search_key = 'shape of you'
    search_result = get_search_result_with_keyword('shape of you')
    all_rids = extract_all_rid(search_result)
    # print(all_rids)
    # first_rid = search_result[5]['rid']
    # single_music_info = get_single_music_url(first_rid)
    # pprint.pprint(single_music_info)

