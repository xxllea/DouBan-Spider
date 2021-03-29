# -*- coding: utf-8 -*-

import re
import json
import requests
from lxml import etree


class PersonPageParse:
    def __init__(self, person_id, person_info_html):
        """
        初始化
        :param person_url:
        :param person_info_html:
        """
        self.person_id = person_id
        self.person_info_html = person_info_html
        self.person_html = etree.HTML(person_info_html)
        div_element = self.person_html.xpath('//div[@class="info"]/ul')[0]
        self.div_html = etree.tostring(div_element, pretty_print=True, encoding='utf-8').decode('utf-8')

    def _get_person_name(self):
        """
        得到作者名称
        :return:
        """
        try:
            name = self.person_html.xpath('//div[@id="content"]/h1/text()')
        except Exception as err:
            name = ''
        return name

    def _get_person_image_url(self):
        """
        得到作者图片链接
        :return:
        """
        try:
            image_url = self.person_html.xpath('//div[@class="nbg"]/img/@src')
        except Exception as err:
            image_url = ''
        return image_url

    def _get_person_birthday(self):
        """
        获取作者出生日期
        :return:
        """
        try:
            birthday = re.search(r"生卒日期</span>:(.*?)</li>", self.div_html, re.S).group(1).strip()     
        except Exception as err:
            birthday = ''
        return birthday

    def _get_person_country(self):
        """
        获取作者国家/地区
        :return:
        """
        try:
            country = re.search(r"国家/地区</span>:(.*?)</li>", self.div_html, re.S).group(1).strip()     
        except Exception as err:
            country = ''
        return country

    def _get_person_other_chinese_name(self):
        """
        获取作者其他中文名称
        :return:
        """
        try:
            other_chinese_name = re.search(r"更多中文名</span>:(.*?)</li>", self.div_html, re.S).group(1).strip()     
        except Exception as err:
            other_chinese_name = ''
        return other_chinese_name
        
    def _get_person_other_english_name(self):
        """
        获取作者其他英文名称
        :return:
        """
        try:
            other_english_name = re.search(r"更多外文名</span>:(.*?)</li>", self.div_html, re.S).group(1).strip()     
        except Exception as err:
            other_english_name = ''
        return other_english_name
    
    def _get_person_introduction(self):
        """
        获取作者介绍
        :return:
        """
        try:
            introduction = self.person_html.xpath("//div[@class='bd']/span[@class='all hidden']/text()")[0]
        except Exception as err:
            introduction = ''
        return introduction

    def parse(self):
        """
        获取作者信息
        :return:
        """
        name = self._get_person_name()  # 作者名称
        image_url = self._get_person_image_url()  # 作者图片链接
        # gender = self._get_person_gender()  # 作者性别
        birthday = self._get_person_birthday()  # 作者出生日期
        country = self._get_person_country()  # 作者国家
        other_chinese_name = self._get_person_other_chinese_name()  # 作者其他中文名称
        other_english_name = self._get_person_other_english_name()  # 作者其他英文名称
        introduction = self._get_person_introduction()  # 作者介绍

        person_info_json = {
            'id': self.person_id,
            'name': name,
            'image_url': image_url,
            # 'gender': gender,
            'birthday': birthday,
            'country': country,
            'other_chinese_name': other_chinese_name,
            'other_english_name': other_english_name,
            'introduction': introduction
        }
        return person_info_json

if __name__ == '__main__':
    person_id = '1039386'
    person_url = 'https://book.douban.com/author/' + str(person_id)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36"}
    person_info_html  = requests.get(person_url, headers=headers).text
    person_page_parse = PersonPageParse(person_id, person_info_html)
    person_info_json = person_page_parse.parse()
    with open("person.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(person_info_json, ensure_ascii=False, indent=2))