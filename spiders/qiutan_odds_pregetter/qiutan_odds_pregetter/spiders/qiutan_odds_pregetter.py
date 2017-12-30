import json
import datetime
import scrapy
from scrapy.http.headers import Headers
from scrapy import Spider
from ..items import QiutanOddsPregetterItem
from scrapy_splash import SplashRequest

RENDER_HTML_URL = "http://0.0.0.0:8050/render.html"
HEADERS = {
    # 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}

class QTOddsAHSpider(Spider):
    name = "qiutan_odds_pregetter"
    allowed_domains = ["nowgoal.com"]

    start_url = "http://nba.nowgoal.com/cn/normal/1.html"
    start_urls = []

    start_urls.append(start_url)

    def start_requests(self):

        for url in self.start_urls:

            yield SplashRequest(url, self.parse, args={
                'wait': 0.5, 'html': 1, 'timeout': 1800,
            }, headers=HEADERS,
            )

    def parse(self, response):
        today = datetime.datetime.now()
        y = today.strftime('%Y')
        item = QiutanOddsPregetterItem()

        tr_list = response.xpath("//*[@id='scheTab']/tbody/tr")
        for tr in reversed(tr_list):
            if len(tr.xpath("td")) <= 1:
                row_date_string = tr.xpath("td/strong/text()").extract()[0]
                row_date_string = row_date_string.split()[0]
                row_d = datetime.datetime.strptime(row_date_string, "%Y-%m-%d")
                if row_d > today:
                    continue
                else:
                    # Skip the date row
                    break
            else:
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
                    home_cur_score = td_list[3].xpath("a/span[1]/text()").extract()[0]
                except:
                    home_cur_score = ""

                try:
                    away_cur_score = td_list[3].xpath("a/span[2]/text()").extract()[0]
                except:
                    away_cur_score = ""
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

                ## Update: Adding download time##
                download_date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

                item['GAME_TYPE'] = game_type
                item['GAME_DATE'] = game_date
                item['home_team_name'] = home_team_name
                item['home_current_score'] = home_cur_score
                item['away_team_name'] = away_team_name
                item['away_current_score'] = away_cur_score
                item['handicap'] = handicap
                item['O_and_U'] = o_u
                item['DOWNLOAD_DATE'] = download_date_time
                yield item