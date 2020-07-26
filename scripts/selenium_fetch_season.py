#!/usr/bin/env python
import os
import pathlib
import csv
from dotenv import load_dotenv
from tqdm import tqdm
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

CHROME_DRIVER = os.environ['CHROME_DRIVER']
DATA_DIR = os.path.join(pathlib.Path().absolute(), 'data')
RAW_DATA = os.path.join(DATA_DIR, 'raw')
PROC_DATA = os.path.join(DATA_DIR, 'processed')
BOX_SCORE_URLS = [
    ('https://stats.nba.com/game/{}/', 'traditional.html'),
    ('https://stats.nba.com/game/{}/advanced/', 'advanced.html'),
    ('https://stats.nba.com/game/{}/misc/', 'misc.html'),
    ('https://stats.nba.com/game/{}/scoring/', 'scoring.html'),
    ('https://stats.nba.com/game/{}/four-factors/', 'four-factors.html'),
    ('https://stats.nba.com/game/{}/tracking/', 'player-tracking.html'),
]

TABLE1_XPATH = '/html/body/main/div[2]/div/div/div[4]/div/div[2]/div/nba-stat-table[1]/div[2]/div[1]/table'
TABLE2_XPATH = '/html/body/main/div[2]/div/div/div[4]/div/div[2]/div/nba-stat-table[2]/div[2]/div[1]/table'


def process_game(game_id, season_dir, driver):
    """
    Get individual games raw data from box score urls.
    """
    game_dir = os.path.join(season_dir, game_id)
    if not os.path.exists(game_dir):
        os.mkdir(game_dir)
    else:
        # game dir exists, check if it can be skipped
        game_files = os.listdir(game_dir)
        for _, page in BOX_SCORE_URLS:
            if page not in game_files:
                break
        else:
            return  # can skip this game!!

    for url, page in BOX_SCORE_URLS:
        url = url.format(game_id)
        driver.get(url)

        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, TABLE1_XPATH)))
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, TABLE2_XPATH)))

        boxscore = driver.execute_script(
            "return document.getElementsByClassName('stats-boxscore-page')[0].innerHTML")

        with open(os.path.join(game_dir, page), 'w') as f:
            f.write(boxscore)


def process_season(season, driver):
    """
    Set up season csv file and process each game.
    """
    src_path = os.path.join(PROC_DATA, 'season', season + '.csv')
    season_dir = os.path.join(RAW_DATA, 'games', season)
    if not os.path.exists(season_dir):
        os.mkdir(season_dir)

    with open(src_path, 'r') as src:
        games = csv.reader(src)
        next(games)  # skip headers

        for season_id, game_id in tqdm(games, total=2460):
            try:
                process_game(game_id, season_dir, driver)
            except Exception:
                print('Errored at game {}'.format(game_id))


def main():
    if len(sys.argv) < 1:
        raise Error('Invalid args')

    options = Options()
    options.add_argument('--headless')
    options.add_argument('disable-blink-features=AutomationControlled')
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36')
    driver = webdriver.Chrome(
        executable_path=CHROME_DRIVER, options=options)

    with driver as d:
        process_season(sys.argv[1], d)


if __name__ == "__main__":
    main()
