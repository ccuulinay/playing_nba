from __future__ import division
from __future__ import print_function

import pandas as pd
import numpy as np
import itertools

from sklearn.model_selection import train_test_split

import tensorflow as tf
import odds_data_getter as odg

MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017

MONGODB_DB = "nba_odds_n_predict"
MONGODB_COLLECTION = "games_ah_odds"

COLUMNS = ['away_team__Atlanta_Hawks',
           'away_team__Boston_Celtics',
           'away_team__Brooklyn_Nets',
           'away_team__Charlotte_Hornets',
           'away_team__Chicago_Bulls',
           'away_team__Cleveland_Cavaliers',
           'away_team__Dallas_Mavericks',
           'away_team__Denver_Nuggets',
           'away_team__Detroit_Pistons',
           'away_team__Golden_State_Warriors',
           'away_team__Houston_Rockets',
           'away_team__Indiana_Pacers',
           'away_team__Los_Angeles_Clippers',
           'away_team__Los_Angeles_Lakers',
           'away_team__Memphis_Grizzlies',
           'away_team__Miami_Heat',
           'away_team__Milwaukee_Bucks',
           'away_team__Minnesota_Timberwolves',
           'away_team__New_Orleans_Pelicans',
           'away_team__New_York_Knicks',
           'away_team__Oklahoma_City_Thunder',
           'away_team__Orlando_Magic',
           'away_team__Philadelphia_76ers',
           'away_team__Phoenix_Suns',
           'away_team__Portland_Trail_Blazers',
           'away_team__Sacramento_Kings',
           'away_team__San_Antonio_Spurs',
           'away_team__Toronto_Raptors',
           'away_team__Utah_Jazz',
           'away_team__Washington_Wizards',
           'home_team__Atlanta_Hawks',
           'home_team__Boston_Celtics',
           'home_team__Brooklyn_Nets',
           'home_team__Charlotte_Hornets',
           'home_team__Chicago_Bulls',
           'home_team__Cleveland_Cavaliers',
           'home_team__Dallas_Mavericks',
           'home_team__Denver_Nuggets',
           'home_team__Detroit_Pistons',
           'home_team__Golden_State_Warriors',
           'home_team__Houston_Rockets',
           'home_team__Indiana_Pacers',
           'home_team__Los_Angeles_Clippers',
           'home_team__Los_Angeles_Lakers',
           'home_team__Memphis_Grizzlies',
           'home_team__Miami_Heat',
           'home_team__Milwaukee_Bucks',
           'home_team__Minnesota_Timberwolves',
           'home_team__New_Orleans_Pelicans',
           'home_team__New_York_Knicks',
           'home_team__Oklahoma_City_Thunder',
           'home_team__Orlando_Magic',
           'home_team__Philadelphia_76ers',
           'home_team__Phoenix_Suns',
           'home_team__Portland_Trail_Blazers',
           'home_team__Sacramento_Kings',
           'home_team__San_Antonio_Spurs',
           'home_team__Toronto_Raptors',
           'home_team__Utah_Jazz',
           'home_team__Washington_Wizards',
           'ah_1',
           'odd_cnt_1',
           'new_odd_home_1',
           'new_odd_away_1',
           # 'ah_2',
           # 'odd_cnt_2',
           # 'new_odd_home_2',
           # 'new_odd_away_2',
           # 'ah_3',
           # 'odd_cnt_3',
           # 'new_odd_home_3',
           # 'new_odd_away_3',
           # 'ah_4',
           # 'odd_cnt_4',
           # 'new_odd_home_4',
           # 'new_odd_away_4',
           'year',
           'month',
           'day',
           'weekDay',
           'ot',
           'home_win',
           'score_away',
           'score_home',
           'total_score',
           'sub_score']

FEATURES = COLUMNS[:-5]

LABEL_1 = ['home_win']
LABEL_2 = ['sub_score']


def input_fn(data_df, label_df):
    continuous_cols = {name: tf.constant(data_df[name].values)
                       for name in FEATURES}
    """
    categorical_cols = {k: tf.SparseTensor(
        indices=[[i, 0] for i in range(df[k].size)],
        values=df[k].values,
        shape=[df[k].size, 1])
                    for k in CATEGORICAL_COLUMNS
    }

    feature_cols = dict(continuous_cols.items() + categorical_cols.items())
    """
    f_cols = dict(continuous_cols.items())
    label = tf.constant(label_df[LABEL_2].values)
    return f_cols, label


