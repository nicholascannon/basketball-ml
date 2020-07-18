#!/usr/bin/env python
"""
Process raw season data.

Written by Nicholas Cannon
"""
import os
import pathlib
from tqdm import tqdm
import ijson
import csv

DATA_DIR = os.path.join(pathlib.Path().absolute(), 'data')
RAW_DATA = os.path.join(DATA_DIR, 'raw', 'season')
PROC_DATA = os.path.join(DATA_DIR, 'processed', 'season')


def process_season(season_file):
    """
    Extract season id and game id from raw season data.
    """
    src_path = os.path.join(RAW_DATA, season_file)

    with open(src_path, 'rb') as src:
        # get season id for dest file
        season_id = list(ijson.items(src, 'resultSets.item.rowSet.item'))[0][0]
        src.seek(0)
        dest_path = os.path.join(PROC_DATA, season_id + '.csv')

        with open(dest_path, 'w') as dest:
            games = ijson.items(src, 'resultSets.item.rowSet.item')
            writer = csv.writer(dest)

            writer.writerow(['season_id', 'game_id'])

            # stream game data from json file
            for game in games:
                writer.writerow([game[0], game[4]])


if __name__ == "__main__":
    for dir in tqdm(os.listdir(RAW_DATA)):
        process_season(dir)
