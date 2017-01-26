

```python
import pandas as pd
from pymongo import MongoClient
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017

MONGODB_DB = "nba_odds_n_predict"
MONGODB_COLLECTION = "games_ah_odds"
```


```python
def _connect_to_mongo(host, port, username, password, db):
    """ A util for making a connection to mongo """

    if username and password:
        mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % (username, password, host, port, db)
        conn = MongoClient(mongo_uri)
    else:
        conn = MongoClient(host, port)

    return conn[db]


def read_mongo_data_to_dataframe(db=MONGODB_DB, collection=MONGODB_COLLECTION, query={}, host=MONGODB_SERVER, port=MONGODB_PORT, username=None, password=None, no_id=True):
    """ Read from Mongo and Store into DataFrame """

    # Connect to MongoDB
    db = _connect_to_mongo(host=host, port=port, username=username, password=password, db=db)

    # Make a query to the specific DB and Collection
    cursor = db[collection].find(query)

    # Expand the cursor and construct the DataFrame
    df = pd.DataFrame(list(cursor))

    # Delete the _id
    if no_id:
        del df['_id']

    return df

def map_team_to_id(teams_df, team_name):
    return teams_df[teams_df.FULL_TEAM_NAME == team_name].TEAM_ID.values[0]

def fraction2decimal(f):
    if f.find("/") != -1:
        return float(Decimal(f.split('/')[0]) / Decimal(f.split('/')[1])) + 1
    else:
        return f


def american2decimal(a):
    if a.find("+") != -1:
        return (float(a)/100) + 1
    elif a.find("-") != -1:
        return (100/abs(float(a))) + 1
    else:
        return a


def to_decimal(x):
    if x.find(".") != -1:
        return x
    elif x.find("/") != -1:
        return fraction2decimal(x)
    else:
        return american2decimal(x)


def calculat_payout(row, num=1):
    if float(row['sub_score']) >= (-1) * float(row['ah_'+str(num)]):
        home_win_with_ah = 1.0
    else:
        home_win_with_ah = 0.0
    if float(row['predict_subscore']) >= (-1) * float(row['ah_'+str(num)]):
        return (float(row['new_odd_home_'+str(num)]) * home_win_with_ah) - 1.0
    else:
        return (float(row['new_odd_away_'+str(num)]) * (1.0 - home_win_with_ah)) - 1.0

```


```python
teams_df = pd.read_json('/Users/ccuulinay/github_proj/scrapy_proj/nba_odds_spider/lab/collection_backup/all_teams.json')
ah_df = read_mongo_data_to_dataframe()
```


