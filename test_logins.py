import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import askquestion

url = 'https://cloud.webiomed.ru'

def waitUntil(browser, t1, delay=.5):
    t = 0
    while True:
        if t > 10:
            print('Debug: Waited too long')
            exit(1)
        time.sleep(delay)
        if t1 in browser.title:
            return True
        t+= delay

def login(browser, creds):
    # creds = pd.read_csv('creds.csv').loc[0]
    waitUntil(browser, "Webiomed")
    time.sleep(3)
    browser.find_element(By.XPATH, '//*[@id="login"]').send_keys(creds['username'])
    browser.find_element(By.XPATH, '//*[@id="password"]').send_keys(creds['password'] + Keys.RETURN)


data = pd.read_csv('Приморский.csv')

browser = webdriver.Firefox()
browser.get(f'{url}')
waitUntil(browser, "Webiomed")

for i, user in data.iterrows():
    time.sleep(3)
    print(i, user['username'])
    login(browser, user)
    time.sleep(3)
    if 'Невозможно войти с предоставленными учетными данными.' in browser.page_source:
        print('Not OK')
        browser.refresh()
        time.sleep(.3)
    elif 'Аналитика' in browser.title:
        print('OK')
        browser.find_element(By.XPATH, '/html/body/div/header/nav/div/div/button').click()
        time.sleep(.4)
    else:
        print('Error')
        browser.refresh()
        time.sleep(.3)





