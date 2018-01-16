# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field


class QiutanRunOddsSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    qiutan_game_id = Field()
    GAME_DATE = Field()
    offer_company_name = Field()
    game_run_time = Field()
    home_team_name = Field()
    home_curr_score = Field()
    away_team_name = Field()
    away_curr_score = Field()
    curr_ah_home_odds = Field()
    curr_handicap = Field()
    curr_ah_away_odds = Field()
    odds_status = Field()
    DOWNLOAD_DATE = Field()
