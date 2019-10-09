import requests
from lxml import etree
import time, random
from useragents import ua_list
import csv
from queue import Queue
from threading import Thread


class LianjiaSpider(object):
    def __init__(self):
        self.url = 'https://bj.lianjia.com/ershoufang/pg{}/'
        self.blog = 1
        self.q = Queue()
        # 用来存储爬取的数据
        self.item_list = []

    def get_html(self, url):
        headers = {'User-Agent': random.choice(ua_list)}
        # 尝试3次,否则换下一页地址
        if self.blog <= 3:
            try:
                res = requests.get(url=url, headers=headers, timeout=3)
                res.encoding = 'utf-8'
                html = res.text
                return html
            except Exception as e:
                print("等待响应失败", e)
                self.blog += 1
                self.get_html(url)

    def parse_page(self):
        while True:
            if not self.q.empty():
                url = self.q.get()
                html = self.get_html(url)
                parse_HTML = etree.HTML(html)
                # li_list = [<element li at xxx>, ]
                li_list = parse_HTML.xpath('//ul[@class="sellListContent"]/li[@class="clear LOGVIEWDATA LOGCLICKDATA"]')
                item = {}
                for li in li_list:
                    # 名称
                    name_list = li.xpath('.//a[@data-el="region"]/text()')
                    item['name'] = [name_list[0].strip() if name_list else '无名'][0]
                    # 户型+面积+方位+是否精装
                    info_list = li.xpath('.//div[@class="houseInfo"]/text()')
                    if info_list:
                        info_list = info_list[0].strip().split('|')
                        if len(info_list) == 5:
                            item['model'] = info_list[1].strip()
                            item['area'] = info_list[2].strip()
                            item['direction'] = info_list[3].strip()
                            item['perfect'] = info_list[4].strip()
                        else:
                            item['model'] = item['area'] = \
                                item['direction'] = item['perfect'] = None
                    else:
                        print("缺少房源信息")
                    # 楼层
                    xpath_floor = './/div[@class="positionInfo"]/text()'
                    floor_list = li.xpath(xpath_floor)
                    item['floor'] = [floor_list[0].strip().split()[0]
                                     if floor_list else None][0]
                    # 地区
                    add_list = li.xpath('.//div[@class="positionInfo"]/a/text()')
                    item['address'] = [add_list[0].strip() if add_list else None][0]
                    # 总价
                    tprice_list = li.xpath('.//div[@class="totalPrice"]/span/text()')
                    item['total_price'] = [tprice_list[0].strip()
                                           if tprice_list else None][0]
                    # 单价
                    price_list = li.xpath('.//div[@class="unitPrice"]/span/text()')
                    item['unit_price'] = [price_list[0].strip()
                                          if price_list else None][0]
                    #
                    self.item_list.append(tuple(item.values()))
            else:
                break

    def write_csv(self):
        '''存入csv文件'''
        with open('lianjia.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(self.item_list)

    def main(self):
        # 入队
        for pg in range(1, 101):
            url = self.url.format(pg)
            self.q.put(url)
            # 对self.blog初始化
            self.blog = 1
        t_list = []
        for i in range(8):
            t = Thread(target=self.parse_page)
            t_list.append(t)
            t.start()
        for t in t_list:
            t.join()
        self.write_csv()


if __name__ == '__main__':
    start = time.time()
    spider = LianjiaSpider()
    spider.main()
    end = time.time()
    print("执行时间:%.2fs" % (end - start))