```python
ah_df.head()
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>ah_1</th>
      <th>ah_2</th>
      <th>ah_3</th>
      <th>ah_4</th>
      <th>away_team</th>
      <th>date_time</th>
      <th>home_team</th>
      <th>odd_away_1</th>
      <th>odd_away_2</th>
      <th>odd_away_3</th>
      <th>...</th>
      <th>odd_cnt_2</th>
      <th>odd_cnt_3</th>
      <th>odd_cnt_4</th>
      <th>odd_home_1</th>
      <th>odd_home_2</th>
      <th>odd_home_3</th>
      <th>odd_home_4</th>
      <th>overtime</th>
      <th>score_away</th>
      <th>score_home</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>-5.0</td>
      <td>-4.5</td>
      <td>-6.0</td>
      <td>-5.5</td>
      <td>Miami Heat</td>
      <td>2015-03-07 02:00:00</td>
      <td>Washington Wizards</td>
      <td>1.98</td>
      <td>1.96</td>
      <td>1.91</td>
      <td>...</td>
      <td>10</td>
      <td>8</td>
      <td>7</td>
      <td>1.86</td>
      <td>1.88</td>
      <td>1.95</td>
      <td>1.89</td>
      <td>False</td>
      <td>97</td>
      <td>99</td>
    </tr>
    <tr>
      <th>1</th>
      <td>-7.0</td>
      <td>-7.5</td>
      <td>-6.5</td>
      <td>-10.5</td>
      <td>Milwaukee Bucks</td>
      <td>2015-03-13 01:00:00</td>
      <td>Indiana Pacers</td>
      <td>1.92</td>
      <td>1.83</td>
      <td>1.98</td>
      <td>...</td>
      <td>7</td>
      <td>7</td>
      <td>4</td>
      <td>1.94</td>
      <td>2.00</td>
      <td>1.86</td>
      <td>2.45</td>
      <td>True</td>
      <td>103</td>
      <td>109</td>
    </tr>
    <tr>
      <th>2</th>
      <td>9.0</td>
      <td>8.5</td>
      <td>9.5</td>
      <td>6.5</td>
      <td>Los Angeles Clippers</td>
      <td>2015-03-19 04:00:00</td>
      <td>Sacramento Kings</td>
      <td>1.94</td>
      <td>1.86</td>
      <td>1.98</td>
      <td>...</td>
      <td>7</td>
      <td>7</td>
      <td>4</td>
      <td>1.92</td>
      <td>1.97</td>
      <td>1.83</td>
      <td>2.28</td>
      <td>False</td>
      <td>116</td>
      <td>105</td>
    </tr>
    <tr>
      <th>3</th>
      <td>14.5</td>
      <td>15.0</td>
      <td>13.5</td>
      <td>15.5</td>
      <td>Los Angeles Clippers</td>
      <td>2015-03-26 01:00:00</td>
      <td>New York Knicks</td>
      <td>17/20</td>
      <td>93/100</td>
      <td>7/10</td>
      <td>...</td>
      <td>8</td>
      <td>4</td>
      <td>4</td>
      <td>97/100</td>
      <td>47/50</td>
      <td>23/20</td>
      <td>43/50</td>
      <td>False</td>
      <td>111</td>
      <td>80</td>
    </tr>
    <tr>
      <th>4</th>
      <td>3.0</td>
      <td>3.5</td>
      <td>2.5</td>
      <td>2.0</td>
      <td>Brooklyn Nets</td>
      <td>2015-02-21 05:30:00</td>
      <td>Los Angeles Lakers</td>
      <td>1.92</td>
      <td>1.94</td>
      <td>1.83</td>
      <td>...</td>
      <td>8</td>
      <td>5</td>
      <td>4</td>
      <td>1.94</td>
      <td>1.87</td>
      <td>2.03</td>
      <td>2.12</td>
      <td>False</td>
      <td>114</td>
      <td>105</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 22 columns</p>
</div>




```python
ah_df = ah_df[ah_df.away_team != 'Team USA']
ah_df = ah_df[ah_df.away_team != 'West']
ah_df = ah_df[ah_df.home_team != 'Team World']
ah_df = ah_df[ah_df.away_team != 'EAST']
ah_df['winner'] = np.where(ah_df['score_home'] - ah_df['score_away']>0, 'home','away')
ah_df['ot'] = ah_df['overtime'].apply(lambda x : 1 if x == True else 0)
ah_df['home_win'] = ah_df['winner'].apply(lambda x : 1 if x == 'home' else 0)

ah_df['date_time_DT'] = pd.to_datetime(ah_df['date_time'])
ah_df['year'] = ah_df['date_time_DT'].dt.year.astype(str)
ah_df['month'] = ah_df['date_time_DT'].dt.month.astype(str)
ah_df['day'] = ah_df['date_time_DT'].dt.day.astype(str)
ah_df['weekDay'] = ah_df['date_time_DT'].dt.dayofweek.astype(str)
```


```python
from fractions import Fraction
from decimal import Decimal

