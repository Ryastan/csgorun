from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import InvalidSessionIdException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from fake_useragent import UserAgent

import random
import urllib3
import os
import sys
import time
import configparser
import requests
import traceback


class ScriptMain:
    def __init__(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        dir_path = os.getcwd()
        self.config = configparser.ConfigParser()
        self.config.read(f"{dir_path}\\config.ini")
        self.url = self.config["SETTINGS"]["url"]
        self.x = self.config["SETTINGS"]["x"]
        self.visible = self.config["SETTINGS"]["visible"]
        self.auth_status = self.config["SETTINGS"]["auth"]
        self.crashes = requests.get("https://api.csgorun.pro/current-state?montaznayaPena=null").json()
        self.last_crash = self.crashes['data']['game']['history'][0]
        self.last_crash_id = self.last_crash['id']
        self.count = 0
        self.last_crash = ''

        with open('proxies.txt') as proxies:
            self.proxy = random.choice(proxies.readlines()).strip()

        ua = UserAgent()
        self.options = Options()
        self.options.add_argument(f"user-agent={ua.chrome}")
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--start-maximized')
        self.options.add_argument('--ignore-certificate-errors-spki-list')

        self.options.add_argument(f"user-data-dir={dir_path}\\Default")

        if self.visible == '0':
            self.options.add_argument('--headless')

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), chrome_options=self.options)

    def start(self):
        self.driver.get(url=self.url)
        time.sleep(2)
        self.pick_items()
        # self.x_sln = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[2]/div[2]/div[1]/div[2]/div/div[3]/label/input')
        # self.items_sln = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[2]/div[1]/div[2]/div/div[1]/label/div')
        # self.btn_sln = self.driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[2]/div[2]/div[1]/div[2]/div/div[3]/div/button')
        
        while True:
            status = self.check_crashes()
            if status == "triple":
                self.play(status)
            elif status == "quadro":
                self.play(status)
                self.pick_items()

    def auth(self):
        self.driver.get(url=self.url)

        while True:
            try:
                _ = self.driver.window_handles
            except InvalidSessionIdException as e:
                break
            time.sleep(1)

    def save_new_crash(self, crash):
        last_crash_x = self.crashes['data']['game']['history'][0]['crash']
        last_crash_id = self.crashes['data']['game']['history'][0]['id']
        self.last_crash = crash
        output = f"\n{last_crash_x}x IT WAS {crash} ID:{last_crash_id} TIME:{datetime.now()}"

        with open('crash_log.txt', 'a') as file:
            file.write(output)
    
    def play(self, status):
        x = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[2]/div[2]/div[1]/div[2]/div/div[3]/label/input')
        x.click()
        x.send_keys(Keys.CONTROL + "a")
        x.send_keys(Keys.BACK_SPACE)
        x.send_keys(self.x)

        if status == 'triple':
            item = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[2]/div[1]/div[2]/div/div[2]/div/button[2]')
            item.click()
        elif status == 'quadro':
            item = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[2]/div[1]/div[2]/div/div[2]/div/button[1]')
            item.click()

        btn = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[2]/div[2]/div[1]/div[2]/div/div[3]/div/button')
        btn.click()

    def check_crashes(self):
        try:
            self.crashes = requests.get("https://api.csgorun.pro/current-state?montaznayaPena=null", verify=False, timeout=2, proxies=self.proxy).json()
        except requests.exceptions.ReadTimeout:
            with open('proxies.txt') as proxies:
                self.proxy = random.choice(proxies.readlines()).strip()

        self.last_crash = self.crashes['data']['game']['history'][0]
        self.last_crash_x = self.last_crash['crash']

        if self.last_crash_id != self.last_crash['id']:
            self.last_crash_id = self.last_crash['id']
            if float(self.last_crash_x) < 1.2:
                self.count += 1
                if self.count == 1:
                    print('Crash')
                elif self.count == 2:
                    print('Double')
                elif self.count == 3:
                    print('Triple!')
                    self.save_new_crash('triple')
                    return "triple"
                elif self.count == 4:
                    print("QUADRO CRASH!!!!!!!!")
                    self.save_new_crash('quadro')
                    return "quadro"
            elif float(self.last_crash_x) > 1.2 and self.count == 3:
                self.pick_items()
                self.count = 0
            else:
                self.count = 0


    def pick_items(self):
        items = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[2]/div[1]/div[2]/div/div[1]/label/div')
        items.click()

        x = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[2]/div[1]/div[2]/div/div[3]/button[1]')
        x.click()

        bank = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[1]/div[2]/div/div[2]/div[1]/div/div[1]/div[2]')
        time.sleep(2)
        low_bank = round(float((bank.text[0:-2])) * 0.16, 2)

        input_amount = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[1]/div[2]/div/div[2]/div[2]/label[3]/input')
        input_amount.send_keys(low_bank)

        time.sleep(3)
        pick_item = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[1]/div[2]/div/div[2]/div[3]/button[1]')
        pick_item.click()

        confirm = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[1]/div[2]/div/div[2]/div[1]/button')
        confirm.click()

        x.click()
        time.sleep(1)
        x.click()
        time.sleep(3)
        pick_item = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[1]/div[2]/div/div[2]/div[3]/button[1]')
        pick_item.click()
        time.sleep(1)
        confirm = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[1]/div[2]/div/div[2]/div[1]/button')
        confirm.click()
        time.sleep(1)
        x.click()


if __name__ == '__main__':
    csgorun = ScriptMain()
    if csgorun.auth_status == "1":
        csgorun.auth()
    elif csgorun.auth_status == "0":
        csgorun.start()