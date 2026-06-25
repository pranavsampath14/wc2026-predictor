import numpy as np
import pandas as pd
import random
from datetime import datetime
from features import elo_current, run_prediction, get_recent_goals
from itertools import combinations

GROUPS = {
    'A': ['Mexico', 'South Africa', 'South Korea', 'Czechia'],
    'B': ['Canada', 'Bosnia and Herzegovina', 'Qatar', 'Switzerland'],
    'C': ['Brazil', 'Morocco', 'Haiti', 'Scotland'],
    'D': ['United States', 'Paraguay', 'Australia', 'Turkey'],
    'E': ['Germany', 'Curaçao', 'Ivory Coast', 'Ecuador'],
    'F': ['Netherlands', 'Japan', 'Sweden', 'Tunisia'],
    'G': ['Belgium', 'Egypt', 'Iran', 'New Zealand'],
    'H': ['Spain', 'Cape Verde', 'Saudi Arabia', 'Uruguay'],
    'I': ['France', 'Senegal', 'Iraq', 'Norway'],
    'J': ['Argentina', 'Algeria', 'Austria', 'Jordan'],
    'K': ['Portugal', 'DR Congo', 'Uzbekistan', 'Colombia'],
    'L': ['England', 'Croatia', 'Ghana', 'Panama'],
}

BRACKET = [
    (73, ('runner', 'A'), ('runner', 'B')),
    (74, ('winner', 'E'), ('third', ['A','B','C','D','F'])),
    (75, ('winner', 'F'), ('runner', 'C')),
    (76, ('winner', 'C'), ('runner', 'F')),
    (77, ('winner', 'I'), ('third', ['C','D','F','G','H'])),
    (78, ('runner', 'E'), ('runner', 'I')),
    (79, ('winner', 'A'), ('third', ['C','E','F','H','I'])),
    (80, ('winner', 'L'), ('third', ['E','H','I','J','K'])),
    (81, ('winner', 'D'), ('third', ['B','E','F','I','J'])),
    (82, ('winner', 'G'), ('third', ['A','E','H','I','J'])),
    (83, ('runner', 'K'), ('runner', 'L')),
    (84, ('winner', 'H'), ('runner', 'J')),
    (85, ('winner', 'B'), ('third', ['E','F','G','I','J'])),
    (86, ('winner', 'J'), ('runner', 'H')),
    (87, ('winner', 'K'), ('third', ['D','E','I','J','L'])),
    (88, ('runner', 'D'), ('runner', 'G')),
]


HOST_NATIONS = ['United States', 'Canada', 'Mexico']

def precompute_probabilities():
    cache = {}
    teams = elo_current['country'].tolist()
    
    for home_team in teams:
        for away_team in teams:
            if home_team == away_team:
                continue
            
            # compute features and get probabilities and then
            # store in dictionary
            cache[(home_team, away_team)] = run_prediction(home_team=home_team, away_team=away_team)

    
    return cache

prob_cache = None
goals_cache = None

def initialise_caches():
    global prob_cache, goals_cache
    if prob_cache is None:
        print("Precomputing match probabilities now:")
        prob_cache = precompute_probabilities()
        goals_cache = precompute_goals()
        print("Caches built.")

def simulate_match(home_team, away_team):
    outcomes = [home_team, 'draw', away_team]
    probs = prob_cache[(home_team, away_team)]
    probs = np.array(probs)
    # normalise to exactly 1
    probs = probs / probs.sum()
    return np.random.choice(outcomes, p=probs)

def precompute_goals():
    cache = {}
    teams = elo_current['country'].tolist()
    today = pd.Timestamp(datetime.now().date())
    
    for team in teams:
        scored, conceded = get_recent_goals(team, today)
        cache[team] = {'scored': scored, 'conceded': conceded}
    
    return cache


