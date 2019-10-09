# -*- coding: utf-8 -*-
import scrapy
from hashlib import md5
import json
import time, random
from ..items import YoudaoItem


class YoudaoSpider(scrapy.Spider):
    name = 'youdao'
    allowed_domains = ['fanyi.youdao.com']

    word = input("请输入单词:")

    # 重写start_urls = ['http://fanyi.youdao.com/'],进行表单提交
    def start_requests(self):
        post_url = 'http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'
        salt, sign, ts = self.get_salt_sign_ts(self.word)
        formdata = {
            'i': self.word,
            'from': 'AUTO',
            'to': 'AUTO',
            'smartresult': 'dict',
            'client': 'fanyideskweb',
            'salt': salt,
            'sign': sign,
            'ts': ts,
            'bv': '93ab8a54b571f3ceac16a13fbb95fb1c',
            'doctype': 'json',
            'version': '2.1',
            'keyfrom': 'fanyi.web',
            'action': 'FY_BY_CLICKBUTTION'
        }
        cookies = self.get_cookies()
        yield scrapy.FormRequest(
            url=post_url,
            formdata=formdata,
            cookies=cookies,
            callback=self.parse
        )

    def get_cookies(self):
        cookies = {}
        string = "OUTFOX_SEARCH_USER_ID=121525442@10.168.8.76; JSESSIONID=aaaeAxJ2oMQf1cVAYUQ2w; OUTFOX_SEARCH_USER_ID_NCOO=932692021.0825853; ___rl__test__cookies=1570527812851"
        for s in string.split('; '):
            cookies[s.split('=')[0]] = s.split('=')[1]

        return cookies

    def get_salt_sign_ts(self, word):
        ts = str(int(time.time() * 1000))
        salt = ts + str(random.randint(0, 9))
        string = "fanyideskweb" + word + salt + "n%A-rKaT5fb[Gy?;N5@Tj"
        s = md5()
        s.update(string.encode())
        sign = s.hexdigest()
        return salt, sign, ts

    def parse(self, response):
        item = YoudaoItem()
        html = json.loads(response.text)
        item['result'] = html['translateResult'][0][0]['tgt']
        yield item
