# -*- coding:utf-8 -*-

from scrapy import Request, Selector
from .core.base import BaseSpider, BaseParser
from .core.errors import DataOut, DuplicateData, NoMorePagesException


class UniqloParser(BaseParser):

    def get_goods_url(self, response=None):
        # get urls for goods pages
        super().get_goods_url(response)

    def get_sublevel(self, response=None):
        urls = response.xpath()

    def get_next_page(self, response=None):
        # return list next catalog pages, or rise Exception

        super().get_next_page(response)

    def get_sku(self, response=None):
        return super().get_sku(response)

    def get_title(self, response=None):
        return super().get_title(response)

    def get_description(self, response=None):
        return super().get_description(response)

    def get_sizes(self, response=None):
        return super().get_sizes(response)

    def get_article(self, response=None):
        return super().get_article(response)

    def get_url(self, response=None):
        return {'URL':response.url}

    def get_images(self, response=None):
        return super().get_images(response)

    def get_category(self, response=None):
        return super().get_category(response)

    def get_price(self, response=None):
        return super().get_price(response)

    def get_brand(self, response=None):
        return super().get_brand(response)

    def get_merchant(self, response=None):
        return super().get_merchant(response)


class UniqloSpider(BaseSpider, UniqloParser):

    name = "uniqlo.com"

    def __init__(self):
        pass

    def parse(self, response):
        goods_url = self.get_goods_url(response)
        for url in goods_url:
            yield Request(url=url, callback=self.parse_page)

        next_url = self.get_next_page(response)
        for url in next_url:
            yield Request(url=url, callback=self.parse)

    def parse_page(self, response):
        result = dict()
        result.update(self.get_sku(response))
        result.update(self.get_title(response))
        result.update(self.get_description(response))
        result.update(self.get_sizes(response))
        result.update(self.get_article(response))
        result.update(self.get_url(response))
        result.update(self.get_images(response))
        result.update(self.get_category(response))
        result.update(self.get_price(response))
        result.update(self.get_brand(response))
        result.update(self.get_merchant(response))
        yield result

