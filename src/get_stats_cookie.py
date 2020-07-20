#!/usr/bin/env python
import os
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()
CHROME_DRIVER = os.environ['CHROME_DRIVER']

if __name__ == "__main__":
    options = Options()
    options.add_argument('--headless')
    options.add_argument('disable-blink-features=AutomationControlled')
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36')
    driver = webdriver.Chrome(
        executable_path=CHROME_DRIVER, options=options)

    with driver as d:
        driver.get('https://stats.nba.com/game/0021900969/')

        cookies = driver.execute_script("return document.cookie")
        print(cookies)
