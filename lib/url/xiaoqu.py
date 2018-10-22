#!/usr/bin/env python
# coding=utf-8
# author: zengyuetian

import re
import requests
from bs4 import BeautifulSoup
from lib.url.url_helper import *
from lib.item.xiaoqu import *
from lib.city.district import *
from lib.const.request_headers import *
from lib.utility.log import logger
from lib.const.spider import SPIDER_NAME


def get_xiaoqu_info(city, area):
    district = area_dict.get(area, "")
    chinese_district = get_chinese_district(district)
    chinese_area = chinese_area_dict.get(area, "")
    xiaoqu_list = list()
    page = 'http://{0}.{1}.com/xiaoqu/{2}/'.format(city, SPIDER_NAME, area)
    print(page)
    logger.info(page)

    headers = create_headers()
    response = requests.get(page, timeout=10, headers=headers)
    html = response.content
    soup = BeautifulSoup(html, "lxml")

    # 获得总的页数
    try:
        page_box = soup.find_all('div', class_='page-box')[0]
        matches = re.search('.*"totalPage":(\d+),.*', str(page_box))
        total_page = int(matches.group(1))
    except Exception as e:
        print("\tWarning: only find one page for {0}".format(area))
        print(e)
        total_page = 1

    # print("total page %d" % total_page)
    # last_page = soup.find('a', gahref="results_totalpage")
    # if last_page is not None:  # 如果找到了标示最后一页的链接
    #     total_page = int(last_page.text)
    # else:   # 没有标示最后一页的链接,那么总页数不超过10,从大到小倒序找到最后一页
    #     href_list = ["results_d{0}".format(i) for i in range(10+1)[1:]]
    #     href_list.reverse()
    #     for href in href_list:
    #         last_page = soup.find('a', gahref=href)
    #         if last_page is not None:
    #             total_page = int(last_page.text)
    #             break

    # 从第一页开始,一直遍历到最后一页
    for i in range(1, total_page + 1):
        headers = create_headers()
        page = 'http://{0}.{1}.com/xiaoqu/{2}/pg{3}'.format(city, SPIDER_NAME, area, i)
        response = requests.get(page, timeout=10, headers=headers)
        html = response.content
        soup = BeautifulSoup(html, "lxml")

        # 获得有小区信息的panel
        house_elems = soup.find_all('li', class_="xiaoquListItem")
        for house_elem in house_elems:
            price = house_elem.find('div', class_="totalPrice")
            name = house_elem.find('div', class_='title')
            on_sale = house_elem.find('div', class_="xiaoquListItemSellCount")

            # 继续清理数据
            price = price.text.strip()
            name = name.text.replace("\n", "")
            on_sale = on_sale.text.replace("\n", "").strip()

            # 作为对象保存
            xiaoqu = XiaoQu(chinese_district, chinese_area, name, price, on_sale)
            xiaoqu_list.append(xiaoqu)
    return xiaoqu_list


if __name__ == "__main__":
    # urls = get_xiaoqu_area_urls()
    # print urls
    get_xiaoqu_info("sh", "beicai")
