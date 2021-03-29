# -*- coding: utf-8 -*-

import re
import requests
import json
from bs4 import BeautifulSoup


class BookPageParse:
    def __init__(self, book_id, book_info_html):
        """
        初始化 
        :param book_id:
        :param book_info_html:
        """
        self.book_id = book_id
        self.book_info_html = book_info_html
        self.book_soup = BeautifulSoup(self.book_info_html, "lxml")
    
    def _get_book_name(self):
        """   
        得到书籍名称
        :return: name 
        """
        try:
            name = self.book_soup.find("span", property="v:itemreviewed").text
        except Exception as err:
            name = ""
        return name
    
    def _get_book_image_url(self):
        """ 
        得到书籍图片链接
        : return: image_url
        """
        try:
            image_url = str(self.book_soup.find("img", rel="v:photo")["src"])
        except Exception as err:
            image_url = ""
        return image_url

    def _get_book_subtitle(self):
        """
        获取书籍副标题
        :return: subtitle
        """
        try:
            book_info = str(self.book_soup.find('div', id='info'))
            subtitle = re.search(r"副标题:</span>(.*?)<br/>", book_info).group(1).strip()
        except Exception as err:
            subtitle = ''
        return subtitle

    def _get_book_origin_name(self):
        """
        获取书籍原作名
        :return: origin_name（str）
        """
        try:
            book_info = str(self.book_soup.find('div', id='info'))
            origin_name = re.search(r'原作名:</span>(.*?)<br/>', book_info).group(1).strip()
        except Exception as err:
            origin_name = ''
        return origin_name

    def _get_book_author(self):
        """
        得到图书作者（list）
        :return: author_list
        """
        try:
            book_info = str(self.book_soup.find("div", id="info"))
            if '作者</span>' in book_info:
                author_str_list = re.findall(r'.*?作者</span>.*?href="(.*?)">(.*?)</a>', book_info, re.S)
            else:
                author_str_list = re.findall(r'.*?作者:</span>.*?href="(.*?)">(.*?)</a>', book_info, re.S)
            author_list = []
            for i in range(0, len(author_str_list)):
                author_str = author_str_list[i]
                author_name = author_str[1].replace("\n", "").replace(" ", "").strip()
                author_href = ''
                if '/author/' in author_str[0]:
                    author_href = author_str[0].strip()
                    author_href = re.sub(r".*?/author/", "", author_href).strip("/")
                author_dict = {
                    "name": author_name,
                    "href": author_href
                }
                author_list.append(author_dict)
        except Exception as err:
            author_list = []
        return author_list

    def _get_book_translator(self):
        """
        得到图书译者（list）
        :return: translator_list
        """
        try:
            book_info = str(self.book_soup.find("div", id="info"))
            if '译者</span>' in book_info:
                translator_str_list = re.findall(r'.*?译者</span>.*?href="(.*?)">(.*?)</a>', book_info, re.S)
            else:
                translator_str_list = re.findall(r'.*?译者:</span>.*?href="(.*?)">(.*?)</a>', book_info, re.S)
            translator_list = []
            for i in range(0, len(translator_str_list)):
                author_str = translator_str_list[i]
                author_name = author_str[1].replace("\n", "").replace(" ", "").strip()
                author_href = ''
                if '/author/' in author_str[0]:
                    author_href = author_str[0].strip()
                    author_href = re.sub(r".*?/author/", "", author_href).strip("/")
                author_dict = {"name": author_name, "href": author_href}
                translator_list.append(author_dict)
        except Exception as err:
            translator_list = []
        return translator_list
    
    def _get_book_press(self):
        """
        得到图书出版社信息
        :return: press
        """
        try:
            book_info = str(self.book_soup.find("div", id="info"))
            press = re.search(r"出版社:</span>(.*?)<br/>", book_info).group(1).strip()
        except Exception as err:
            press = ""
        return press
    
    def _get_book_publish_year(self):
        """
        得到图书出版年份
        :return: publish_year
        """
        try:
            book_info = str(self.book_soup.find("div", id="info"))
            publish_year = re.search(r"出版年:</span>(.*?)<br/>", book_info).group(1).strip()
        except Exception as err:
            publish_year = ""
        return publish_year
    
    def _get_book_page_num(self):
        """
        得到书籍页数
        :return: page_num
        """
        try:
            book_info = str(self.book_soup.find("div", id="info"))
            page_num = re.search(r"页数:</span>(.*?)<br/>", book_info).group(1).strip()
        except Exception as Err:
            page_num = ""
        return page_num

    def _get_book_price(self):
        """
        得到书籍价格
        :return: price
        """
        try:
            book_info = str(self.book_soup.find("div", id="info"))
            price = re.search(r"定价:</span>(.*?)<br/>", book_info).group(1).strip()
        except Exception as Err:
            price = ""
        return price
    
    def _get_book_content_abstract(self):
        """
        得到图书内容简介
        :return: content_abstract
        """
        try:
            content_abstract = self.book_soup.find_all("div", class_="intro")[0].text.strip()
        except Exception as Err:
            content_abstract = ""
        return content_abstract

    # def _get_book_catalog(self):
    #     """
    #     得到图书目录
    #     :return:
    #     """
    #     try:
    #         try:
    #             catalog_id = 'dir_' + str(self.book_id) + '_full'
    #             catalog = str(self.book_soup.find('div', id=catalog_id).text)
    #             catalog = catalog.replace(' ', '')
    #         except:
    #             catalog_id = 'dir_' + str(self.book_id) + '_short'
    #             catalog = str(self.book_soup.find('div', id=catalog_id).text)
    #             catalog = catalog.replace(' ', '')
    #     except Exception as err:
    #         catalog = ''
    #     return catalog

    def _get_book_rating(self):
        """
        得到书籍评分
        :return:
        """
        try:
            average = str(self.book_soup.find('strong', property='v:average').text).strip()
            reviews_count = str(self.book_soup.find('a', class_='rating_people').text)
            rating = {
                'average': average,
                'reviews_count': reviews_count
            }
        except Exception as err:
            rating = {
                'average': '',
                'reviews_count': ''
            }
        return rating

    def parse(self):
        """
        获取书籍信息
        :return: book_info_json
        """
        name = self._get_book_name()  # 书籍名称
        image_url = self._get_book_image_url()  # 书籍图片链接
        subtitle = self._get_book_subtitle()  # 书籍副标题
        origin_name = self._get_book_origin_name()  # 原作名
        author = self._get_book_author()  # 书籍作者
        translator = self._get_book_translator()  # 书籍译者
        press = self._get_book_press()  # 书籍出版社
        publish_year = self._get_book_publish_year()  # 书籍出版年份
        price = self._get_book_price()  # 书籍价格
        page_num = self._get_book_page_num()  # 书籍页数
        content_abstract = self._get_book_content_abstract()  # 图书内容简介
        # catalog = self._get_book_catalog()  # 图书目录
        rating = self._get_book_rating()  # 书籍评分

        book_info_json = {
            'id': self.book_id,
            'image_url': image_url,
            'name': name,
            'subtitle': subtitle,
            'origin_name': origin_name,
            'author': author,
            'translator': translator,
            'press': press,
            'publish_year': publish_year,
            'page_num': page_num,
            'price': price,
            'content_abstract': content_abstract,
            # 'catalog': catalog,
            'rating': rating
        }
        return book_info_json
    

if __name__ == '__main__':
    book_id = 27128608
    book_url = 'https://book.douban.com/subject/' + str(book_id)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36"}
    book_info_response = requests.get(book_url, headers=headers)
    book_info_html = book_info_response.text
    book_page_parse = BookPageParse(book_id, book_info_html)
    book_info_json = book_page_parse.parse()
    with open("book.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(book_info_json, ensure_ascii=False, indent=2))