def read_n_preprocess_ah_df(teams_df):
    ah_df = odg.read_mongo_data_to_dataframe()
    ah_df = ah_df[ah_df.away_team != 'Team USA']
    ah_df = ah_df[ah_df.away_team != 'West']
    ah_df = ah_df[ah_df.home_team != 'Team World']
    ah_df = ah_df[ah_df.away_team != 'EAST']

    ah_df = ah_df.merge(teams_df, how='left', left_on='away_team', right_on='FULL_TEAM_NAME')
    ah_df.drop(['FULL_TEAM_NAME'],axis=1, inplace=True)
    ah_df.rename(columns={'TEAM_ID': 'away_team_id'}, inplace=True)
    ah_df = ah_df.merge(teams_df, how='left', left_on='home_team', right_on='FULL_TEAM_NAME')
    ah_df.drop(['FULL_TEAM_NAME'],axis=1, inplace=True)
    ah_df.rename(columns={'TEAM_ID': 'home_team_id'}, inplace=True)

    ah_df['winner'] = np.where(ah_df['score_home'] - ah_df['score_away'] > 0, 'home', 'away')
    ah_df['ot'] = ah_df['overtime'].apply(lambda x: 1 if x == True else 0)
    ah_df['home_win'] = ah_df['winner'].apply(lambda x: 1 if x == 'home' else 0)

    ah_df['date_time_DT'] = pd.to_datetime(ah_df['date_time'])
    ah_df['year'] = ah_df['date_time_DT'].dt.year.astype(int)
    ah_df['month'] = ah_df['date_time_DT'].dt.month.astype(int)
    ah_df['day'] = ah_df['date_time_DT'].dt.day.astype(int)
    ah_df['weekDay'] = ah_df['date_time_DT'].dt.dayofweek.astype(int)

    for i in range(1, 5):
        ah_df["new_odd_home_" + str(i)] = ah_df["odd_home_" + str(i)].apply(lambda x: odg.to_decimal(x))
        ah_df["new_odd_away_" + str(i)] = ah_df["odd_away_" + str(i)].apply(lambda x: odg.to_decimal(x))
        ah_df["new_odd_home_" + str(i)] = ah_df["new_odd_home_" + str(i)].astype(float)
        ah_df["new_odd_away_" + str(i)] = ah_df["new_odd_away_" + str(i)].astype(float)

    ah_df.drop(
        ['odd_home_1', 'odd_home_2', 'odd_home_3', 'odd_home_4', 'odd_away_1', 'odd_away_2', 'odd_away_3',
         'odd_away_4'],
        axis=1, inplace=True)

    one_hot = pd.get_dummies(ah_df[['away_team', 'home_team']], prefix=['away_team_', 'home_team_'])
    ah_df = ah_df.join(one_hot)
    ah_df.drop(['away_team', 'home_team'], axis=1, inplace=True)
    ah_df.drop(['date_time', 'date_time_DT', 'winner', 'overtime'], axis=1, inplace=True)

    ah_df['total_score'] = ah_df['score_home'] + ah_df['score_away']
    ah_df['sub_score'] = ah_df['score_home'] - ah_df['score_away']

    # ah_df['bet_winner'] = np.where(float(row['sub_score']) + float(row['ah_'+str(num)]) >= 0, 'home', 'away')

    ah_df.rename(columns=lambda x: x.replace(' ', '_'), inplace=True)
    return ah_df


def main(unused_argv):
    advanced_stat_df = pd.read_json('./advanced_data_slice_201702.json')
    teams_df = pd.read_json('/Users/ccuulinay/github_proj/scrapy_proj/nba_odds_spider/lab/collection_backup/all_teams.json')
    teams_df.drop(['TEAM_CITY', 'TEAM_NAME'],axis=1, inplace=True)

    ah_df = read_n_preprocess_ah_df(teams_df)

    ah_df = ah_df[COLUMNS]
    ah_df.sort_values(by=['year', 'month','day'], ascending=[1, 1, 1], inplace=True)

    result_df = pd.merge(advanced_stat_df, ah_df, left_index=True, right_index=True, how='inner')

    NEW_COLUMNS = result_df.columns.tolist()
    NEW_FEATURES = NEW_COLUMNS[:-5]

    # ah_df = pd.DataFrame(ah_df)
    # Defining The Logistic Regression Model
    dnn_model_dir = './ah_model/dnn_model_dir/'

    feature_df = result_df[NEW_FEATURES]
    label_df = ah_df[LABEL_2]

    x_train, x_test, y_train, y_test = train_test_split(feature_df, label_df, test_size=0.3)

    feature_cols = [tf.contrib.layers.real_valued_column(k) for k in FEATURES]

    regressor = tf.contrib.learn.DNNRegressor(feature_columns=feature_cols, model_dir=dnn_model_dir,
                                              hidden_units=[256, 64, 8])

    regressor.fit(input_fn=lambda: input_fn(x_train, y_train), steps=5000)

    # ev = regressor.evaluate(input_fn=lambda: input_fn(test_set), steps=1)
    # loss_score = ev["loss"]
    # print("Loss: {0:f}".format(loss_score))
    print(np.shape(x_test))
    y_len = np.shape(x_test)[0]
    y = regressor.predict(input_fn=lambda: input_fn(x_test, y_test))
    # list_y = list(y)
    # print(len(list_y))
    predictions = list(itertools.islice(y, y_len))
    # print("Predictions: {}".format(str(predictions)))


    home_win = result_df['home_win']
    sub_score = result_df['sub_score']
    payout_df = pd.DataFrame(x_test, columns=NEW_FEATURES)
    payout_df['predict_subscore'] = predictions
    payout_df['home_win'] = home_win
    payout_df['sub_score'] = sub_score
    payout_df['payout_1'] = payout_df.apply(lambda x : odg.calculate_payout(x), axis=1)
    # payout_df['payout_2'] = payout_df.apply(lambda x : calculate_payout(x, num=2), axis=1)
    # payout_df['payout_3'] = payout_df.apply(lambda x : calculate_payout(x, num=3), axis=1)
    # payout_df['payout_4'] = payout_df.apply(lambda x : calculate_payout(x, num=4), axis=1)
    # print(payout_df.payout_1.sum(), payout_df.payout_2.sum(),payout_df.payout_3.sum(),payout_df.payout_4.sum())
    print(payout_df.payout_1.sum())


if __name__ == "__main__":
    tf.app.run()