def simulate_scoreline(home_team, away_team, winner):
    home_xg = (goals_cache[home_team]['scored'] + goals_cache[away_team]['conceded']) / 2
    away_xg = (goals_cache[away_team]['scored'] + goals_cache[home_team]['conceded']) / 2
    
    while True:
        home_goals = np.random.poisson(home_xg)
        away_goals = np.random.poisson(away_xg)
        
        if winner == home_team and (home_goals > away_goals):
            break
        if winner == away_team and (away_goals > home_goals):
            break
        if winner == 'draw' and (away_goals == home_goals):
            break
    
    return home_goals, away_goals

""" for i in range(5):
    winner = simulate_match('France', 'Brazil')
    home_goals, away_goals = simulate_scoreline('France', 'Brazil', winner)
    print(f"{winner} | France {home_goals} - {away_goals} Brazil") """

def simulate_group(teams):
    # initialise standings
    standings = {team: {'points': 0, 'gd': 0, 'gs': 0} for team in teams}
    
    for team_a, team_b in combinations(teams, 2):
        # ensure host nations are always home
        if team_b in HOST_NATIONS:
            home_team, away_team = team_b, team_a
        else:
            home_team, away_team = team_a, team_b
        
        # simulate the match
        winner = simulate_match(home_team, away_team)
        home_goals, away_goals = simulate_scoreline(home_team, away_team, winner)
        
        # update standings — your code here
        # you need to update points, gd, and gs for both teams
        # winner gets 3 points, draw gets 1 each, loser gets 0
        # gd = goals scored minus goals conceded
        # gs = goals scored
        standings[away_team]['gs'] += away_goals
        standings[home_team]['gs'] += home_goals

        if winner == home_team:
            standings[home_team]['points'] += 3
            standings[home_team]['gd'] += home_goals - away_goals

            standings[away_team]['gd'] += away_goals - home_goals
        if winner == away_team:
            standings[away_team]['points'] += 3
            standings[home_team]['gd'] += home_goals - away_goals

            standings[away_team]['gd'] += away_goals - home_goals
        if winner == 'draw':
            standings[home_team]['points'] += 1
            standings[away_team]['points'] += 1
        
    # sort standings by points, then gd, then gs
    sorted_standings = sorted(
        standings.items(),
        key=lambda x: (x[1]['points'], x[1]['gd'], x[1]['gs']),
        reverse=True
    )
    
    return sorted_standings

""" for i in range(5):
    result = simulate_group(GROUPS['C'])
    for team, stats in result:
        print(f"{team}: {stats['points']}pts, gd={stats['gd']}, gs={stats['gs']}")
    print("---")
 """

def simulate_all_groups():
    all_results = {}
    for group_id, teams in GROUPS.items():
        all_results[group_id] = simulate_group(teams)
    return all_results

def get_group_winners_and_runners_up(all_group_results):
    winners = []
    runners_up = []
    for group_id, standings in all_group_results.items():
        winners.append(standings[0][0])
        runners_up.append(standings[1][0])
    return winners, runners_up

def get_best_third_place_teams(all_group_results):
    third_place_teams = []
    for group_id, standings in all_group_results.items():
        team_name = standings[2][0]
        stats = standings[2][1]
        third_place_teams.append((team_name, stats, group_id))
    
    third_place_teams.sort(
        key=lambda x: (x[1]['points'], x[1]['gd'], x[1]['gs']),
        reverse=True
    )
    
    return [(team, group) for team, stats, group in third_place_teams[:8]]


def resolve_team(source, winners_dict, runners_dict, third_dict):
    if source[0] == 'winner':
        return winners_dict[source[1]]
    elif source[0] == 'runner':
        return runners_dict[source[1]]
    elif source[0] == 'third':
        eligible_groups = source[1]
        for g in eligible_groups:
            if g in third_dict:
                return third_dict.pop(g)
        # fallback — take any remaining third place team
        if third_dict:
            return third_dict.pop(next(iter(third_dict)))
        return None  

    

def build_round_of_32(winners, runners_up, best_third):
    group_order = ['A','B','C','D','E','F','G','H','I','J','K','L']
    
    winners_dict = {group_order[i]: winners[i] for i in range(12)}
    runners_dict = {group_order[i]: runners_up[i] for i in range(12)}
    # key 3rd place by group
    third_dict = {group: team for team, group in best_third}  
    
    matchups = []
    for match_id, team1_source, team2_source in BRACKET:
        team1 = resolve_team(team1_source, winners_dict, runners_dict, third_dict)
        team2 = resolve_team(team2_source, winners_dict, runners_dict, third_dict)
        matchups.append((team1, team2))
    
    return matchups