ah_df["new_odd_home_1"]= ah_df.odd_home_1.apply(lambda x: to_decimal(x))
ah_df["new_odd_home_2"]= ah_df.odd_home_2.apply(lambda x: to_decimal(x))
ah_df["new_odd_home_3"]= ah_df.odd_home_3.apply(lambda x: to_decimal(x))
ah_df["new_odd_home_4"]= ah_df.odd_home_4.apply(lambda x: to_decimal(x))
ah_df["new_odd_away_1"]= ah_df.odd_away_1.apply(lambda x: to_decimal(x))
ah_df["new_odd_away_2"]= ah_df.odd_away_2.apply(lambda x: to_decimal(x))
ah_df["new_odd_away_3"]= ah_df.odd_away_3.apply(lambda x: to_decimal(x))
ah_df["new_odd_away_4"]= ah_df.odd_away_4.apply(lambda x: to_decimal(x))
```


```python
ah_df.head()
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>ah_1</th>
      <th>ah_2</th>
      <th>ah_3</th>
      <th>ah_4</th>
      <th>away_team</th>
      <th>date_time</th>
      <th>home_team</th>
      <th>odd_away_1</th>
      <th>odd_away_2</th>
      <th>odd_away_3</th>
      <th>...</th>
      <th>day</th>
      <th>weekDay</th>
      <th>new_odd_home_1</th>
      <th>new_odd_home_2</th>
      <th>new_odd_home_3</th>
      <th>new_odd_home_4</th>
      <th>new_odd_away_1</th>
      <th>new_odd_away_2</th>
      <th>new_odd_away_3</th>
      <th>new_odd_away_4</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>-5.0</td>
      <td>-4.5</td>
      <td>-6.0</td>
      <td>-5.5</td>
      <td>Miami Heat</td>
      <td>2015-03-07 02:00:00</td>
      <td>Washington Wizards</td>
      <td>1.98</td>
      <td>1.96</td>
      <td>1.91</td>
      <td>...</td>
      <td>7</td>
      <td>5</td>
      <td>1.86</td>
      <td>1.88</td>
      <td>1.95</td>
      <td>1.89</td>
      <td>1.98</td>
      <td>1.96</td>
      <td>1.91</td>
      <td>1.93</td>
    </tr>
    <tr>
      <th>1</th>
      <td>-7.0</td>
      <td>-7.5</td>
      <td>-6.5</td>
      <td>-10.5</td>
      <td>Milwaukee Bucks</td>
      <td>2015-03-13 01:00:00</td>
      <td>Indiana Pacers</td>
      <td>1.92</td>
      <td>1.83</td>
      <td>1.98</td>
      <td>...</td>
      <td>13</td>
      <td>4</td>
      <td>1.94</td>
      <td>2.00</td>
      <td>1.86</td>
      <td>2.45</td>
      <td>1.92</td>
      <td>1.83</td>
      <td>1.98</td>
      <td>1.51</td>
    </tr>
    <tr>
      <th>2</th>
      <td>9.0</td>
      <td>8.5</td>
      <td>9.5</td>
      <td>6.5</td>
      <td>Los Angeles Clippers</td>
      <td>2015-03-19 04:00:00</td>
      <td>Sacramento Kings</td>
      <td>1.94</td>
      <td>1.86</td>
      <td>1.98</td>
      <td>...</td>
      <td>19</td>
      <td>3</td>
      <td>1.92</td>
      <td>1.97</td>
      <td>1.83</td>
      <td>2.28</td>
      <td>1.94</td>
      <td>1.86</td>
      <td>1.98</td>
      <td>1.60</td>
    </tr>
    <tr>
      <th>3</th>
      <td>14.5</td>
      <td>15.0</td>
      <td>13.5</td>
      <td>15.5</td>
      <td>Los Angeles Clippers</td>
      <td>2015-03-26 01:00:00</td>
      <td>New York Knicks</td>
      <td>17/20</td>
      <td>93/100</td>
      <td>7/10</td>
      <td>...</td>
      <td>26</td>
      <td>3</td>
      <td>1.97</td>
      <td>1.94</td>
      <td>2.15</td>
      <td>1.86</td>
      <td>1.85</td>
      <td>1.93</td>
      <td>1.7</td>
      <td>1.95</td>
    </tr>
    <tr>
      <th>4</th>
      <td>3.0</td>
      <td>3.5</td>
      <td>2.5</td>
      <td>2.0</td>
      <td>Brooklyn Nets</td>
      <td>2015-02-21 05:30:00</td>
      <td>Los Angeles Lakers</td>
      <td>1.92</td>
      <td>1.94</td>
      <td>1.83</td>
      <td>...</td>
      <td>21</td>
      <td>5</td>
      <td>1.94</td>
      <td>1.87</td>
      <td>2.03</td>
      <td>2.12</td>
      <td>1.92</td>
      <td>1.94</td>
      <td>1.83</td>
      <td>1.75</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 38 columns</p>
</div>




