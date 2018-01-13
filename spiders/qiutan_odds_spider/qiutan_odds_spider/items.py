# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field


class QiutanOddsSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    GAME_TYPE = Field()
    GAME_DATE = Field()
    home_team_name = Field()
    home_score = Field()
    away_team_name = Field()
    away_score = Field()

    DOWNLOAD_DATE = Field()

    # Single odds
    handicap = Field()
    O_and_U = Field()

    # Multiple odds
    qiutan_game_id = Field()

    company_1_name = Field()
    company_1_init_handicap = Field()
    company_1_init_ah_home_odds = Field()
    company_1_init_ah_away_odds = Field()
    company_1_init_ou = Field()
    company_1_init_ou_home_odds = Field()
    company_1_init_ou_away_odds = Field()
    company_1_curr_handicap = Field()
    company_1_curr_ah_home_odds = Field()
    company_1_curr_ah_away_odds = Field()
    company_1_curr_ou = Field()
    company_1_curr_ou_home_odds = Field()
    company_1_curr_ou_away_odds = Field()

    company_2_name = Field()
    company_2_init_handicap = Field()
    company_2_init_ah_home_odds = Field()
    company_2_init_ah_away_odds = Field()
    company_2_init_ou = Field()
    company_2_init_ou_home_odds = Field()
    company_2_init_ou_away_odds = Field()
    company_2_curr_handicap = Field()
    company_2_curr_ah_home_odds = Field()
    company_2_curr_ah_away_odds = Field()
    company_2_curr_ou = Field()
    company_2_curr_ou_home_odds = Field()
    company_2_curr_ou_away_odds = Field()

    company_3_name = Field()
    company_3_init_handicap = Field()
    company_3_init_ah_home_odds = Field()
    company_3_init_ah_away_odds = Field()
    company_3_init_ou = Field()
    company_3_init_ou_home_odds = Field()
    company_3_init_ou_away_odds = Field()
    company_3_curr_handicap = Field()
    company_3_curr_ah_home_odds = Field()
    company_3_curr_ah_away_odds = Field()
    company_3_curr_ou = Field()
    company_3_curr_ou_home_odds = Field()
    company_3_curr_ou_away_odds = Field()

    company_4_name = Field()
    company_4_init_handicap = Field()
    company_4_init_ah_home_odds = Field()
    company_4_init_ah_away_odds = Field()
    company_4_init_ou = Field()
    company_4_init_ou_home_odds = Field()
    company_4_init_ou_away_odds = Field()
    company_4_curr_handicap = Field()
    company_4_curr_ah_home_odds = Field()
    company_4_curr_ah_away_odds = Field()
    company_4_curr_ou = Field()
    company_4_curr_ou_home_odds = Field()
    company_4_curr_ou_away_odds = Field()

    company_5_name = Field()
    company_5_init_handicap = Field()
    company_5_init_ah_home_odds = Field()
    company_5_init_ah_away_odds = Field()
    company_5_init_ou = Field()
    company_5_init_ou_home_odds = Field()
    company_5_init_ou_away_odds = Field()
    company_5_curr_handicap = Field()
    company_5_curr_ah_home_odds = Field()
    company_5_curr_ah_away_odds = Field()
    company_5_curr_ou = Field()
    company_5_curr_ou_home_odds = Field()
    company_5_curr_ou_away_odds = Field()


