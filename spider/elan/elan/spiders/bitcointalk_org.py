# -*- coding:utf-8 -*-


from scrapy import Request, Selector
from scrapy import Spider
import re

iscontain = lambda t, p: len(list(filter(lambda x: x in t, p))) > 0
remove_tags = lambda t: re.sub(r'\<[^>]*\>', '', str(t))


class BitcoinTalkParser(object):

    def get_topic_pagination(self, response):
        l = list(set(response.xpath("//*[@class='navPages']/@href").getall()))
        return l

    def get_topic_description_list(self, response):
        """
        Получаем список топиков со страницы
        :param response:
        :return:
        """
        s = list(map(lambda x: Selector(text=x), response.xpath("//table//tr").getall()))
        section = self.get_section(response)
        l = list(map(lambda x: {'url': x.xpath("//td//*[contains(@id, 'msg_')]//@href").get(),
                                'title': " ".join(x.xpath("//td//*[contains(@id, 'msg_')]//text()").getall()),
                                'author_nick': x.xpath("//td//a[@title]/text()").get(),
                                'author_profile': x.xpath("//td//a[@title]/@href").get(),
                                'posts': x.xpath(
                                    "normalize-space((//td[contains(@class, 'windowbg')])[5]/text())").get(),
                                'views': x.xpath(
                                    "normalize-space((//td[contains(@class, 'windowbg')])[6]/text())").get(),
                                'date': x.xpath(
                                    "normalize-space(//td[contains(@class, 'lastpostcol')]/span/text())").get(),
                                'section': section,
                                "__type": 'topic'
                                }, s))
        l = list(filter(lambda x: x.get('url', None) and x.get('author_nick', None), l))
        return l

    def get_section(self, response):
        """
        Текущий раздел
        """
        section = response.xpath("//*[@class='nav']//a/text()").getall()
        section = section[:int(len(section) / 2)]
        return section

    def get_next_topic_page(self, response):
        """
        Пагинация по топикам
        """
        l = list(set(response.xpath("//tr//span[@class='prevnext']//@href").getall()))
        return l

    def get_next_posts_page(self, response):
        """
        Пагинация на следующую страницы с постами
        """
        l = response.xpath("//span[@class='prevnext']/a[contains(text(), '»')]/@href").get()
        return l

    def get_post_list(self, response):
        """
        Список постов со страницы
        """
        p = response.xpath("//tr[@class]//td[@class]//td[contains(@class, 'windowbg')]").getall()
        ex = response.xpath("//tbody//tbody//div[@class='subject']/a[contains(@href, text())]").getall()
        # remove hidden posts
        posts = list(filter(lambda x: not iscontain(x, ex), p))
        posts = list(map(lambda x: Selector(text=x), posts))
        posts = list(map(lambda x: {'user_nick': x.xpath("//td[@class='poster_info']//a[@title]/text()").get(),
                                    'user_profile': x.xpath("//td[@class='poster_info']//a[@title]/@href").get(),
                                    'post_header': x.xpath("//div[@class='subject']//a/text()").get(),
                                    'topik_link': x.xpath("//div[@class='subject']//@href").get(),
                                    'post_date': x.xpath(
                                        "//td[@class='td_headerandpost']//div[@class='subject']/following::*[@class='smalltext']/text()").get(),
                                    'post_message': x.xpath("//div[@class='post']").get(),
                                    'post_link': x.xpath("//a[@class='message_number']//@href").get(),
                                    '__type': 'post'
                                    }, posts))
        return posts


class BitcoinTalkSpider(Spider, BitcoinTalkParser):
    name = "bitcointalk.org"
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'DOWNLOAD_DELAY': .1,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1
        # 'CONCURRENT_REQUESTS': 100,
        # 'CONCURRENT_REQUESTS_PER_DOMAIN': 100,
        # # 'COOKIE_ENABLED': True,
        # 'DOWNLOAD_DELAY': .1,
        # 'AUTOTHROTTLE_TARGET_CONCURRENCY': 10,
        # # # proxy plugin params
        # 'PROXY_TOTAL_COUNT': 100,
        # 'PROXY_RANGE': 8,
        # 'PROXY_TOP_RANGE': 10,
        # 'PROXY_TYPES': 1,
        # 'PROXY_POOL_SIZE': 10,
        # 'PROXY_ACCESS': TOKEN,
        # 'DOWNLOADER_MIDDLEWARES': {
        #     'scrapyproject.extensions.proxy.SimpleProxyRotator': 50,
        #     'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        #     'scrapyproject.extensions.random_useragent.RandomUserAgent': 400,
        # },
        #
        # 'ITEM_PIPELINES': {
        #     'scrapyproject.extensions.pipelines.DropDublicate': 100,
        #     'scrapyproject.pipelines.FormatChecker': 201
        # }
    }

    def __init__(self, mode='board', entry='', **kw):
        """
        работает в 3 режимах.
        в зависимости от режима работы нужна передать ссылку на board, topic или profile
        """
        self._start_url = entry
        self._mode = mode
        self.mode_parse = {
            'board': self.parse_board,
            'topic': self.parse_topic,
            'profile': self.parse_profile
        }
        self.parse = self.mode_parse.get(self._mode, None)

    def parse(self, response):
        pass

    def start_requests(self):
        yield Request(url=self._start_url, callback=self.parse)
        pass

    def parse_board(self, response):
        topics = self.get_topic_description_list(response)
        for topic in topics:
            yield topic
            yield Request(url=topic.get('url'), callback=self.parse_topic, priority=-1)
        next_page = self.get_next_posts_page(response)
        if next_page:
            yield Request(url=next_page, callback=self.parse_board)

    def parse_topic(self, response):
        posts = self.get_post_list(response)
        for post in posts:
            yield post
            yield Request(url=post.get('user_profile'), callback=self.parse_profile, priority=5, dont_filter=False)
        next_page = self.get_next_posts_page(response)
        if next_page:
            yield Request(url=next_page, callback=self.parse_topic, priority=1)

    def parse_profile(self, response):
        user = {"__type": "user_profile", "profile_link": response.url}
        s = response.xpath("//td[@class='windowbg']//table/tr").getall()
        s = list(map(lambda x: Selector(text=x), s))
        p = list(filter(lambda y: len(y) == 2, list(map(lambda x: x.xpath("//td").getall(), s))))
        p = list(map(lambda x: (remove_tags(x[0]), remove_tags(x[1])), p))
        user.update(p)
        yield user