```python
ah_df.drop("odd_home_1", axis=1, inplace=True)
ah_df.drop("odd_home_2", axis=1, inplace=True)
ah_df.drop("odd_home_3", axis=1, inplace=True)
ah_df.drop("odd_home_4", axis=1, inplace=True)
ah_df.drop("odd_away_1", axis=1, inplace=True)
ah_df.drop("odd_away_2", axis=1, inplace=True)
ah_df.drop("odd_away_3", axis=1, inplace=True)
ah_df.drop("odd_away_4", axis=1, inplace=True)
```


```python
ah_df.head()
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>ah_1</th>
      <th>ah_2</th>
      <th>ah_3</th>
      <th>ah_4</th>
      <th>away_team</th>
      <th>date_time</th>
      <th>home_team</th>
      <th>odd_cnt_1</th>
      <th>odd_cnt_2</th>
      <th>odd_cnt_3</th>
      <th>...</th>
      <th>day</th>
      <th>weekDay</th>
      <th>new_odd_home_1</th>
      <th>new_odd_home_2</th>
      <th>new_odd_home_3</th>
      <th>new_odd_home_4</th>
      <th>new_odd_away_1</th>
      <th>new_odd_away_2</th>
      <th>new_odd_away_3</th>
      <th>new_odd_away_4</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>-5.0</td>
      <td>-4.5</td>
      <td>-6.0</td>
      <td>-5.5</td>
      <td>Miami Heat</td>
      <td>2015-03-07 02:00:00</td>
      <td>Washington Wizards</td>
      <td>10</td>
      <td>10</td>
      <td>8</td>
      <td>...</td>
      <td>7</td>
      <td>5</td>
      <td>1.86</td>
      <td>1.88</td>
      <td>1.95</td>
      <td>1.89</td>
      <td>1.98</td>
      <td>1.96</td>
      <td>1.91</td>
      <td>1.93</td>
    </tr>
    <tr>
      <th>1</th>
      <td>-7.0</td>
      <td>-7.5</td>
      <td>-6.5</td>
      <td>-10.5</td>
      <td>Milwaukee Bucks</td>
      <td>2015-03-13 01:00:00</td>
      <td>Indiana Pacers</td>
      <td>9</td>
      <td>7</td>
      <td>7</td>
      <td>...</td>
      <td>13</td>
      <td>4</td>
      <td>1.94</td>
      <td>2.00</td>
      <td>1.86</td>
      <td>2.45</td>
      <td>1.92</td>
      <td>1.83</td>
      <td>1.98</td>
      <td>1.51</td>
    </tr>
    <tr>
      <th>2</th>
      <td>9.0</td>
      <td>8.5</td>
      <td>9.5</td>
      <td>6.5</td>
      <td>Los Angeles Clippers</td>
      <td>2015-03-19 04:00:00</td>
      <td>Sacramento Kings</td>
      <td>9</td>
      <td>7</td>
      <td>7</td>
      <td>...</td>
      <td>19</td>
      <td>3</td>
      <td>1.92</td>
      <td>1.97</td>
      <td>1.83</td>
      <td>2.28</td>
      <td>1.94</td>
      <td>1.86</td>
      <td>1.98</td>
      <td>1.60</td>
    </tr>
    <tr>
      <th>3</th>
      <td>14.5</td>
      <td>15.0</td>
      <td>13.5</td>
      <td>15.5</td>
      <td>Los Angeles Clippers</td>
      <td>2015-03-26 01:00:00</td>
      <td>New York Knicks</td>
      <td>9</td>
      <td>8</td>
      <td>4</td>
      <td>...</td>
      <td>26</td>
      <td>3</td>
      <td>1.97</td>
      <td>1.94</td>
      <td>2.15</td>
      <td>1.86</td>
      <td>1.85</td>
      <td>1.93</td>
      <td>1.7</td>
      <td>1.95</td>
    </tr>
    <tr>
      <th>4</th>
      <td>3.0</td>
      <td>3.5</td>
      <td>2.5</td>
      <td>2.0</td>
      <td>Brooklyn Nets</td>
      <td>2015-02-21 05:30:00</td>
      <td>Los Angeles Lakers</td>
      <td>10</td>
      <td>8</td>
      <td>5</td>
      <td>...</td>
      <td>21</td>
      <td>5</td>
      <td>1.94</td>
      <td>1.87</td>
      <td>2.03</td>
      <td>2.12</td>
      <td>1.92</td>
      <td>1.94</td>
      <td>1.83</td>
      <td>1.75</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 30 columns</p>
</div>




```python
one_hot = pd.get_dummies(ah_df[['away_team','home_team']], prefix=['away_team_', 'home_team_'])
```


```python
ah_df = ah_df.join(one_hot)
ah_df.drop(['away_team','home_team'], axis=1, inplace=True)
```


```python
ah_df.drop(['date_time', 'date_time_DT', 'winner', 'overtime'], axis=1, inplace=True)
```


```python
ah_df['total_score'] = ah_df['score_home'] + ah_df['score_away']
ah_df['sub_score'] = ah_df['score_home'] - ah_df['score_away']
```


```python
ah_df.head()
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>ah_1</th>
      <th>ah_2</th>
      <th>ah_3</th>
      <th>ah_4</th>
      <th>odd_cnt_1</th>
      <th>odd_cnt_2</th>
      <th>odd_cnt_3</th>
      <th>odd_cnt_4</th>
      <th>score_away</th>
      <th>score_home</th>
      <th>...</th>
      <th>home_team__Philadelphia 76ers</th>
      <th>home_team__Phoenix Suns</th>
      <th>home_team__Portland Trail Blazers</th>
      <th>home_team__Sacramento Kings</th>
      <th>home_team__San Antonio Spurs</th>
      <th>home_team__Toronto Raptors</th>
      <th>home_team__Utah Jazz</th>
      <th>home_team__Washington Wizards</th>
      <th>total_score</th>
      <th>sub_score</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>-5.0</td>
      <td>-4.5</td>
      <td>-6.0</td>
      <td>-5.5</td>
      <td>10</td>
      <td>10</td>
      <td>8</td>
      <td>7</td>
      <td>97</td>
      <td>99</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>196</td>
      <td>2</td>
    </tr>
    <tr>
      <th>1</th>
      <td>-7.0</td>
      <td>-7.5</td>
      <td>-6.5</td>
      <td>-10.5</td>
      <td>9</td>
      <td>7</td>
      <td>7</td>
      <td>4</td>
      <td>103</td>
      <td>109</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>212</td>
      <td>6</td>
    </tr>
    <tr>
      <th>2</th>
      <td>9.0</td>
      <td>8.5</td>
      <td>9.5</td>
      <td>6.5</td>
      <td>9</td>
      <td>7</td>
      <td>7</td>
      <td>4</td>
      <td>116</td>
      <td>105</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>221</td>
      <td>-11</td>
    </tr>
    <tr>
      <th>3</th>
      <td>14.5</td>
      <td>15.0</td>
      <td>13.5</td>
      <td>15.5</td>
      <td>9</td>
      <td>8</td>
      <td>4</td>
      <td>4</td>
      <td>111</td>
      <td>80</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>191</td>
      <td>-31</td>
    </tr>
    <tr>
      <th>4</th>
      <td>3.0</td>
      <td>3.5</td>
      <td>2.5</td>
      <td>2.0</td>
      <td>10</td>
      <td>8</td>
      <td>5</td>
      <td>4</td>
      <td>114</td>
      <td>105</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>219</td>
      <td>-9</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 86 columns</p>
