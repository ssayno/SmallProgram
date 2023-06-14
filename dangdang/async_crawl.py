import csv
from bs4 import BeautifulSoup
import asyncio
import aiohttp

search_type = 'python'

lock = asyncio.Lock()
csv_file = open(f'{search_type}-result.csv', 'w+', encoding='U8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow([
    '类型', '书名', '出版日期', '出版社', '现价', '原价', '折扣', '详细说明', '图片地址'
])


async def crawl_single_page(url, session, params, page_index):
    try:
        params["page_index"] = page_index
        async with session.get(url, params=params) as resp:
            html_text = await resp.text(encoding="gbk")
            await extract_info(html_text)
        await asyncio.sleep(4)
    except Exception as e:
        print(e)
        return
    # use async with statement, we needn't type `resp.close()`
    # resp = await session.get(url, params=params)
    # page_count = await get_page_count(resp)
    # resp.close()
    # return page_count


async def get_page_count(url, session, init_params):
    init_params["page_index"] = 1
    async with session.get(url, params=init_params) as resp:
        html_text = await resp.text(encoding="gbk")
    soup = BeautifulSoup(html_text, 'lxml')
    pages = soup.find_all(name='a', attrs={"name": "bottom-page-turn"})[-1].text
    return pages


async def extract_info(html_text):
    soup = BeautifulSoup(html_text, 'lxml')
    li_tags = soup.select('#component_59 > li')
    result_maps = []
    for li_tag in li_tags:
        # get image url
        image_tag = li_tag.find('img')
        image_src = image_tag.attrs['src']
        if 'none' in image_src:
            image_src = image_tag.attrs['data-original']
        if not image_src.startswith('https:'):
            image_src = f'https:{image_src}'
        # get title
        title_p = li_tag.find('p', attrs={"class": "name", "name": "title"})
        book_name = title_p.text
        # detail
        detail_p = li_tag.find('p', attrs={"class": "detail"})
        details = detail_p.text
        # print(details)
        # price
        price_p = li_tag.find('p', attrs={"class": "price"})
        now_price = price_p.find('span', attrs={"class": "search_now_price"}).text
        previous_price = price_p.find('span', attrs={"class": "search_pre_price"})
        if previous_price is None:
            previous_price = now_price
        else:
            previous_price = previous_price.text
        discount = price_p.find('span', attrs={"class": "search_discount"})
        if discount is None:
            discount = "10折"
        else:
            discount = discount.text.replace(
                '\xa0', ''
            ).replace('(', '').replace(')', '')
        # print(now_price, previous_price, discount)
        # search author
        search_author = li_tag.find('p', attrs={"class": "search_book_author"})
        infos = search_author.find_all('span')
        author = infos[0].text
        publish_data = infos[1].text.lstrip(' /')
        press = infos[2].text.lstrip(' /')
        # print(author, publish_data, press)
        result_maps.append([
            search_type, book_name, publish_data, press, now_price, previous_price, discount, details, image_src
        ])
    async with lock:
        csv_writer.writerows(result_maps)


async def main(search_type):
    headers = {
        "Host": "search.dangdang.com",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Referer": "http://search.dangdang.com/?key=python&SearchFromTop=1&catalog=",
        "Accept-Language": "zh,zh-CN;q=0.9",
        "Proxy-Connection": "keep-alive"
    }
    cookies = {
        "ddscreen": "2",
        "__permanent_id": "20230429171130828225542237863733452",
        "__ddc_15d": "1682759491%7C!%7C_ddclickunion%3DP-129054",
        "__ddc_15d_f": "1682759491%7C!%7C_ddclickunion%3DP-129054",
        "__visit_id": "20230430210302289132255947777442641",
        "__out_refer": "1682859782%7C!%7Cwww.google.com%7C!%7C",
        "dest_area": "country_id%3D9000%26province_id%3D111%26city_id%3D0%26district_id%3D0%26town_id%3D0",
        "__rpm": "...1682859810817%7Cs_112100.155956512835%2C155956512836..1682860072930",
        "search_passback": "91da83bf7b229c4f29684e64fc0100002aa86400ad664e64",
        "__trace_id": "20230430210753806298993738680917559",
        "pos_9_end": "1682860074018",
        "pos_0_end": "1682860074075",
        "ad_ids": "31898396%2C14129493%2C5066933%7C%233%2C3%2C3",
        "pos_0_start": "1682860303914"
    }
    url = "http://search.dangdang.com/"
    params = {
        "key": search_type,
        "SearchFromTop": "1",
        "catalog": "",
    }
    #
    tasks = []
    session = aiohttp.ClientSession(headers=headers, cookies=cookies)
    pages = await get_page_count(url, session, init_params=params)
    print(pages)
    for i in range(1, 100):
        in_page_index = i + 1
        tasks.append(
            crawl_single_page(url, session, params=params, page_index=in_page_index)
        )
    await asyncio.gather(*tasks)
    await session.close()


if __name__ == '__main__':
    asyncio.run(main(search_type))
    csv_file.close()
