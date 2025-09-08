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
perms = {'requestperms': ['Врач'],
         'frontsections': ['DHRA Аналитика',
                           'DHRA Просмотр всех запросов МО',
                           # 'DHRA Просмотр всех запросов региона',
                           'DHRA Статистика']}


# Is needed to make sure that page has loaded
def waitUntil(browser, title, delay=.5):
    t = 0
    while True:
        if t > 10:
            print('Debug: Waited too long')
            exit(1)
        time.sleep(delay)
        if title in browser.title:
            break
        t+= delay

def waitUntilNot(browser, title, delay=.5):
    t = 0
    while True:
        if t > 10:
            print('Debug: Waited too long')
            exit(1)
        time.sleep(delay)
        if title not in browser.title:
            break
        t+= delay


def setSelect(browser, xpath, value):
    s = Select(browser.find_element(By.XPATH, xpath))
    s.select_by_value(value)


# Region selector is weird, god help me
def selectReion(browser, region):
    elem = browser.find_element(By.XPATH, '//span[@id="select2-id_region-container"]')
    elem.click()


    time.sleep(.1)
    elem = browser.find_element(By.XPATH, '/html/body/span/span/span[1]/input')
    elem.send_keys(region)

    time.sleep(.69)

    elem = browser.find_element(By.XPATH, '//ul[@id="select2-id_region-results"]')
    for opt in elem.find_elements(By.TAG_NAME, 'li'):
        if opt.text == region:
            time.sleep(.07)
            opt.click()
            time.sleep(.07)
            # browser.find_element(By.XPATH, '//span[@id="select2-id_region-container"]').click()
            return True
    print('Weird region name!')

    for opt in elem.find_elements(By.TAG_NAME, 'li'):
        if region in opt.text:
            opt.click()
            return True

    time.sleep(.1)
    return False


# Gets values from current session to reuse
def getValues(browser):
    data = {}
    data['region'] = browser.find_element(By.ID, 'select2-id_region-container').text
    # data['hospitalid'] = browser.find_element(By.XPATH, '//select[@id="id_hospital_id"]').get_attribute('value')
    data['his'] = browser.find_element(By.XPATH,'//select[@id="id_his"]').get_attribute('value')

    print(data)

    return data


# Reuse data
def setValues(browser, data):
    time.sleep(.0999)
    # setSelect(browser, '//select[@id="id_hospital_id"]', data['hospitalid'])
    setSelect(browser, '//select[@id="id_his"]', data['his'])
    selectReion(browser, data['region'])


# Set default permissions
def setPerms(browser):
    browser.find_element(By.XPATH, '//*[@id="fieldsetcollapser2"]').click()

    time.sleep(.3)

    elems = browser.find_element(By.XPATH, '//select[@id="id_request_permission_groups_from"]').find_elements(By.TAG_NAME, 'option')
    # print(len(elems))
    for opt in elems:
        try:
            if opt.get_attribute('title') in perms['requestperms']:
                opt.click()
                time.sleep(.1)
        except:
            print('Debug: wrong option')
    time.sleep(.3)
    browser.find_element(By.XPATH, '//*[@id="id_request_permission_groups_add_link"]').click()

    time.sleep(.3)

    elems = browser.find_element(By.XPATH, '//select[@id="id_frontend_sections_from"]').find_elements(By.TAG_NAME, 'option')
    for opt in elems:
        try:
            if opt.get_attribute('title') in perms['frontsections']:
                opt.click()
                time.sleep(.3)
        except:
            print('Debug: wrong option 2')
    browser.find_element(By.XPATH, '//*[@id="id_frontend_sections_add_link"]').click()


# Superuser auth
def login(browser):
    creds = pd.read_csv('creds.csv').loc[0]
    waitUntil(browser, 'Войти')
    browser.find_element(By.XPATH, '//*[@id="id_username"]').send_keys(creds['username'])
    browser.find_element(By.XPATH, '//*[@id="id_password"]').send_keys(creds['password'] + Keys.RETURN)