</div>




```python
cols = list(ah_df.columns.values)
ah_df = ah_df[[u'away_team__Atlanta Hawks',
 u'away_team__Boston Celtics',
 u'away_team__Brooklyn Nets',
 u'away_team__Charlotte Hornets',
 u'away_team__Chicago Bulls',
 u'away_team__Cleveland Cavaliers',
 u'away_team__Dallas Mavericks',
 u'away_team__Denver Nuggets',
 u'away_team__Detroit Pistons',
 u'away_team__Golden State Warriors',
 u'away_team__Houston Rockets',
 u'away_team__Indiana Pacers',
 u'away_team__Los Angeles Clippers',
 u'away_team__Los Angeles Lakers',
 u'away_team__Memphis Grizzlies',
 u'away_team__Miami Heat',
 u'away_team__Milwaukee Bucks',
 u'away_team__Minnesota Timberwolves',
 u'away_team__New Orleans Pelicans',
 u'away_team__New York Knicks',
 u'away_team__Oklahoma City Thunder',
 u'away_team__Orlando Magic',
 u'away_team__Philadelphia 76ers',
 u'away_team__Phoenix Suns',
 u'away_team__Portland Trail Blazers',
 u'away_team__Sacramento Kings',
 u'away_team__San Antonio Spurs',
 u'away_team__Toronto Raptors',
 u'away_team__Utah Jazz',
 u'away_team__Washington Wizards',
 u'home_team__Atlanta Hawks',
 u'home_team__Boston Celtics',
 u'home_team__Brooklyn Nets',
 u'home_team__Charlotte Hornets',
 u'home_team__Chicago Bulls',
 u'home_team__Cleveland Cavaliers',
 u'home_team__Dallas Mavericks',
 u'home_team__Denver Nuggets',
 u'home_team__Detroit Pistons',
 u'home_team__Golden State Warriors',
 u'home_team__Houston Rockets',
 u'home_team__Indiana Pacers',
 u'home_team__Los Angeles Clippers',
 u'home_team__Los Angeles Lakers',
 u'home_team__Memphis Grizzlies',
 u'home_team__Miami Heat',
 u'home_team__Milwaukee Bucks',
 u'home_team__Minnesota Timberwolves',
 u'home_team__New Orleans Pelicans',
 u'home_team__New York Knicks',
 u'home_team__Oklahoma City Thunder',
 u'home_team__Orlando Magic',
 u'home_team__Philadelphia 76ers',
 u'home_team__Phoenix Suns',
 u'home_team__Portland Trail Blazers',
 u'home_team__Sacramento Kings',
 u'home_team__San Antonio Spurs',
 u'home_team__Toronto Raptors',
 u'home_team__Utah Jazz',
 u'home_team__Washington Wizards',

 u'ah_1',
 u'odd_cnt_1',
 'new_odd_home_1',
 'new_odd_away_1',
 u'ah_2',
 u'odd_cnt_2',
 'new_odd_home_2',
 'new_odd_away_2',
 u'ah_3',
 u'odd_cnt_3',
 'new_odd_home_3',
 'new_odd_away_3',
 u'ah_4',
 u'odd_cnt_4',
 'new_odd_home_4',
 'new_odd_away_4',
 
 'year',
 'month',
 'day',
 'weekDay',
 'ot',
 'home_win',
 u'score_away',
 u'score_home',
 'total_score',
 'sub_score']]
```


