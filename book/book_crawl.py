# -*- coding: utf-8 -*-

import requests
import logging
import logging.config
import yaml
import re
import json
import redis
from multiprocessing.dummy import Pool as ThreadPool
from lxml import etree
from book_page_parse import BookPageParse
from book_person_page_parse import PersonPageParse
import time
import random
import os


class DouBanBookSpider:
    def __init__(self):
        """
        爬虫初始化
        :param token: init user
        """

        # 请求头
        self.headers = {
            "User-Agent": "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.2; Trident/4.0; SLCC2; .NET CLR 2.0.50727; "
                          ".NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)"}

        # 初始化log
        try:
            log_config_file_path = '../log/book_log_config.yaml'
            with open(log_config_file_path, 'r', encoding="utf-8") as f:
                log_config = yaml.load(f)
                logging.config.dictConfig(log_config)
            self.book_spider_log = logging.getLogger('spider')
            self.book_spider_log.info('Logger初始化成功')
        except Exception as err:
            print('Logger初始化失败' + str(err))

        # 初始化配置
        try:
            spider_config_file_path = 'book_spider_config.yaml'
            with open(spider_config_file_path, 'r', encoding="utf-8") as f:
                spider_config = yaml.load(f)
                self.config = spider_config
                self.book_spider_log.info('Config初始化成功')
        except Exception as err:
            self.book_spider_log.error('Config初始化失败' + str(err))

        # 初始化redis
        try:
            redis_host = self.config['redis']['host']
            redis_port = self.config['redis']['port']
            self.redis_con = redis.Redis(host=redis_host, port=redis_port, db=0)
            # 刷新redis库
            self.redis_con.flushdb()
            self.book_spider_log.info('Redis初始化成功')
        except Exception as err:
            self.book_spider_log.error('Redis初始化失败' + str(err))

        # 初始化读取ua
        try:
            ua_list_file_path = '../proxy/ua_list.txt'
            self.ua_list = []
            with open(ua_list_file_path, 'r', encoding="utf-8") as f:
                line = f.readline()
                while line:
                    self.ua_list.append(line.strip('\n'))
                    line = f.readline()
            self.book_spider_log.info('UA初始化成功')
        except Exception as err:
            self.book_spider_log.error('UA初始化失败' + str(err))

        # 初始化文件
        try:
            book_info_file_path = '../data/book_info.txt'
            if os.path.exists(book_info_file_path):
                os.remove(book_info_file_path)
            person_info_file_path = '../data/book_person_info.txt'
            if os.path.exists(person_info_file_path):
                os.remove(person_info_file_path)
            self.book_spider_log.info('文件初始化成功')
        except Exception as err:
            self.book_spider_log.info('文件初始化失败' + str(err))

        # ip代理
        self.proxies = {"https": "https://123.101.141.18:47441"}
        # 请求过期时间
        self.timeout = self.config['timeout']

        self.book_spider_log.info('DouBan-Book-Spider初始化成功')

    def _set_random_sleep_time(self):
        """
        设置随机睡眠时间
        :return:
        """
        # 爬虫间隔时间
        self.sleep_time = random.randint(1, 2)

    def _set_random_ua(self):
        """
        设置随机ua
        :return:
        """
        ua_len = len(self.ua_list)
        rand = random.randint(0, ua_len - 1)
        self.headers['User-Agent'] = self.ua_list[rand]
        self.book_spider_log.info('当前ua为' + str(self.ua_list[rand]))

    @staticmethod
    def _read_ip_list():
        """
        读取ip文件
        :return:
        """
        ip_list_file_path = '../proxy/ip_list.txt'
        ip_list = []
        with open(ip_list_file_path, 'r', encoding="utf-8") as f:
            line = f.readline()
            while line:
                ip_list.append(line)
                line = f.readline()
        return ip_list

    @staticmethod
    def _set_random_test_url():
        """
        随机生成测试url
        :return:
        """
        test_url_list = ['https://www.baidu.com/', 'https://www.sogou.com/', 'http://soso.com/', 'https://www.so.com/']
        rand = random.randint(0, len(test_url_list) - 1)
        rand_url = test_url_list[rand]
        return rand_url

    def _set_random_ip(self):
        """
        设置随机ip, 并检查可用性
        :return:
        """
        ip_flag = False
        ip_list = self._read_ip_list()
        ip_len = len(ip_list)
        while not ip_flag:
            rand = random.randint(0, ip_len - 1)
            rand_ip = ip_list[rand]
            if 'https' in rand_ip:
                check_ip_proxies = {'https': rand_ip.strip('\n')}
            else:
                check_ip_proxies = {'http': rand_ip.strip('\n')}
            self.book_spider_log.info('检查ip' + str(check_ip_proxies) + '可行性...')
            try:
                # rand_url = self._set_random_test_url()
                rand_url = "https://book.douban.com/tag/"
                check_ip_response = requests.get(rand_url, proxies=check_ip_proxies, headers=self.headers, timeout=self.timeout)
                check_ip_status = check_ip_response.status_code
                if check_ip_status == 200:
                    self.proxies.clear()
                    self.proxies['https'] = rand_ip.strip('\n')
                    self.book_spider_log.info('当前ip' + str(check_ip_proxies) + '可行')
                    self.book_spider_log.info('当前ip设置为' + str(self.proxies))
                    ip_flag = True
                else:
                    self.book_spider_log.info('当前ip' + str(check_ip_proxies) + '不可行, 尝试其他中...')
            except Exception as err:
                self.book_spider_log.error('当前ip' + str(check_ip_proxies) + '不可行, 尝试其他中...' + str(err))

                
    def get_book_tags(self):
        """
        得到所有书籍标签
        :return:
        """
        self.book_spider_log.info('尝试获取书籍标签信息中...')
        try:
            self._set_random_ua()
            self._set_random_ip()
            self._set_random_sleep_time()
            time.sleep(self.sleep_time)
            tags_url = 'https://book.douban.com/tag/?view=type'
            tags_response = requests.get(tags_url, headers=self.headers, proxies=self.proxies, timeout=self.timeout)
            tags_html = tags_response.text
            # parse html
            tags_html_element = etree.HTML(tags_html)
            tags_list = tags_html_element.xpath('//table[@class="tagCol"]//td/a/text()')
            self.book_spider_log.info('获取书籍标签信息成功, 内容为' + str(tags_list))
            return tags_list
        except Exception as err:
            self.book_spider_log.error('获取书籍标签信息失败' + str(err))

    def _is_parse_book_id(self, book_id):
        """
        判断是否已经爬取过该id
        :return:
        """
        try:
            if self.redis_con.hexists('already_parse_book', book_id):
                self.book_spider_log.info('已经解析过' + str(book_id) + '书籍')
                return True
            else:
                self.redis_con.hset('already_parse_book', book_id, 1)
                self.book_spider_log.info('没有解析过' + str(book_id) + '书籍, 等待解析')
                return False
        except Exception as err:
            return False

    def get_book_id(self, book_tag='小说', start=0):
        """
        获取当前页面的书籍ID
        :param book_tag:
        :param start:
        :return:
        """
        self.book_spider_log.info('尝试获取' + str(book_tag) + 'tag, 第' + str(start) + '个书籍ID...')
        try:
            self._set_random_ua()
            self._set_random_ip()
            self._set_random_sleep_time()
            time.sleep(self.sleep_time)
            book_tag_url = 'https://book.douban.com/tag/' + str(book_tag) + '?start=' + str(start) + '&type=T'
            book_tag_page_response = requests.get(book_tag_url, headers=self.headers, proxies=self.proxies, timeout=self.timeout)
            book_tag_page_html = book_tag_page_response.text
            if '没有找到符合条件的图书' in book_tag_page_html:
                self.book_spider_log.info('获取' + str(book_tag) + 'tag, 没有找到符合条件的图书')
                return None
            else:
                book_id_list = []
                book_tag_page_html_element = etree.HTML(book_tag_page_html)
                book_subject_list = book_tag_page_html_element.xpath('//div[@class="pic"]/a[@class="nbg"]/@href')
                for book in book_subject_list:
                    book_id = re.match(r"https://.*?subject/(.*?)/", book).group(1).strip()
                    if self._is_parse_book_id(book_id):
                        continue
                    else:
                        book_id_list.append(book_id)
                self.book_spider_log.info(
                    '获取' + str(book_tag) + 'tag, 第' + str(start) + '个书籍ID成功, 长度为' + str(len(book_id_list)))
                return book_id_list
        except Exception as err:
            self.book_spider_log.info('获取' + str(book_tag) + 'tag, 第' + str(start) + '个书籍ID失败' + str(err))
            return None

    def _add_wait_author(self, person_href):
        """
        加入待抓取作者队列
        :param user_token:
        :return:
        """
        try:
            if not self.redis_con.hexists('already_get_author', person_href):
                self.redis_con.hset('already_get_author', person_href, 1)
                self.redis_con.lpush('author_queue', person_href)
                self.book_spider_log.info('添加作者' + str(person_href) + '到待爬取队列成功')
        except Exception as err:
            self.book_spider_log.error('添加作者到待爬取队列失败' + str(err))

    def get_book_info(self, book_id):
        """
        获取当前书籍信息
        :return:
        """
        self.book_spider_log.info('开始获取书籍' + str(book_id) + '信息...')
        try:
            self._set_random_ua()
            self._set_random_ip()
            self._set_random_sleep_time()
            time.sleep(self.sleep_time)

            book_info_url = 'https://book.douban.com/subject/' + str(book_id)
            book_info_response = requests.get(book_info_url, headers=self.headers, proxies=self.proxies, timeout=self.timeout)
            book_info_html = book_info_response.text
            book_page_parse = BookPageParse(book_id, book_info_html)
            book_info_json = book_page_parse.parse()
            self.book_spider_log.info('获取书籍' + str(book_id) + '信息成功')
            # self.book_spider_log.info('书籍' + str(book_id) + '信息为' + str(book_info_json))

            # 将作者ID加入到redis之中
            self.book_spider_log.info('添加作者信息到redis之中...')
            key_value = ['author', 'translator']
            for key in key_value:
                for person in book_info_json[key]:
                    if person['href']:
                        self._add_wait_author(person['href'])

            # 将电影信息保存到文件之中
            self.book_spider_log.info('保存书籍' + str(book_id) + '信息到文件之中...')
            book_info_file_path = '../data/book_info.txt'
            with open(book_info_file_path, 'a+', encoding='utf-8') as f:
                f.write(json.dumps(book_info_json, ensure_ascii=False) + '\n')
        except Exception as err:
            self.book_spider_log.error('获取书籍' + str(book_id) + '信息失败' + str(err))

    def get_person_info(self, person_id):
        """
        得到作者信息
        :return:
        """
        self.book_spider_log.info('开始获取作者' + str(person_id) + '信息...')
        try:
            self._set_random_ua()
            self._set_random_ip()
            self._set_random_sleep_time()
            time.sleep(self.sleep_time)
            person_url = 'https://book.douban.com/author/' + str(person_id)
            person_info_html = requests.get(person_url, headers=self.headers, proxies=self.proxies,
                                            timeout=self.timeout).text
            person_page_parse = PersonPageParse(person_id, person_info_html)
            person_info_json = person_page_parse.parse()
            self.book_spider_log.info('获取作者' + str(person_id) + '信息成功')
            # self.book_spider_log.info('作者' + str(person_id) + '信息为' + str(person_info_json))

            # 将作者信息保存到文件之中
            self.book_spider_log.info('保存作者' + str(person_id) + '信息到文件之中')
            person_info_file_path = '../data/book_person_info.txt'
            with open(person_info_file_path, 'a+', encoding='utf-8') as f:
                f.write(json.dumps(person_info_json, ensure_ascii=False) + '\n')
        except Exception as err:
            self.book_spider_log.error('获取作者' + str(person_id) + '信息失败')

    def get_all_book_info(self):
        """
        迭代爬取所有种类书籍信息和作者信息
        :return:
        """
        # 得到书籍标签信息
        book_tags = self.get_book_tags()
        for tag in book_tags:
            is_end = False
            start = 0
            while not is_end:
                # 获取书籍ID
                book_id_list = self.get_book_id(tag, start)
                if not book_id_list and start < 1000:
                    # 如果小于9800, 而且是空, 再尝试访问3次
                    for i in range(0, 3):
                        book_id_list = self.get_book_id(tag, start)
                        if book_id_list:
                            self.book_spider_log.info(
                                '重新获取' + str(tag) + 'tag, 第' + str(start) + '个书籍ID失败, 重试第' + str(i) + '次数成功')
                            break
                        else:
                            self.book_spider_log.info(
                                '重新获取' + str(tag) + 'tag, 第' + str(start) + '个书籍ID失败, 重试第' + str(i) + '次数失败')
                        time.sleep(10)
                    if not book_id_list:
                        start += 20
                        continue
                elif not book_id_list:
                    break

                # 多线程获取书籍Info
                movie_pool = ThreadPool(12)
                movie_pool.map(self.get_book_info, book_id_list)
                movie_pool.close()
                movie_pool.join()

                # 多线程获取电影作者信息
                person_id_list = []
                while self.redis_con.llen('author_queue'):
                    # 出队列获取作者ID
                    person_id_list.append(str(self.redis_con.rpop('author_queue').decode('utf-8')))
                author_poll = ThreadPool(12)
                author_poll.map(self.get_person_info, person_id_list)
                author_poll.close()
                author_poll.join()

                # 进行下一轮迭代
                start += 20

    def run(self):
        """
        获取书籍信息和书籍作者信息
        :return:
        """
        # 获取书籍信息
        self.get_all_book_info()


if __name__ == '__main__':
    dou_ban_book_spider = DouBanBookSpider()
    dou_ban_book_spider.run()
