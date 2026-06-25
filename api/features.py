import pandas as pd
import numpy as np
from datetime import datetime
import joblib
import os

HOST_NATIONS = ['United States', 'Canada', 'Mexico']

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load Data
results = pd.read_csv(os.path.join(BASE_DIR, '../data/raw/results.csv'))
elo_wc = pd.read_csv(os.path.join(BASE_DIR, '../data/raw/elo_ratings_wc2026.csv'))

# Load results
results['date'] = pd.to_datetime(results['date'])
results = results[results['date'] >= '1990-01-01']
results = results.sort_values('date').reset_index(drop=True)
results = results.dropna(subset=['home_score', 'away_score'])

def get_result(row):
    if row['home_score'] > row['away_score']:
        return 'home_win'
    elif row['home_score'] < row['away_score']:
        return 'away_win'
    else:
        return 'draw'

results['result'] = results.apply(get_result, axis=1)

tournament_weights = {
    'FIFA World Cup qualification': 2.5,
    'FIFA World Cup': 4.0,
    'UEFA Euro': 3.0,
    'UEFA Euro qualification': 2.0,
    'Copa América': 3.0,
    'Africa Cup of Nations': 2.5,
    'UEFA Nations League': 2.0,
    'Friendly': 0.5,
}

def get_tournament_weight(tournament):
    for key in tournament_weights:
        if key.lower() in tournament.lower():
            return tournament_weights[key]
    return 1.0

results['tournament_weight'] = results['tournament'].apply(get_tournament_weight)

elo_wc['snapshot_date'] = pd.to_datetime(elo_wc['snapshot_date'])
elo_current = elo_wc.sort_values('snapshot_date').groupby('country').last().reset_index()

# Load model and encoder here so both app.py and simulator.py can use them
model = joblib.load(os.path.join(BASE_DIR, '../model/xgb_model.pkl'))
le = joblib.load(os.path.join(BASE_DIR, '../model/label_encoder.pkl'))


def get_current_elo(country):
    row = elo_current[elo_current['country'] == country]
    if not row.empty:
        return row.iloc[0]['rating']
    return 1500

def get_recent_form(country, curr_date):
    res_filtered = results[
        ((results['home_team'] == country) | (results['away_team'] == country)) &
        (results['date'] < curr_date)
    ]
    res_filtered = res_filtered.sort_values('date').iloc[-10:][['home_team', 'away_team', 'result', 'tournament_weight']]

    available_points = res_filtered['tournament_weight'].sum()
    form_points = 0

    for _, row in res_filtered.iterrows():
        if ((row['home_team'] == country and row['result'] == 'home_win') or
            (row['away_team'] == country and row['result'] == 'away_win')):
            form_points += row['tournament_weight']
        elif row['result'] == 'draw':
            form_points += row['tournament_weight'] * 0.5

    if available_points == 0:
        return 0
    return form_points / available_points

def get_recent_goals(country, curr_date):
    res_filtered = results[
        ((results['home_team'] == country) | (results['away_team'] == country)) &
        (results['date'] < curr_date)
    ]
    res_filtered = res_filtered.sort_values('date').iloc[-10:]

    if len(res_filtered) == 0:
        return 0, 0

    goals_scored = 0
    goals_conceded = 0

    for _, row in res_filtered.iterrows():
        if row['home_team'] == country:
            goals_scored += row['home_score']
            goals_conceded += row['away_score']
        else:
            goals_scored += row['away_score']
            goals_conceded += row['home_score']

    n = len(res_filtered)
    return goals_scored / n, goals_conceded / n

def get_head_to_head(home_country, away_country, curr_date):
    res_filtered = results[
        (((results['home_team'] == home_country) & (results['away_team'] == away_country)) |
         ((results['home_team'] == away_country) & (results['away_team'] == home_country))) &
        (results['date'] < curr_date)
    ]

    total_games = len(res_filtered)

    if total_games == 0:
        return [0.33, 0.33, 0.33]

    agg_home_wins = 0
    agg_away_wins = 0
    draws = 0

    for _, row in res_filtered.iterrows():
        if ((row['home_team'] == home_country and row['result'] == 'home_win') or
            (row['away_team'] == home_country and row['result'] == 'away_win')):
            agg_home_wins += 1
        elif ((row['home_team'] == away_country and row['result'] == 'home_win') or
              (row['away_team'] == away_country and row['result'] == 'away_win')):
            agg_away_wins += 1
        else:
            draws += 1

    weight = min(total_games / 10, 1.0)

    blended_home = weight * (agg_home_wins / total_games) + (1 - weight) * 0.33
    blended_away = weight * (agg_away_wins / total_games) + (1 - weight) * 0.33
    blended_draw = weight * (draws / total_games) + (1 - weight) * 0.33

    return [blended_home, blended_away, blended_draw]

def get_features_for_match(home_team, away_team, neutral):
    today = pd.Timestamp(datetime.now().date())

    home_elo = get_current_elo(home_team)
    away_elo = get_current_elo(away_team)
    elo_diff = home_elo - away_elo

    home_form = get_recent_form(home_team, today)
    away_form = get_recent_form(away_team, today)
    form_diff = home_form - away_form

    home_goals_scored, home_goals_conceded = get_recent_goals(home_team, today)
    away_goals_scored, away_goals_conceded = get_recent_goals(away_team, today)

    h2h = get_head_to_head(home_team, away_team, today)

    return [
        elo_diff, home_form, away_form, form_diff,
        h2h[0], h2h[1], h2h[2], neutral,
        home_goals_scored, home_goals_conceded,
        away_goals_scored, away_goals_conceded
    ]

def is_neutral(home_team):
    if home_team in HOST_NATIONS:
        return 0
    return 1

def run_prediction(home_team, away_team):
    neutral = is_neutral(home_team)

    features_a = get_features_for_match(home_team, away_team, neutral)
    proba_a = model.predict_proba(np.array(features_a).reshape(1, -1))[0]

    if neutral == 1:
        features_b = get_features_for_match(away_team, home_team, neutral)
        proba_b = model.predict_proba(np.array(features_b).reshape(1, -1))[0]

        home_win_prob = (proba_a[2] + proba_b[0]) / 2
        draw_prob     = (proba_a[1] + proba_b[1]) / 2
        away_win_prob = (proba_a[0] + proba_b[2]) / 2
    else:
        home_win_prob = proba_a[2]
        draw_prob     = proba_a[1]
        away_win_prob = proba_a[0]

    return [home_win_prob, draw_prob, away_win_prob]