# Create user
def addUser(browser, username, password):
    waitUntil(browser, 'Добавить Пользователь')

    browser.find_element(By.XPATH, '//*[@id="id_username"]').send_keys(username)
    browser.find_element(By.XPATH, '//*[@id="id_password1"]').send_keys(password)
    browser.find_element(By.XPATH, '//*[@id="id_password2"]').send_keys(password + Keys.RETURN)

    time.sleep(3)
    if 'Пользователь с таким логином уже существует' in browser.page_source:
        return False


    waitUntilNot(browser, 'Добавить Пользователь')
    if 'Изменить Пользователь' in browser.title:
        print('added user', username)
        return True
    elif len(browser.find_elements(By.XPATH, "//li[contains(text(),'Пользователь с таким логином уже существует')]")) == 0:
        return False
    else:
        # input('ok?')
        return False


# Selects medical organization by matching substring, might cause errors
x = '0' # МО не указана
def selectOrg(browser, org):
    global x
    print(x)
    opts = browser.find_element(By.ID, 'id_hospital_id').find_elements(By.TAG_NAME, 'option')
    for opt in opts:
        try:
            if org.lower() in opt.text.lower():
                opt.click()
                x = opt.get_attribute('value')
                return True
        except:
            print('Debug: bad org')

    setSelect(browser, '//*[@id="id_hospital_id"]', x) # try to use previous good MO value
    print(f'Debug: Couldn`t find org: {org}')
    return False


# Modify user
def customizeUser(browser, user, data):
    #waitUntil(browser, 'Изменить Пользователь')

    errors = ''

    time.sleep(1)
    browser.find_element(By.XPATH, '//*[@id="id_first_name"]').send_keys(user['name'])
    browser.find_element(By.XPATH, '//*[@id="id_last_name"]').send_keys(user['surname'])
    browser.find_element(By.XPATH, '//*[@id="id_second_name"]').send_keys(user['patronymic'])
    browser.find_element(By.XPATH, '//*[@id="id_email"]').send_keys(user['email'])

    time.sleep(.1)

    browser.find_element(By.XPATH, '//*[@id="id_is_privacy_policy_consent"]').click()

    time.sleep(.5)

    setPerms(browser)

    time.sleep(.4)

    if not selectOrg(browser, user['org_short']):
        errors += ' org'

    time.sleep(.1)
    if not data:
        # input("Please select region and HIS, then press enter")
        while True:
            res = askquestion('Вопрос', 'Поля МИС и Регион заполнены?')
            if res == 'yes':
                break
        data = getValues(browser)
    else:
        # browser.find_element(By.XPATH, '//*[ @ id = "fieldsetcollapser3"]').click()
        try:
            setValues(browser, data)
        except:
            while True:
                res = askquestion('Ошибка', 'Поля МИС и Регион заполнены?')
                if res == 'yes':
                    break

    # print('input please!')
    print('set user', user['username'])
    return errors, data

########################################################################################################################

if __name__ == '__main__':

    Tk().withdraw()

    fullPath = askopenfilename()
    path = '/'.join(fullPath.split('/')[:-1])

    users = pd.read_csv(fullPath)

    browser = webdriver.Firefox()
    browser.get(f'{url}/gate/control/accounts/customuser/add/')
    waitUntil(browser, "Войти")

    login(browser)
    time.sleep(.75)
    errors = []

    data = {}

    print(users)

    for i, user in users.iterrows():
        e = ''
        if addUser(browser, user['username'], user['password']):
            e, data = customizeUser(browser, user, data)
            time.sleep(.1)
            browser.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/form/div/div[3]/input[1]').click() # Save
        else:
            user = user.to_dict()
            user['errors'] = 'username collision'
            errors.append(user)
            print(user)
        if len(e) > 0:
            user = user.to_dict()
            user['errors'] = e
            errors.append(user)
            print(user)

        time.sleep(.1)
        browser.get(f'{url}/gate/control/accounts/customuser/add/')
        time.sleep(.1)
    # Collect all problematic users for correction
    if errors:
        df = pd.DataFrame(errors)
        df.to_csv(path + '/' + 'rejects.csv')
