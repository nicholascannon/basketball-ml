#!/usr/bin/env python
import os
import pathlib
import sys
import csv
import json
from tqdm import tqdm

DATA_DIR = os.path.join(pathlib.Path().absolute(), 'data')
RAW_DATA = os.path.join(DATA_DIR, 'raw')
PROC_DATA = os.path.join(DATA_DIR, 'processed')

HEADERS = [
    'GAME_ID',
    'DATE',
    'SEASON',

    'A_ID',
    'H_ID',

    'A_FGM', 'A_FGA', 'A_FG_PCT', 'A_FG3M', 'A_FG3A', 'A_FG3_PCT', 'A_FTM',
    'A_FTA', 'A_FT_PCT', 'A_OREB', 'A_DREB', 'A_REB', 'A_AST', 'A_STL',
    'A_BLK', 'A_TO', 'A_PF', 'A_PTS', 'A_PLUS_MIN',
    'H_FGM', 'H_FGA', 'H_FG_PCT', 'H_FG3M', 'H_FG3A', 'H_FG3_PCT', 'H_FTM',
    'H_FTA', 'H_FT_PCT', 'H_OREB', 'H_DREB', 'H_REB', 'H_AST', 'H_STL',
    'H_BLK', 'H_TO', 'H_PF', 'H_PTS', 'H_PLUS_MIN',

    'A_TM_TOV_PCT',
    'H_TM_TOV_PCT',

    'A_OFF_RATING', 'A_DEF_RATING', 'A_EFG_PCT', 'A_TS_PCT', 'A_PACE',
    'H_OFF_RATING', 'H_DEF_RATING', 'H_EFG_PCT', 'H_TS_PCT', 'H_PACE',

    'A_PTS_OFF_TO', 'A_PTS_2ND_CHANCE', 'A_PTS_FB', 'A_PTS_PAINT',
    'H_PTS_OFF_TO', 'H_PTS_2ND_CHANCE', 'H_PTS_FB', 'H_PTS_PAINT',

    'A_DIST', 'A_ORBC', 'A_DRBC', 'A_RBC', 'A_TCHS', 'A_PASS', 'A_CFGM',
    'A_CFGA', 'A_UFGM', 'A_UFGA',
    'H_DIST', 'H_ORBC', 'H_DRBC', 'H_RBC', 'H_TCHS', 'H_PASS', 'H_CFGM',
    'H_CFGA', 'H_UFGM', 'H_UFGA',

    'HOME_WIN'
]


def process_game(game_path):
    """
    team_idx[0] -> AWAY
    team_idx[1] -> HOME
    """
    data = []
    team_idx = []

    with open(os.path.join(game_path, 'boxscore-summary.json')) as f:
        summary = json.load(f)

        data.append(summary['resultSets'][0]['rowSet'][0][0])  # date
        data.append(summary['resultSets'][0]['rowSet'][0][8])  # season

        away_id = summary['resultSets'][0]['rowSet'][0][7]
        home_id = summary['resultSets'][0]['rowSet'][0][6]
        data.append(away_id)
        data.append(home_id)

    with open(os.path.join(game_path, 'traditional.json')) as f:
        traditional = json.load(f)

        # figure out home / away indexes
        if traditional['resultSets'][1]['rowSet'][0][1] == away_id:
            team_idx = [0, 1]
        else:
            team_idx = [1, 0]

        # scores
        home_win = int(
            traditional['resultSets'][1]['rowSet'][team_idx[1]][23] >
            traditional['resultSets'][1]['rowSet'][team_idx[0]][23]
        )

        for team in team_idx:
            data += traditional['resultSets'][1]['rowSet'][team][6:25]

    with open(os.path.join(game_path, 'four-factors.json')) as f:
        factors = json.load(f)

        # figure out home / away indexes
        if factors['resultSets'][1]['rowSet'][0][1] == away_id:
            team_idx = [0, 1]
        else:
            team_idx = [1, 0]

        for team in team_idx:
            data.append(factors['resultSets'][1]['rowSet'][team][8])

    with open(os.path.join(game_path, 'advanced.json')) as f:
        adv = json.load(f)

        # figure out home / away indexes
        if adv['resultSets'][1]['rowSet'][0][1] == away_id:
            team_idx = [0, 1]
        else:
            team_idx = [1, 0]

        for team in team_idx:
            data += [
                adv['resultSets'][1]['rowSet'][team][7],
                adv['resultSets'][1]['rowSet'][team][9],
                adv['resultSets'][1]['rowSet'][team][20],
                adv['resultSets'][1]['rowSet'][team][21],
                adv['resultSets'][1]['rowSet'][team][25],
            ]

    with open(os.path.join(game_path, 'misc.json')) as f:
        misc = json.load(f)

        # figure out home / away indexes
        if misc['resultSets'][1]['rowSet'][0][1] == away_id:
            team_idx = [0, 1]
        else:
            team_idx = [1, 0]

        for team in team_idx:
            data += misc['resultSets'][1]['rowSet'][team][6:10]

    with open(os.path.join(game_path, 'tracking.json')) as f:
        tracking = json.load(f)

        # figure out home / away indexes
        if tracking['resultSets'][1]['rowSet'][0][1] == away_id:
            team_idx = [0, 1]
        else:
            team_idx = [1, 0]

        for team in team_idx:
            data += tracking['resultSets'][1]['rowSet'][team][6:10]
            data += tracking['resultSets'][1]['rowSet'][team][10:11]
            data.append(tracking['resultSets'][1]['rowSet'][team][13])
            data += tracking['resultSets'][1]['rowSet'][team][15:17]
            data += tracking['resultSets'][1]['rowSet'][team][18:20]

    data.append(home_win)
    return data


def process_season(season_id):
    src = os.path.join(RAW_DATA, 'games', season_id)
    dest = os.path.join(PROC_DATA, 'games', season_id[1:] + '-full.csv')

    with open(dest, 'w') as f:
        writer = csv.writer(f)

        writer.writerow(HEADERS)

        for game_id in tqdm(os.listdir(src)):
            writer.writerow([
                game_id,
                *process_game(os.path.join(src, game_id))
            ])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception('Must supply season code (22013 etc)')

    process_season(sys.argv[1])
