import json
import datetime
from datetime import timedelta, timezone
import scrapy
from scrapy.http.headers import Headers
from scrapy import Spider
from ..items import QiutanOddsSpiderItem
from scrapy_splash import SplashRequest

RENDER_HTML_URL = "http://0.0.0.0:8050/render.html"
HEADERS = {
    # 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}
base_url = "http://nba.nowgoal.com/cn/Normal/"


class QTOddsAHSpider(Spider):
    name = "qiutan_odds_spider"
    allowed_domains = ["nowgoal.com"]

    start_urls = []
    # start_year = 2005
    start_year = 2017
    # end_year = 2017
    end_year = 2018

    # If you would like to query from exactly date range, set below to True and set start_year and end_year above to
    # corresponding years
    # If set to False, will scratch thw whole year's games.
    day_query_flag = True
    # day_query_flag = False
    start_date_string = "2018-01-01"
    end_date_string = "2018-01-14"
    # start_date_obj = datetime.datetime.strptime(start_date_string, "%Y-%m-%d")
    # end_date_obj = datetime.datetime.strptime(end_date_string, "%Y-%m-%d")
    start_date_obj = datetime.datetime.strptime(start_date_string, "%Y-%m-%d").astimezone(timezone(timedelta(hours=-8)))
    end_date_obj = datetime.datetime.strptime(end_date_string, "%Y-%m-%d").astimezone(timezone(timedelta(hours=-8)))

    for x in range(start_year, end_year):
        season_full_string = str(x) + "-" + str(x+1)
        target_url = base_url + season_full_string + "/1.html"
        start_urls.append(target_url)

    def start_requests(self):

        for url in self.start_urls:

            yield SplashRequest(url, self.parse, args={
                'wait': 0.5, 'html': 1, 'timeout': 1800,
            }, headers=HEADERS,
            )

    def parse(self, response):
        child_urls = []
        child_base_url = "http://nba.nowgoal.com/cn/Normal.html?"
        child_base_url_trail = "&SclassID=1"

        year_month_list = response.xpath("//*[@id='yearmonthTable2']/tbody/tr/td//text()").extract()
        y_list = []
        date_param_list = []
        for t_str in year_month_list:
            if int(t_str) > 12:
                y = str(t_str)
                y_list.append(y)
                continue
            else:
                m = str(t_str)
            if y and m:
                param_str = "y=" + y + "&m=" + m
                date_param_list.append(param_str)
        matchSeason = "-".join(y_list)

        for date_param in date_param_list:
            url = child_base_url + date_param + "&matchSeason=" + matchSeason + child_base_url_trail
            child_urls.append(url)

            yield SplashRequest(url, self.parse_odds_page, args={
                    'wait': 0.5, 'html': 1, 'timeout': 3600,
                }, headers=HEADERS,
                meta={'date_param': date_param}
            )

    def parse_odds_page(self, response):
        today = datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
        item = QiutanOddsSpiderItem()

        date_param = response.meta['date_param']
        y = date_param.split("&")[0].split("=")[1]

        item['GAME_TYPE'] = "Regular"

        tr_list = response.xpath("//*[@id='scheTab']/tbody/tr")
        # First row would be column names
        tr_list = tr_list[1:]
        if not self.day_query_flag:
            for tr in tr_list:
                if len(tr.xpath("td")) <= 1:
                    row_date_string = tr.xpath("td/strong/text()").extract()[0]
                    row_date_string = row_date_string.split()[0]
                    row_d = datetime.datetime.strptime(row_date_string, "%Y-%m-%d")
                    if row_d.date() > today.date():
                        break
                    else:
                        # Skip the date row
                        continue

                else:
                    odds_list_url_list = []
                    td_list = tr.xpath("td")

                    try:
                        game_type = td_list[0].xpath("text()").extract()[0]
                    except:
                        game_type = ""

                    try:
                        game_date = y + "-" + " ".join(td_list[1].xpath("text()").extract())
                    except:
                        game_date = ""

                    try:
                        home_team_name = td_list[2].xpath("a/text()").extract()[0]
                    except:
                        home_team_name = ""
                    try:
                        home_score = td_list[3].xpath("a/span[1]/text()").extract()[0]
                    except:
                        home_score = ""

                    try:
                        away_score = td_list[3].xpath("a/span[2]/text()").extract()[0]
                    except:
                        away_score = ""
                    try:
                        away_team_name = td_list[4].xpath("a/text()").extract()[0]
                    except:
                        away_team_name = ""
                    try:
                        handicap = td_list[5].xpath("text()").extract()[0]
                    except:
                        handicap = ""
                    try:
                        o_u = td_list[6].xpath("text()").extract()[0]
                    except:
                        o_u = ""

                    try:
                        odds_list_url = td_list[7].xpath("a[1]/@href").extract()[0]
                        odds_list_url_list.append(odds_list_url)
                        qiutan_game_id =  odds_list_url.split('/')[-1].split('.')[0]
                        # print(qiutan_game_id)
                    except:
                        odds_list_url = ""
                        qiutan_game_id = ""

                    ## Update: Adding download time##
                    download_date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

                    meta_item = dict()
                    meta_item['GAME_TYPE'] = game_type
                    meta_item['GAME_DATE'] = game_date
                    meta_item['home_team_name'] = home_team_name
                    meta_item['home_score'] = home_score
                    meta_item['away_team_name'] = away_team_name
                    meta_item['away_score'] = away_score
                    meta_item['handicap'] = handicap
                    meta_item['O_and_U'] = o_u
                    meta_item['DOWNLOAD_DATE'] = download_date_time
                    meta_item['qiutan_game_id'] = qiutan_game_id

                    if odds_list_url:
                        yield SplashRequest(odds_list_url, self.parse_odds_list_page, args={
                                'wait': 0.5, 'html': 1, 'timeout': 3600,
                            }, headers=HEADERS,
                            meta={'meta_item': meta_item}
                        )
                    """
                    item['GAME_TYPE'] = game_type
                    item['GAME_DATE'] = game_date
                    item['home_team_name'] = home_team_name
                    item['home_score'] = home_score
                    item['away_team_name'] = away_team_name
                    item['away_score'] = away_score
                    item['handicap'] = handicap
                    item['O_and_U'] = o_u
                    item['DOWNLOAD_DATE'] = download_date_time
                    yield item
                    """
        else:
            spider_flag = False
            for tr in tr_list:
                if len(tr.xpath("td")) <= 1:
                    row_date_string = tr.xpath("td/strong/text()").extract()[0]
                    row_date_string = row_date_string.split()[0]
                    row_d = datetime.datetime.strptime(row_date_string, "%Y-%m-%d")
                    if self.start_date_obj.date() <= row_d.date() <= self.end_date_obj.date():
                        spider_flag = True
                        continue

                    elif row_d.date() > self.end_date_obj.date():
                        break
                    elif row_d.date() > (today + datetime.timedelta(days=1)).date():
                        # Skip the date row
                        break
                    else:
                        continue
                else:
                    if spider_flag:
                        odds_list_url_list = []
                        td_list = tr.xpath("td")

                        try:
                            game_type = td_list[0].xpath("text()").extract()[0]
                        except:
                            game_type = ""

                        try:
                            game_date = y + "-" + " ".join(td_list[1].xpath("text()").extract())
                        except:
                            game_date = ""

                        try:
                            home_team_name = td_list[2].xpath("a/text()").extract()[0]
                        except:
                            home_team_name = ""
                        try:
                            home_score = td_list[3].xpath("a/span[1]/text()").extract()[0]
                        except:
                            home_score = ""

                        try:
                            away_score = td_list[3].xpath("a/span[2]/text()").extract()[0]
                        except:
                            away_score = ""
                        try:
                            away_team_name = td_list[4].xpath("a/text()").extract()[0]
                        except:
                            away_team_name = ""
                        try:
                            handicap = td_list[5].xpath("text()").extract()[0]
                        except:
                            handicap = ""
                        try:
                            o_u = td_list[6].xpath("text()").extract()[0]
                        except:
                            o_u = ""


                        try:
                            odds_list_url = td_list[7].xpath("a[1]/@href").extract()[0]
                            odds_list_url_list.append(odds_list_url)
                            qiutan_game_id =  odds_list_url.split('/')[-1].split('.')[0]
                            # print(qiutan_game_id)
                        except:
                            odds_list_url = ""
                            qiutan_game_id = ""


                        ## Update: Adding download time##
                        download_date_time = datetime.datetime.utcnow().replace(tzinfo=timezone.utc).strftime('%Y-%m-%d %H:%M')

                        meta_item = dict()
                        meta_item['GAME_TYPE'] = game_type
                        meta_item['GAME_DATE'] = game_date
                        meta_item['home_team_name'] = home_team_name
                        meta_item['home_score'] = home_score
                        meta_item['away_team_name'] = away_team_name
                        meta_item['away_score'] = away_score
                        meta_item['handicap'] = handicap
                        meta_item['O_and_U'] = o_u
                        meta_item['DOWNLOAD_DATE'] = download_date_time
                        meta_item['qiutan_game_id'] = qiutan_game_id

                        if odds_list_url:
                            yield SplashRequest(odds_list_url, self.parse_odds_list_page, args={
                                    'wait': 0.5, 'html': 1, 'timeout': 3600,
                                }, headers=HEADERS,
                                meta={'meta_item': meta_item}
                            )
                        """
                        item['GAME_TYPE'] = game_type
                        item['GAME_DATE'] = game_date
                        item['home_team_name'] = home_team_name
                        item['home_score'] = home_score
                        item['away_team_name'] = away_team_name
                        item['away_score'] = away_score
                        item['handicap'] = handicap
                        item['O_and_U'] = o_u
                        item['DOWNLOAD_DATE'] = download_date_time
                        yield item
                        """

    def parse_odds_list_page(self, response):
        item = QiutanOddsSpiderItem()
        meta_item = response.meta['meta_item']

        tr_list = response.xpath("//*[@id='main']/table/tbody/tr[2]/td[1]/table[1]/tbody/tr[contains(@class,'te')]")
        if len(tr_list) > 5:
            tr_list = tr_list[:5]
        for i, tr in enumerate(tr_list):
            td_list = tr.xpath("td")

            try:
                company_name = td_list[0].xpath("text()").extract()[0]
            except:
                company_name = ""

            try:
                company_init_ah_home_odds = td_list[1].xpath("text()").extract()[0]
            except:
                company_init_ah_home_odds = ""
            try:
                company_curr_ah_home_odds = td_list[1].xpath("span/text()").extract()[0]
            except:
                company_curr_ah_home_odds = ""

            try:
                company_init_handicap = td_list[2].xpath("text()").extract()[0]
            except:
                company_init_handicap = ""
            try:
                company_curr_handicap = td_list[2].xpath("span/text()").extract()[0]
            except:
                company_curr_handicap = ""

            try:
                company_init_ah_away_odds = td_list[3].xpath("text()").extract()[0]
            except:
                company_init_ah_away_odds = ""
            try:
                company_curr_ah_away_odds = td_list[3].xpath("span/text()").extract()[0]
            except:
                company_curr_ah_away_odds = ""

            try:
                company_init_ou_home_odds = td_list[4].xpath("text()").extract()[0]
            except:
                company_init_ou_home_odds = ""
            try:
                company_curr_ou_home_odds = td_list[4].xpath("span/text()").extract()[0]
            except:
                company_curr_ou_home_odds = ""

            try:
                company_init_ou = td_list[5].xpath("text()").extract()[0]
            except:
                company_init_ou = ""
            try:
                company_curr_ou = td_list[5].xpath("span/text()").extract()[0]
            except:
                company_curr_ou = ""

            try:
                company_init_ou_away_odds = td_list[6].xpath("text()").extract()[0]
            except:
                company_init_ou_away_odds = ""
            try:
                company_curr_ou_away_odds = td_list[6].xpath("span/text()").extract()[0]
            except:
                company_curr_ou_away_odds = ""

            item['company_'+str(i+1)+'_name'] = company_name
            item['company_'+str(i+1)+'_init_handicap'] = company_init_handicap
            item['company_'+str(i+1)+'_init_ah_home_odds'] = company_init_ah_home_odds
            item['company_'+str(i+1)+'_init_ah_away_odds'] = company_init_ah_away_odds
            item['company_'+str(i+1)+'_init_ou'] = company_init_ou
            item['company_'+str(i+1)+'_init_ou_home_odds'] = company_init_ou_home_odds
            item['company_'+str(i+1)+'_init_ou_away_odds'] = company_init_ou_away_odds
            item['company_'+str(i+1)+'_curr_handicap'] = company_curr_handicap
            item['company_'+str(i+1)+'_curr_ah_home_odds'] = company_curr_ah_home_odds
            item['company_'+str(i+1)+'_curr_ah_away_odds'] = company_curr_ah_away_odds
            item['company_'+str(i+1)+'_curr_ou'] = company_curr_ou
            item['company_'+str(i+1)+'_curr_ou_home_odds'] = company_curr_ou_home_odds
            item['company_'+str(i+1)+'_curr_ou_away_odds'] = company_curr_ou_away_odds

        item['GAME_TYPE'] = meta_item['GAME_TYPE']
        item['GAME_DATE'] = meta_item['GAME_DATE']
        item['home_team_name'] = meta_item['home_team_name']
        item['home_score'] = meta_item['home_score']
        item['away_team_name'] = meta_item['away_team_name']
        item['away_score'] = meta_item['away_score']
        item['DOWNLOAD_DATE'] = meta_item['DOWNLOAD_DATE']
        item['handicap'] = meta_item['handicap']
        item['O_and_U'] = meta_item['O_and_U']
        item['qiutan_game_id'] = meta_item['qiutan_game_id']

        yield item