```python
ah_df.to_json("ah_df_bk20170120.json", orient='records')
```


```python
ah_data = ah_df.as_matrix()
```


```python
ah_data.shape
```




    (3091, 86)




```python
train_data = ah_data[:,:-5]
train_label = ah_data[:,-5:].astype(int)
```


```python
# First build a simple RFC for home_win
x_train, x_test, y_train, y_test = train_test_split(train_data,train_label[:,0], test_size=0.3)
# clf = RandomForestClassifier(n_estimators=200, criterion='entropy', max_depth=4)

clf = Pipeline([
        ('ss', StandardScaler()),
        ('DTC', RandomForestClassifier(n_estimators=200, criterion='entropy', max_depth=4))])
rf_clf = clf.fit(x_train, y_train)
y_hat = rf_clf.predict(x_test)
result = (y_hat == y_test)
```

    /Users/ccuulinay/.pyenv/versions/2.7.9/lib/python2.7/site-packages/sklearn/utils/validation.py:429: DataConversionWarning: Data with input dtype object was converted to float64 by StandardScaler.
      warnings.warn(msg, _DataConversionWarning)



```python
acc = np.mean(result)
acc
```




    0.69719827586206895




```python
# Try some other clf on home_win
from sklearn.ensemble import GradientBoostingClassifier
x_train, x_test, y_train, y_test = train_test_split(train_data,train_label[:,0], test_size=0.3)

clf = Pipeline([
        ('ss', StandardScaler()),
        ('DTC', GradientBoostingClassifier(n_estimators=200, max_depth=4))])
rf_clf = clf.fit(x_train, y_train)
y_hat = rf_clf.predict(x_test)
result = (y_hat == y_test)
```


