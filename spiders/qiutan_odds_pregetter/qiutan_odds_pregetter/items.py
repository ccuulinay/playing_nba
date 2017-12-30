# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field



class QiutanOddsPregetterItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    GAME_TYPE = Field()
    GAME_DATE = Field()
    home_team_name = Field()
    home_current_score = Field()
    away_team_name = Field()
    away_current_score = Field()
    handicap = Field()
    O_and_U = Field()
    DOWNLOAD_DATE = Field()