""" all_results = simulate_all_groups()
winners, runners_up = get_group_winners_and_runners_up(all_results)
best_third = get_best_third_place_teams(all_results)
matchups = build_round_of_32(winners, runners_up, best_third)

print(f"Total teams advancing: {len(winners) + len(runners_up) + len(best_third)}")
print("\nRound of 32 matchups:")
for i, (team1, team2) in enumerate(matchups):
    print(f"Match {i+73}: {team1} vs {team2}")
 """

def simulate_knockout_round(matchups):
    winners = []
    for team1, team2 in matchups:
        probs = np.array(prob_cache[(team1, team2)], dtype=np.float64)
        home_win = float(probs[0])
        away_win = float(probs[2])
        total = home_win + away_win
        p_home = home_win / total
        result = np.random.choice([team1, team2], p=[p_home, 1.0 - p_home])
        winners.append(result)
    return winners

def pair_winners(winners):
    return [(winners[i], winners[i+1]) for i in range(0, len(winners), 2)]

def simulate_knockout(matchups, results):
    # R32 — 16 matches, 16 winners
    r32_winners = simulate_knockout_round(matchups)
    for team in r32_winners:
        results[team]['r16'] += 1

    # R16
    r16_matchups = pair_winners(r32_winners)
    r16_winners = simulate_knockout_round(r16_matchups)
    for team in r16_winners:
        results[team]['qf'] += 1

    # QF
    qf_matchups = pair_winners(r16_winners)
    qf_winners = simulate_knockout_round(qf_matchups)
    for team in qf_winners:
        results[team]['sf'] += 1

    # SF
    sf_matchups = pair_winners(qf_winners)
    sf_winners = simulate_knockout_round(sf_matchups)
    for team in sf_winners:
        results[team]['final'] += 1

    # Final
    final_winner = simulate_knockout_round([(sf_winners[0], sf_winners[1])])[0]
    results[final_winner]['winner'] += 1


def simulate_tournament():
    initialise_caches();
    # initialise results tracker for all 48 teams
    all_teams = [team for teams in GROUPS.values() for team in teams]
    results = {team: {'r32': 0, 'r16': 0, 'qf': 0, 'sf': 0, 'final': 0, 'winner': 0} for team in all_teams}

    N_SIMULATIONS = 10000

    for i in range(N_SIMULATIONS):
        # group stage
        all_group_results = simulate_all_groups()
        winners, runners_up = get_group_winners_and_runners_up(all_group_results)
        best_third = get_best_third_place_teams(all_group_results)

        # track group stage advancement — all winners, runners up, best third made r32
        for team in winners + runners_up + [t for t, g in best_third]:
            results[team]['r32'] += 1

        # build bracket and simulate knockouts
        matchups = build_round_of_32(winners, runners_up, best_third)
        simulate_knockout(matchups, results)

    # convert counts to probabilities
    final_results = {}
    for team, counts in results.items():
        final_results[team] = {
            'r32': round(counts['r32'] / N_SIMULATIONS, 3),
            'r16': round(counts['r16'] / N_SIMULATIONS, 3),
            'qf': round(counts['qf'] / N_SIMULATIONS, 3),
            'sf': round(counts['sf'] / N_SIMULATIONS, 3),
            'final': round(counts['final'] / N_SIMULATIONS, 3),
            'winner': round(counts['winner'] / N_SIMULATIONS, 3),
        }

    return final_results

""" print("Running tournament simulation...")
sim_results = simulate_tournament()
# print top 10 by winner probability
sorted_teams = sorted(sim_results.items(), key=lambda x: x[1]['winner'], reverse=True)
for team, probs in sorted_teams[:10]:
    print(f"{team}: winner={probs['winner']}, final={probs['final']}, sf={probs['sf']}") """