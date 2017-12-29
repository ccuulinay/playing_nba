import pandas as pd
import requests
import os
from lxml import etree
import urllib
import datetime
try:
    from urllib import urlretrieve  # python 2 compatible
except:
    from urllib.request import urlretrieve  # python 3 compatible


# Fix non-browser request issue
HEADERS = {
    # 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}


def get_team_games_log(team_id=0, season='2017-18',
                                     season_type="Regular Season"):
    """

    :param team_id:
    :param season:
    :param season_type:
    :return:
    """
    base_url = "http://stats.nba.com/stats/teamgamelog?"
    url_parameters = {
                                "TeamID": str(team_id),
                                "LeagueID": "00",
                                "Season": season,
                                "SeasonType": season_type
                            }

    # get the web page
    response = requests.get(base_url, params=url_parameters,headers=HEADERS)
    response.raise_for_status()

    # The 'header' key accesses the headers
    headers = response.json()['resultSets'][0]['headers']
    # The 'rowSet' key contains the teams data along with their IDs
    teams = response.json()['resultSets'][0]['rowSet']
    # Create dataframe with proper numeric types
    df = pd.DataFrame(teams, columns=headers)
    df.GAME_DATE = pd.to_datetime(df.GAME_DATE)
    return df


def get_all_players_n_teams_ids(season='2017-18', IsOnlyCurrentSeason="0"):

    base_url = "http://stats.nba.com/stats/commonallplayers?"
    url_parameters = {
        "LeagueID": "00",
        "Season": season,
        "IsOnlyCurrentSeason" : IsOnlyCurrentSeason
    }

    # get the web page
    response = requests.get(base_url, params=url_parameters,headers=HEADERS)
    response.raise_for_status()

    # The 'header' key accesses the headers
    headers = response.json()['resultSets'][0]['headers']
    # The 'rowSet' key contains the data along with their IDs
    content = response.json()['resultSets'][0]['rowSet']
    # Create dataframe with proper numeric types
    df = pd.DataFrame(content, columns=headers)
    df = df.convert_objects(convert_numeric=True)

    t_df = pd.DataFrame({"TEAM_NAME": df.TEAM_NAME.unique(),
                        "TEAM_ID": df.TEAM_ID.unique()})

    return df, t_df


def get_player_games_log(player_id, season='2017-18',
                         begin_date="", end_date="", measureType='Base', season_type="Regular Season",
                         OpponentTeamID=0,Outcome=""):
    """

    :param player_id:
    :param season:
    :param measureType: one of 'Base', 'Advanced', 'Four+Factors', 'Misc', 'Scoring', 'Opponent', 'Defense'
    :param begin_date: MM/DD/YYYY
    :param end_date: MM/DD/YYYY
    :param season_type:
    :param OpponentTeamID:
    :param Outcome:
    :return:
    """
    base_url = "http://stats.nba.com/stats/playergamelogs?"
    url_parameters = {
        "DateFrom": begin_date,
        "DateTo": end_date,
        "GameSegment": "",
        "LastNGames": "",
        "LeagueID": str("00"),
        "Season": season,
        "SeasonType": season_type,
        "PlayerID": str(player_id),
        "MeasureType": measureType,
        "OpponentTeamID": str(OpponentTeamID),
        "Outcome":Outcome
    }
    # get the web page
    response = requests.get(base_url, params=url_parameters, headers=HEADERS)
    response.raise_for_status()

    # The 'header' key accesses the headers
    headers = response.json()['resultSets'][0]['headers']
    # The 'rowSet' key contains the teams data along with their IDs
    players = response.json()['resultSets'][0]['rowSet']
    # Create dataframe with proper numeric types
    df = pd.DataFrame(players, columns=headers)
    df.GAME_DATE = pd.to_datetime(df.GAME_DATE)
    return df


def get_league_dash_team_stats_to_df(season='2016-17', m=0, measureType='Base', begin_date="", end_date="",
                                     season_type="Regular+Season"):
    """
    :rtype : object
    :param season:
    :param measureType: one of 'Base', 'Advanced', 'Four+Factors', 'Misc', 'Scoring', 'Opponent', 'Defense'
    :param month: 0 means all, starting from 1 meaning Jan.
    :param begin_date: MM/DD/YYYY
    :param end_date: MM/DD/YYYY
    :return: dataframe
    """

    if m == 0:
        month = str(m)
    elif m == 9:
        month = str(m + 3)
    else:
        month = str((m + 3) % 12)

    url = "http://stats.nba.com/stats/leaguedashteamstats?" \
          "Conference=&DateFrom=&DateTo=&Division=&GameScope=&GameSegment=&LastNGames=0&LeagueID=00" \
          "&Location=&MeasureType=" + measureType + "&Month=" + month + "&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0" \
                                                                        "&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N" \
                                                                        "&Season=" + season + "&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=" \
                                                                                              "&StarterBench=&TeamID=0&VsConference=&VsDivision="

    regular_url = "http://stats.nba.com/stats/leaguedashteamstats?" \
                  "DateFrom=" + begin_date + "&DateTo=" + end_date + \
                  "&Conference=&Division=&GameScope=&GameSegment=&LastNGames=0&LeagueID=00" \
                  "&Location=&MeasureType=" + measureType + "&Month=" + month + "&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0" \
                                                                                "&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N" \
                                                                                "&Season=" + season + "&SeasonSegment=&SeasonType=" + season_type + "&ShotClockRange=" \
                                                                                                                                                    "&StarterBench=&TeamID=0&VsConference=&VsDivision="

    # get the web page
    response = requests.get(regular_url, headers=HEADERS)
    response.raise_for_status()

    # The 'header' key accesses the headers
    headers = response.json()['resultSets'][0]['headers']
    # The 'rowSet' key contains the teams data along with their IDs
    teams = response.json()['resultSets'][0]['rowSet']
    # Create dataframe with proper numeric types
    df = pd.DataFrame(teams, columns=headers)

    return df


def get_one_team_stats_to_df(team_id=0, season='2016-17', m=0, measureType='Base', begin_date="", end_date=""):
    """
    :param season:
    :param measureType: one of 'Base', 'Advanced', 'Four+Factors', 'Misc', 'Scoring', 'Opponent', 'Defense'
    :param month: 0 means all, starting from 1 meaning Jan.
    :param begin_date: MM/DD/YYYY
    :param end_date: MM/DD/YYYY
    :return: dataframe
    """
    if m == 0:
        month = str(m)
    elif m == 9:
        month = str(m + 3)
    else:
        month = str((m + 3) % 12)

    team_id = str(team_id)

    url = "http://stats.nba.com/stats/leaguedashteamstats?" \
          "Conference=&DateFrom=&DateTo=&Division=&GameScope=&GameSegment=&LastNGames=0&LeagueID=00" \
          "&Location=&MeasureType=" + measureType + "&Month=" + month + "&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0" \
                                                                        "&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N" \
                                                                        "&Season=" + season + "&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=" \
                                                                                              "&StarterBench=&TeamID=0&VsConference=&VsDivision="

    time_url = "http://stats.nba.com/stats/leaguedashteamstats?" \
               "DateFrom=" + begin_date + "&DateTo=" + end_date + \
               "&Conference=&Division=&GameScope=&GameSegment=&LastNGames=0&LeagueID=00" \
               "&Location=&MeasureType=" + measureType + "&Month=" + month + "&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0" \
                                                                             "&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N" \
                                                                             "&Season=" + season + "&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=" \
                                                                                                   "&StarterBench=&TeamID=" + team_id + "&VsConference=&VsDivision="

    # get the web page
    response = requests.get(time_url, headers=HEADERS)
    response.raise_for_status()

    # The 'header' key accesses the headers
    headers = response.json()['resultSets'][0]['headers']
    # The 'rowSet' key contains the teams data along with their IDs
    teams = response.json()['resultSets'][0]['rowSet']
    # Create dataframe with proper numeric types
    df = pd.DataFrame(teams, columns=headers)

    return df


def get_boxscore_list_to_df(team_id=0, season='2017-18', m=0, begin_date="", end_date="", season_type="Regular+Season"):
    """
    :rtype : object
    :param season:
    :param month: 0 means all, starting from 1 meaning Jan.
    :param begin_date: MM/DD/YYYY
    :param end_date: MM/DD/YYYY
    :return: dataframe
    """
    team_id = str(team_id)

    sample_url = "https://stats.nba.com/stats/leaguegamelog?" \
                 "Counter=1000&DateFrom=&DateTo=&Direction=DESC&LeagueID=00&PlayerOrTeam=T&Season=2016-17&SeasonType=Regular+Season&Sorter=DATE"

    time_url = "http://stats.nba.com/stats/leaguegamelog?" \
               "DateFrom=" + begin_date + "&DateTo=" + end_date + "&Direction=DESC&LeagueID=00&PlayerOrTeam=T" \
                                                                  "&Season=" + season + "&SeasonType=" + season_type + "&TeamID=" + team_id + "&Sorter=DATE"


    # get the web page
    response = requests.get(time_url, headers=HEADERS)
    response.raise_for_status()

    # The 'header' key accesses the headers
    headers = response.json()['resultSets'][0]['headers']
    # The 'rowSet' key contains the teams data along with their IDs
    teams = response.json()['resultSets'][0]['rowSet']
    # Create dataframe with proper numeric types
    df = pd.DataFrame(teams, columns=headers)

    return df


def get_one_game_play_to_play_to_df(game_id, end_period=10, end_range=55800, range_type=2,
                                    season='2017-18', season_type="Regular+Season", start_period=1, start_range=0):

    game_id = str(game_id)

    sample_url = "https://stats.nba.com/stats/playbyplayv2?" \
                 "EndPeriod=10&EndRange=55800&GameID=0021700027&RangeType=2&Season=2017-18&SeasonType=Regular+Season&StartPeriod=1&StartRange=0"

    time_url = "https://stats.nba.com/stats/playbyplayv2?" \
               "EndPeriod=" + str(end_period) + "&EndRange=" + str(end_range) + "&GameID=" + str(game_id) + \
               "&RangeType=" + str(range_type) + "&Season=" + season + "&SeasonType=" + season_type + \
               "&StartPeriod=" + str(start_period) + "&StartRange=" + str(start_range)

    # get the web page
    response = requests.get(time_url, headers=HEADERS)
    response.raise_for_status()

    # The 'header' key accesses the headers
    headers = response.json()['resultSets'][0]['headers']
    # The 'rowSet' key contains the teams data along with their IDs
    teams = response.json()['resultSets'][0]['rowSet']
    # Create dataframe with proper numeric types
    df = pd.DataFrame(teams, columns=headers)

    return df


def get_one_game_play_to_play_from_csv_to_df(game_id, filename):
    game_id = str(game_id)
    # filename = path+"pp_"+game_id+".csv"
    df = pd.read_csv(filename)
    # if os.path.isfile(filename):
    return df


def get_one_pp_to_text(df, column_list=None):
    if not column_list:
        column_list = ['PLAYER1_NAME', 'PLAYER2_NAME', 'PLAYER3_NAME', 'HOMEDESCRIPTION',
                       'NEUTRALDESCRIPTION',
                       'VISITORDESCRIPTION']
    main_feat = df[column_list].copy()
    main_text = main_feat.to_csv(index=False, header=False)
    return main_text


def get_bbr_nickname_player_of_week_list(after_2001=True):
    """

    :param after_2001:
    :return:
    """
    player_mapping_url = "https://d2cwpp38twqe55.cloudfront.net/short/inc/players_search_list.csv"
    player_mapping_csv = "data/BBR/players_search_list.csv"
    column_names = ['nickname', 'fullname','career_seasons','active_service']
    player_mapping_df = pd.read_csv(player_mapping_csv, header=None, names=column_names)

    bbr_pow_url = "https://www.basketball-reference.com/awards/pow.html"

    # get the web page
    response = requests.get(bbr_pow_url, headers=HEADERS)
    response.raise_for_status()

    root = etree.HTML(response.content)
    years_pows = root.xpath("//*[@id='div_']/div")
    # after2001_column_names = ['season', 'week', 'eastern_pow_nickname', 'western_pow_nickname']
    # before2001_column_names = ['season', 'week', '1st_pow_nickname', '2nd_pow_nickname']

    after2001_column_names = ['season', 'week', 'division', 'pow_name', 'REWARD_DATE']
    # before2001_column_names = ['season', 'week', '1st_pow_name', '2nd_pow_name', 'REWARD_DATE']

    after2001_pows_list = []
    before2001_pows_list = []
    for year_pows in years_pows:
        season = year_pows.xpath("./h3/text()")[0]
        weeks_pows = year_pows.xpath("./*[@class='data_grid_box']/div[2]/p")
        for week_pows in weeks_pows:
            week = week_pows.xpath("./strong[1]/text()")[0]
            rdate_string = get_date_from_season_n_week(season, week)
            # print(week)
            if (int(season.split("-")[0])) >= 2001:
                east_pow_nic = week_pows.xpath("./a[1]/@href")[0].split("/")[-1].split(".")[0]
                east_pow_name = player_mapping_df[player_mapping_df.nickname == east_pow_nic].fullname.values[0]
                west_pow_nic = week_pows.xpath("./a[2]/@href")[0].split("/")[-1].split(".")[0]
                west_pow_name = player_mapping_df[player_mapping_df.nickname == west_pow_nic].fullname.values[0]
                e_pows = [season, week, "east", east_pow_name, rdate_string]
                w_pows = [season, week, "west", west_pow_name, rdate_string]
                after2001_pows_list.append(e_pows)
                after2001_pows_list.append(w_pows)
            else:
                pows = week_pows.xpath("./a")
                if len(pows) > 1:
                    st_pow_nickname = week_pows.xpath("./a[1]/@href")[0].split("/")[-1].split(".")[0]
                    st_pow_name = player_mapping_df[player_mapping_df.nickname == st_pow_nickname].fullname.values[0]
                    nd_pow_nickname = week_pows.xpath("./a[2]/@href")[0].split("/")[-1].split(".")[0]
                    nd_pow_name = player_mapping_df[player_mapping_df.nickname == nd_pow_nickname].fullname.values[0]
                    st_pows = [season, week, "", st_pow_name, rdate_string]
                    nd_pows = [season, week, "", nd_pow_name, rdate_string]
                    before2001_pows_list.append(st_pows)
                    before2001_pows_list.append(nd_pows)
                else:
                    st_pow_nickname = week_pows.xpath("./a[1]/@href")[0].split("/")[-1].split(".")[0]
                    st_pow_name = player_mapping_df[player_mapping_df.nickname == st_pow_nickname].fullname.values[0]
                    st_pows = [season, week, "", st_pow_name, rdate_string]
                    before2001_pows_list.append(st_pows)

    after2001_df = pd.DataFrame(after2001_pows_list, columns=after2001_column_names)
    before2001_df = pd.DataFrame(before2001_pows_list, columns=after2001_column_names)

    after2001_df.sort_values(['REWARD_DATE'], inplace=True)
    after2001_df.reset_index(inplace=True, drop=True)
    before2001_df.sort_values(['REWARD_DATE'], inplace=True)
    before2001_df.reset_index(inplace=True, drop=True)

    if after_2001:
        return after2001_df
    else:
        return before2001_df


def get_player_img(player_id, path):
    url = "http://stats.nba.com/media/players/230x185/"+str(player_id)+".png"
    img_file = os.path.join(path, str(player_id) + ".png")
    pic = urllib.urlretrieve(url, img_file)


"""
Utils
"""


def get_date_from_season_n_week(season, week):
    fh_year = int(season.split("-")[0])
    sh_year = fh_year + 1

    mn = str(week).split()[0]
    if mn in ['Sep', 'Oct', 'Nov', 'Dec']:
        year_s = str(fh_year)
    else:
        year_s = str(sh_year)

    s_d = week + " " + str(year_s)
    d = datetime.datetime.strptime(s_d, "%b %d %Y")
    target_date_string = d.strftime('%m/%d/%Y')
    # return str(target_date_string)
    return d