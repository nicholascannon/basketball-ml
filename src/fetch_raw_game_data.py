#!/usr/bin/env python
import os
import pathlib
import sys
import requests
import csv
from tqdm import tqdm
from dotenv import load_dotenv
from http.cookies import SimpleCookie

load_dotenv()

DATA_DIR = os.path.join(pathlib.Path().absolute(), 'data')
LOG_DIR = os.path.join(pathlib.Path().absolute(), 'logs')
RAW_DATA = os.path.join(DATA_DIR, 'raw')
PROC_DATA = os.path.join(DATA_DIR, 'processed')
GAME_TOTAL = 1230
REQUESTS = [
    ('/boxscoreadvancedv2', 'advanced.json'),
    ('/boxscoresummaryv2', 'boxscore-summary.json'),
    ('/boxscorefourfactorsv2', 'four-factors.json'),
    ('/boxscoremiscv2', 'misc.json'),
    ('/boxscorescoringv2', 'scoring.json'),
    ('/boxscoreplayertrackv2', 'tracking.json'),
    ('/boxscoretraditionalv2', 'traditional.json'),
]
SEASON_MAP = {
    '22013': '2013-14',
    '22014': '2014-15',
    '22015': '2015-16',
    '22016': '2016-17',
    '22017': '2017-18',
    '22018': '2018-19',
}

# setup cookie
cookie = SimpleCookie()
cookie.load(os.environ.get('STATS_COOKIE'))
STATS_COOKIE = {}
for key, morsel in cookie.items():
    STATS_COOKIE[key] = morsel.value


def process_game(game_id, season_dir, season_id):
    game_dir = os.path.join(season_dir, game_id)
    if not os.path.exists(game_dir):
        os.mkdir(game_dir)
    else:
        # game dir exists, check if it can be skipped
        game_files = os.listdir(game_dir)
        for _, file in REQUESTS:
            if file not in game_files:
                break  # incomplete files in game directory
        else:
            return  # can skip this game!!

    for url, file in REQUESTS:
        params = {'GameID': game_id}

        # add extra url params if not getting summary
        if file != 'boxscore-summary.json':
            params['EndPeriod'] = 10
            params['EndRange'] = 31800
            params['RangeType'] = 0
            params['Season'] = SEASON_MAP[season_id]
            params['SeasonType'] = 'Regular Season'
            params['StartPeriod'] = 1
            params['StartRange'] = 0

        r = requests.get(
            'https://stats.nba.com/stats' + url,
            headers={
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'x-nba-stats-origin': 'stats',
                'x-nba-stats-token': 'true',
                'X-NewRelic-ID': 'VQECWF5UChAHUlNTBwgBVw==',
                'Referer': 'https://stats.nba.com/game/{}/tracking/'.format(game_id),
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
            },
            params=params,
            cookies=STATS_COOKIE,
            timeout=10
        )
        r.raise_for_status()
        r.json()  # validate we have json data

        with open(os.path.join(game_dir, file), 'w') as f:
            f.write(r.text)


def process_season(season):
    log_path = os.path.join(LOG_DIR, season + '.error')
    src_path = os.path.join(PROC_DATA, 'season', season + '.csv')
    season_dir = os.path.join(RAW_DATA, 'games', season)

    if not os.path.exists(season_dir):
        os.mkdir(season_dir)

    with open(src_path, 'r') as src:
        games = csv.reader(src)
        next(games)  # skip headers

        for season_id, game_id in tqdm(games, total=GAME_TOTAL):
            try:
                process_game(game_id, season_dir, season)
            except Exception as e:
                with open(log_path, 'w') as err:
                    err.write(game_id + '\n')

                break  # will have to break to reset stats cookie


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception('Must supply season code (22013 etc)')

    process_season(sys.argv[1])
