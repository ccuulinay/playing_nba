'''
This asian handicap getter (spider) for historical matches.
'''

import json
import datetime
import scrapy
from scrapy.http.headers import Headers
from scrapy import Spider
from ..items import NbaOddsAhSpiderItem
from scrapy_splash import SplashRequest

RENDER_HTML_URL = "http://0.0.0.0:8050/render.html"

class NbaOddsAHSpider(Spider):
    name = "nba_odds_ah_spider"
    allowed_domains = ["oddsportal.com"]

    start_urls = []
    # start_url ="http://www.oddsportal.com/basketball/usa/nba-2015-2016/results/#/page/"

    start_url ="http://www.oddsportal.com/basketball/usa/nba/results/#/page/"
    # number_pages = 30
    number_pages = 19

    # start_urls.append(start_url)
    for x in range(1, number_pages):
        start_urls.append(start_url + str(x))

    def start_requests(self):
        for url in self.start_urls:
            body = json.dumps({"url": url, "wait": 5})
            headers = Headers({'Content-Type': 'application/json',
                               #'Content-Type': 'text/javascript; charset=UTF-8',
                               #"Host":"www.oddsportal.com",
                               #"Referer":"http://www.oddsportal.com/basketball/usa/nba-2015-2016/results/",
                               "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36"
                               })

            yield SplashRequest(url, self.parse, args={
                'wait': 0.5, 'html': 1, 'timeout': 1800,
            }, headers=headers,
            )

    def parse(self, response):
        # print response.body
        base_url = "http://www.oddsportal.com"
        headers = Headers({'Content-Type': 'application/json',
                               "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36"
                               })

        games = response.xpath("//tr[contains(@class, 'deactivate')]")
        for game in games:

            child_url = base_url + game.xpath("td[contains(@class,'table-participant')]/a/@href").extract()[0] + "#ah;1"

            # print(child_url)

            yield SplashRequest(child_url, self.parse_ah_page, args={
                'wait': 0.5, 'html': 1, 'timeout': 1800,
            }, headers=headers,
            )

    def parse_ah_page(self, response):
        item = NbaOddsAhSpiderItem()

        matchup = response.xpath("//*[@id='col-content']/h1/text()").extract()[0]
        matchup_arr = matchup.strip().split('-')
        item["home_team"] = matchup_arr[0].strip()
        item["away_team"] = matchup_arr[1].strip()

        score = response.xpath("//*[@id='event-status']/p/strong/text()").extract()[0]
        tmp = score.split()
        if len(tmp) > 1:
            item["overtime"] = True
        else :
            item["overtime"] = False
        scores = map(int, tmp[0].split(":"))
        item["score_home"] = scores[0]
        item["score_away"] = scores[1]

        date_n_time = response.xpath("//*[@id='col-content']/p[1]/text()").extract()[0]
        tmp = date_n_time.split(',')
        date_time = datetime.datetime.strptime(tmp[1].strip() + " " + tmp[2].strip(), "%d %b  %Y %H:%M")
        date_time += datetime.timedelta(0,0,0,0,0,2) # datetime.timedelta([days[, seconds[, microseconds[, milliseconds[, minutes[, hours[, weeks]]]]]]])
        item["date_time"] = date_time

        ah_odds = response.xpath("//*[contains(@class, 'table-header-light')]")
        ah_odds_list = []
        for ah_odd in ah_odds:
            # print (ah_odd)
            odds_number_temp = ah_odd.xpath("strong/a/text()").extract()[0]
            odds_number = float(odds_number_temp.split()[-1])
            odds_cnt_temp = ah_odd.xpath("span[contains(@class,'odds-cnt')]/text()").extract()[0]
            print odds_cnt_temp
            odds_cnt = int(odds_cnt_temp[1:-1])
            # odds_cnt = 0
            odds_home = 0
            odds_away = 0
            if odds_cnt > 0:
                odds = ah_odd.xpath("span[contains(@class,'chunk-odd')]/a/text()").extract()
                if len(odds) > 1:
                    odds_home = odds[1]
                    odds_away = odds[0]
            ah_odds_list.append((odds_number, odds_cnt, odds_home, odds_away))
            print (odds_number, odds_cnt, odds_home, odds_away)

        ah_odds_list = sorted(ah_odds_list, reverse=True, key=lambda a: a[1])

        # print (ah_odds_list[:4])
        ah_odds_list = ah_odds_list[:4]
        index = 1
        for i in ah_odds_list:

            ah = "ah_" + str(index)
            cnt = "odd_cnt_" + str(index)
            odd_home = "odd_home_" + str(index)
            odd_away = "odd_away_" + str(index)
            item[ah] = i[0]
            item[cnt] = i[1]
            item[odd_home] = i[2]
            item[odd_away] = i[3]

            index += 1

        yield item

