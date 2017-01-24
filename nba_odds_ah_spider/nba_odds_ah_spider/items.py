# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field


class NbaOddsAhSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    date_time = Field()
    home_team = Field()
    away_team = Field()
    score_home = Field()
    score_away = Field()
    overtime = Field()
    ah_1 = Field()
    odd_cnt_1 = Field()
    odd_home_1 = Field()
    odd_away_1 = Field()
    ah_2 = Field()
    odd_cnt_2 = Field()
    odd_home_2 = Field()
    odd_away_2 = Field()
    ah_3 = Field()
    odd_cnt_3 = Field()
    odd_home_3 = Field()
    odd_away_3 = Field()
    ah_4 = Field()
    odd_cnt_4 = Field()
    odd_home_4 = Field()
    odd_away_4 = Field()


