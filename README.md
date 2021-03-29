### 1. 数据说明

+ **书籍信息**包括书籍id、图片链接、姓名、子标题、原作名称、作者、译者、出版社、出版年份、页数、价格、内容简介、~~目录简介~~、评分、评分人数。

+ **书籍作者信息**包括作者id，姓名、图片链接、性别、出生日期、国家、更多中文名、更多外文名、简介，作者包括书籍作者和译者。

### 2. 配制环境

+ 系统环境：win10

+ python环境：python3.6

+ python依赖包：requests, bs4, lxml, redis, yaml, multiprocessing

### 3. 爬虫思路

1. 请求<https://book.douban.com/tag/?view=type&icn=index-sorttags-all>界面，利用BeautifulSoup获取图书所有标签。

2. 请求<https://book.douban.com/tag/小说?start=0&type=T>，利用BeautifulSoup获取20个书籍ID。如果为空，则更换书籍标签tag。

3. 对返回的20个书籍id存放到redis已爬取队列之中，返回去重后的书籍id list。

4. 多线程爬取书籍id list之中的书籍信息。

5. 获取书籍作者id，存放到redis已爬取队列之中，返回去重后的作者id list。

6. 多线程爬取演员id list之中的作者信息。

7. start加20循环2-7步骤。

### 4. 使用教程

```shell
├── book
│   ├── __init__.py
│   ├── book_crawl.py
│   ├── book_page_parse.py
│   ├── book_person_page_parse.py
│   └── book_spider_config.yaml
├── log
│   └── book_log_config.yaml
└── proxy
    ├── get_ip.py
    ├── ip_list.txt
    └── ua_list.txt
```

爬取之前，需要先启动redis server，然后再配置proxy中的get_ip。爬取过程中为了省事，我用的是收费的ip代理池，每三分钟请求10个ip。如果你要使用的话，可以找一些免费的ip代理工具，成功之后，将有效ip写入到ip_list之中即可。方便一点的话，可以直接购买ip代理池，同样成功后将ip写入到ip_list即可。

book_spider_config用于配制一些爬虫信息，比如超时时间和redis信息。

book_log_config.yaml用于配制log信息，比如log地址和写文件格式信息。

如果你想爬取一些电影或书籍的其他信息，比如电影评论等，可以根据需求更改book_page_parse, book_person_page_parse的代码。

最后，配置好redis和ip代理池之后，启动book_crawl即可。

