# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field


class NbaOddsAhPregetterItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    date_time = Field()
    home_team = Field()
    away_team = Field()
    ah_1 = Field()
    odd_cnt_1 = Field()
    odd_home_1 = Field()
    odd_away_1 = Field()
    download_date_time = Field()

