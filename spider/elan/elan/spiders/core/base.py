# -*- coding:utf-8 -*-

from scrapy import Spider

MODE_UPDATE = 1 # update for scraped data
MODE_NEW = 2 # scrap new data
MODE_FULL = 4 # get all goods in section

MODE = (MODE_UPDATE, MODE_NEW, MODE_FULL)


class BaseParser(object):


    def get_goods_url(self, response = None):
        pass

    def get_next_page(self, response = None):
        pass

    def get_sku(self, response = None):
        return {"SKU": ''}

    def get_title(self, response = None):
        return {"TITLE": ""}

    def get_description(self, response = None):
        return {"DESCRIPTION": None}

    def get_sizes(self, response = None):
        return {'SIZES': []}

    def get_article(self, response = None):
        return {"ARTICLE": None}

    def get_url(self, response = None):
        return {"URL": ""}

    def get_images(self, response = None):
        return {"IMAGES": []}

    def get_category(self, response = None):
        return {"CATEGORY": []}

    def get_price(self, response = None):
        return {"PRICE": {"ORIGIN": 0.0, "DISCOUNT": 0.0, "SPECIAL": 0.0}}

    def get_brand(self, response = None):
        return {"BRAND": ""}

    def get_merchant(self, response = None):
        return {"MERCHANT": ""}




class BaseSpider(Spider):

    name = 'base'

    def __init__(self, section = None, mode=MODE_FULL):
        self._mode = mode
        self.requested_url = set()
        self.visited_url = set()

    def start_requests(self):
        pass

    def parse(self, response):
        result = dict()

    def _get_goods(self, ):
        pass


