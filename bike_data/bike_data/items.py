# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BikeDataItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    url_addres = scrapy.Field()
    add_time = scrapy.Field()
    place = scrapy.Field()
    paid_offer = scrapy.Field()
    added_via_phone = scrapy.Field()
    description = scrapy.Field()