```python
acc = np.mean(result)
acc
```




    0.68318965517241381




```python
# Try XGBoost on home_win
import xgboost as xgb
x_train, x_test, y_train, y_test = train_test_split(train_data,train_label[:,0], test_size=0.3)

data_train = xgb.DMatrix(x_train, label=y_train)
data_test = xgb.DMatrix(x_test, label=y_test)
watch_list = [(data_test, 'eval'), (data_train, 'train')]
param = {'max_depth': 3, 'eta': 1, 'silent': 1, 'objective': 'multi:softmax', 'num_class': 2}
bst = xgb.train(param, data_train, num_boost_round=6, evals=watch_list)
y_hat = bst.predict(data_test)
result = (y_hat == y_test)
```

    [0]	eval-merror:0.324353	train-merror:0.294036
    [1]	eval-merror:0.325431	train-merror:0.288488
    [2]	eval-merror:0.329741	train-merror:0.287564
    [3]	eval-merror:0.324353	train-merror:0.275543
    [4]	eval-merror:0.315733	train-merror:0.263985
    [5]	eval-merror:0.318966	train-merror:0.256588


    /Users/ccuulinay/.pyenv/versions/2.7.9/lib/python2.7/site-packages/sklearn/cross_validation.py:44: DeprecationWarning: This module was deprecated in version 0.18 in favor of the model_selection module into which all the refactored classes and functions are moved. Also note that the interface of the new CV iterators are different from that of this module. This module will be removed in 0.20.
      "This module will be removed in 0.20.", DeprecationWarning)



```python
acc = np.mean(result)
acc
```




    0.68103448275862066




```python

```


```python
adjusted_x_cols = [u'away_team__Atlanta Hawks',
 u'away_team__Boston Celtics',
 u'away_team__Brooklyn Nets',
 u'away_team__Charlotte Hornets',
 u'away_team__Chicago Bulls',
 u'away_team__Cleveland Cavaliers',
 u'away_team__Dallas Mavericks',
 u'away_team__Denver Nuggets',
 u'away_team__Detroit Pistons',
 u'away_team__Golden State Warriors',
 u'away_team__Houston Rockets',
 u'away_team__Indiana Pacers',
 u'away_team__Los Angeles Clippers',
 u'away_team__Los Angeles Lakers',
 u'away_team__Memphis Grizzlies',
 u'away_team__Miami Heat',
 u'away_team__Milwaukee Bucks',
 u'away_team__Minnesota Timberwolves',
 u'away_team__New Orleans Pelicans',
 u'away_team__New York Knicks',
 u'away_team__Oklahoma City Thunder',
 u'away_team__Orlando Magic',
 u'away_team__Philadelphia 76ers',
 u'away_team__Phoenix Suns',
 u'away_team__Portland Trail Blazers',
 u'away_team__Sacramento Kings',
 u'away_team__San Antonio Spurs',
 u'away_team__Toronto Raptors',
 u'away_team__Utah Jazz',
 u'away_team__Washington Wizards',
 u'home_team__Atlanta Hawks',
 u'home_team__Boston Celtics',
 u'home_team__Brooklyn Nets',
 u'home_team__Charlotte Hornets',
 u'home_team__Chicago Bulls',
 u'home_team__Cleveland Cavaliers',
 u'home_team__Dallas Mavericks',
 u'home_team__Denver Nuggets',
 u'home_team__Detroit Pistons',
 u'home_team__Golden State Warriors',
 u'home_team__Houston Rockets',
 u'home_team__Indiana Pacers',
 u'home_team__Los Angeles Clippers',
 u'home_team__Los Angeles Lakers',
 u'home_team__Memphis Grizzlies',
 u'home_team__Miami Heat',
 u'home_team__Milwaukee Bucks',
 u'home_team__Minnesota Timberwolves',
 u'home_team__New Orleans Pelicans',
 u'home_team__New York Knicks',
 u'home_team__Oklahoma City Thunder',
 u'home_team__Orlando Magic',
 u'home_team__Philadelphia 76ers',
 u'home_team__Phoenix Suns',
 u'home_team__Portland Trail Blazers',
 u'home_team__Sacramento Kings',
 u'home_team__San Antonio Spurs',
 u'home_team__Toronto Raptors',
 u'home_team__Utah Jazz',
 u'home_team__Washington Wizards',

 u'ah_1',
 u'odd_cnt_1',
 'new_odd_home_1',
 'new_odd_away_1',
 u'ah_2',
 u'odd_cnt_2',
 'new_odd_home_2',
 'new_odd_away_2',
 u'ah_3',
 u'odd_cnt_3',
 'new_odd_home_3',
 'new_odd_away_3',
 u'ah_4',
 u'odd_cnt_4',
 'new_odd_home_4',
 'new_odd_away_4',
 
 'year',
 'month',
 'day',
 'weekDay',
 'ot']
adjusted_y_cols = ['home_win',
 u'score_away',
 u'score_home',
 'total_score',
 'sub_score']
```


