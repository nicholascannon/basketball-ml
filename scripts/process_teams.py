#!/usr/bin/env python
import os
import pathlib
import pandas as pd
import numpy as np
from tqdm import tqdm


GAME_DIR = os.path.join(pathlib.Path().absolute(),
                        'data', 'processed', 'games')
TEAM_DIR = os.path.join(pathlib.Path().absolute(),
                        'data', 'processed', 'teams')


def process_teams():
    # concatenate all seasons and sort by date
    seasons = pd.DataFrame()
    for season_id in os.listdir(GAME_DIR):
        s_df = pd.read_csv(os.path.join(GAME_DIR, season_id),
                           parse_dates=['DATE'], dtype={'GAME_ID': str})
        seasons = pd.concat([seasons, s_df])

    # fix float error in cols
    pct_cols = seasons.select_dtypes(include=np.float).columns
    seasons[pct_cols] = seasons[pct_cols].round(3)

    # prep stuff
    home_cols = [col for col in seasons.columns if col[:2] == 'H_']
    away_cols = [col for col in seasons.columns if col[:2] == 'A_']
    non_feature_cols = ['GAME_ID', 'DATE', 'SEASON', 'TEAM', 'OPPONENT', 'WON']

    # df rename maps
    away_rename = {hdr: hdr[2:] for hdr in away_cols}
    home_rename = {hdr: hdr[2:] for hdr in home_cols}

    for team_id in tqdm(seasons['A_ID'].unique()):
        # process away games
        away_games = seasons[seasons['A_ID'] == team_id].copy()
        away_games['HOME'] = 0

        # basic stats against this team
        away_games['PTS_A'] = away_games['H_PTS']
        away_games['REB_A'] = away_games['H_REB']
        away_games['AST_A'] = away_games['H_AST']
        away_games['STL_A'] = away_games['H_STL']
        away_games['BLK_A'] = away_games['H_BLK']

        away_games['WON'] = 1 - away_games['HOME_WIN']  # flip the label!
        away_games['TEAM'] = away_games['A_ID']
        away_games['OPPONENT'] = away_games['H_ID']

        # rename and remove
        away_games.rename(columns=away_rename, inplace=True)
        away_games.drop(columns=['HOME_WIN', 'ID', *home_cols], inplace=True)

        # process home games
        home_games = seasons[seasons['H_ID'] == team_id].copy()
        home_games['HOME'] = 1

        # basic stats against this team
        home_games['PTS_A'] = home_games['A_PTS']
        home_games['REB_A'] = home_games['A_REB']
        home_games['AST_A'] = home_games['A_AST']
        home_games['STL_A'] = home_games['A_STL']
        home_games['BLK_A'] = home_games['A_BLK']

        home_games['WON'] = home_games['HOME_WIN']
        home_games['TEAM'] = home_games['H_ID']
        home_games['OPPONENT'] = home_games['A_ID']

        # rename and remove
        home_games.rename(columns=home_rename, inplace=True)
        home_games.drop(columns=['HOME_WIN', 'ID', *away_cols], inplace=True)

        # concat, sort by date, rearrange cols and write to csv
        team = pd.concat([away_games, home_games])
        team.sort_values(by='DATE', inplace=True)
        team = team[
            list(team.columns[:3]) +
            list(team.columns[-2:]) +
            list(team.columns[3:-2])
        ]
        team.to_csv(os.path.join(
            TEAM_DIR, '{}.csv'.format(team_id)), index=False)


if __name__ == "__main__":
    process_teams()