```python
home_win = ah_df['home_win']
sub_score = ah_df['sub_score']
```


```python
# Second build a simple RFR for subscore
from sklearn.ensemble import RandomForestRegressor
x_train, x_test, y_train, y_test = train_test_split(train_data,train_label[:,4], test_size=0.3)
# clf = RandomForestClassifier(n_estimators=200, criterion='entropy', max_depth=4)

clf = Pipeline([
        ('ss', StandardScaler()),
        ('DTC', RandomForestRegressor(n_estimators=200, criterion='mse', max_depth=4))])
rf_clf = clf.fit(x_train, y_train)
y_hat = rf_clf.predict(x_test)
```


```python
payout_df = pd.DataFrame(x_test, columns=adjusted_x_cols)
payout_df['predict_subscore'] = y_hat
payout_df['home_win'] = home_win
payout_df['sub_score'] = sub_score
payout_df.head()
payout_df['payout_1'] = payout_df.apply(lambda x : calculat_payout(x), axis=1)
payout_df.payout_1.sum()
```




    31.846831678773995




```python
# Try XGBoost on subscore
import xgboost as xgb
x_train, x_test, y_train, y_test = train_test_split(train_data,train_label[:,4], test_size=0.3)

data_train = xgb.DMatrix(x_train, label=y_train)
data_test = xgb.DMatrix(x_test, label=y_test)
watch_list = [(data_test, 'eval'), (data_train, 'train')]
param = {'max_depth': 3, 'eta': 1, 'silent': 1, 'objective': 'reg:linear'}
bst = xgb.train(param, data_train, num_boost_round=6, evals=watch_list)
y_hat = bst.predict(data_test)
```

    [0]	eval-rmse:12.1017	train-rmse:11.6484
    [1]	eval-rmse:12.0737	train-rmse:11.4597
    [2]	eval-rmse:12.1112	train-rmse:11.3167
    [3]	eval-rmse:12.1297	train-rmse:11.2115
    [4]	eval-rmse:12.1614	train-rmse:11.1227
    [5]	eval-rmse:12.2237	train-rmse:10.9855



```python
payout_df = pd.DataFrame(x_test, columns=adjusted_x_cols)
payout_df['predict_subscore'] = y_hat
payout_df['home_win'] = home_win
payout_df['sub_score'] = sub_score
payout_df.head()
payout_df['payout_1'] = payout_df.apply(lambda x : calculat_payout(x), axis=1)
payout_df.payout_1.sum()
```




    0.87669043070581765




```python
# Build a linear regressor for subscore
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Lasso, Ridge
from sklearn.model_selection import GridSearchCV

x_train, x_test, y_train, y_test = train_test_split(train_data,train_label[:,4], test_size=0.3)
# clf = RandomForestClassifier(n_estimators=200, criterion='entropy', max_depth=4)

linreg = LinearRegression()
lr_model = linreg.fit(x_train, y_train)
y_hat = linreg.predict(x_test)
```


```python
payout_df = pd.DataFrame(x_test, columns=adjusted_x_cols)
payout_df['predict_subscore'] = y_hat
payout_df['home_win'] = home_win
payout_df['sub_score'] = sub_score
payout_df.head()
payout_df['payout_1'] = payout_df.apply(lambda x : calculat_payout(x), axis=1)
payout_df.payout_1.sum()
```




    -28.866901925483766




```python

```
