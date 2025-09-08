import time
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import askquestion, showinfo

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

url = 'https://cloud.webiomed.ru'
perms = {
    'requestperms': ['Врач'],
    'frontsections': ['DHRA Аналитика', 'DHRA Просмотр всех запросов МО', 'DHRA Статистика']
}

def waitUntil(browser, title, delay=.5):
    t = 0
    while True:
        if t > 20:
            print('Debug: Waited too long')
            exit(1)
        time.sleep(delay)
        if title in browser.title:
            break
        t += delay

def waitUntilNot(browser, title, delay=.5):
    t = 0
    while True:
        if t > 20:
            print('Debug: Waited too long')
            exit(1)
        time.sleep(delay)
        if title not in browser.title:
            break
        t += delay

def selectRegion(browser, full_region_name):
    print(f"➡️ Начинаю выбор региона: {full_region_name}")

    # Убираем " - код XX", если есть
    if " - код" in full_region_name:
        region_name = full_region_name.split(" - код")[0].strip()
    else:
        region_name = full_region_name.strip()

    try:
        print(f"🔍 Пытаюсь выбрать регион по: {region_name}")
        region_dropdown = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.ID, "select2-id_region-container"))
        )
        region_dropdown.click()
        time.sleep(0.3)

        search_input = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "select2-search__field"))
        )
        search_input.clear()

        for char in region_name:
            search_input.send_keys(char)
            browser.execute_script("""
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new KeyboardEvent('keyup', { bubbles: true }));
            """, search_input)
            time.sleep(0.4)

        time.sleep(1.5)  # Увеличено ожидание на подгрузку списка

        options = browser.find_elements(By.XPATH, '//li[contains(@class, "select2-results__option")]')
        for opt in options:
            text = opt.text.strip()
            print(f"[вариант]: {text}")
            if region_name.lower() in text.lower():
                print(f"✅ Найден вариант: {text}")
                ActionChains(browser).move_to_element(opt).click().perform()
                time.sleep(0.5)
                return True

        print(f"❌ Не удалось найти регион по: {region_name}")
        browser.save_screenshot(f'region_not_found_{region_name}.png')
        return False

    except Exception as e:
        print(f"💥 Ошибка при выборе региона: {e}")
        browser.save_screenshot(f'region_error_{region_name}.png')
        return False


def getValues(browser):
    data = {}
    data['region'] = browser.find_element(By.ID, 'select2-id_region-container').text
    data['his'] = browser.find_element(By.XPATH, '//select[@id="id_his"]').get_attribute('value')
    print(data)
    return data

def setSelect(browser, xpath, value):
    s = Select(browser.find_element(By.XPATH, xpath))
    s.select_by_value(value)

def setValues(browser, data):
    if data:
        time.sleep(3)
        selectRegion(browser, data['region'])
        time.sleep(3)
        setSelect(browser, '//select[@id="id_his"]', data['his'])

def setPerms(browser):
    browser.find_element(By.XPATH, '//*[@id="fieldsetcollapser2"]').click()
    time.sleep(.3)

    elems = browser.find_element(By.XPATH, '//select[@id="id_request_permission_groups_from"]').find_elements(By.TAG_NAME, 'option')
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

def login(browser):
    creds = pd.read_csv('creds.csv').loc[0]
    waitUntil(browser, 'Войти')
    browser.find_element(By.XPATH, '//*[@id="id_username"]').send_keys(creds['username'])
    browser.find_element(By.XPATH, '//*[@id="id_password"]').send_keys(creds['password'] + Keys.RETURN)

def addUser(browser, username, password):
    time.sleep(2)
    waitUntil(browser, 'Добавить Пользователь')
    time.sleep(2)
    browser.find_element(By.XPATH, '//*[@id="id_username"]').send_keys(username)
    browser.find_element(By.XPATH, '//*[@id="id_password1"]').send_keys(password)
    browser.find_element(By.XPATH, '//*[@id="id_password2"]').send_keys(password + Keys.RETURN)

    time.sleep(3)
    if 'Пользователь с таким логином уже существует' in browser.page_source:
        return False

    waitUntilNot(browser, 'Добавить Пользователь')
    if 'Изменить Пользователь' in browser.title:
        print('✅ Пользователь добавлен:', username)
        return True
    else:
        return False

def selectOrg(browser, org):
    opts = browser.find_element(By.ID, 'id_hospital_id').find_elements(By.TAG_NAME, 'option')
    for opt in opts:
        try:
            if org.lower() in opt.text.lower():
                opt.click()
                return True
        except:
            print('Debug: bad org')
    print(f'Debug: Организация не найдена: {org}')
    return False

def customizeUser(browser, user, data):
    time.sleep(1)
    browser.find_element(By.XPATH, '//*[@id="id_first_name"]').send_keys(user['name'])
    browser.find_element(By.XPATH, '//*[@id="id_last_name"]').send_keys(user['surname'])
    browser.find_element(By.XPATH, '//*[@id="id_second_name"]').send_keys(user['patronymic'])
    browser.find_element(By.XPATH, '//*[@id="id_email"]').send_keys(user['email'])

    browser.find_element(By.XPATH, '//*[@id="id_is_privacy_policy_consent"]').click()
    time.sleep(.5)

    setPerms(browser)
    time.sleep(.4)

    setValues(browser, data)
    time.sleep(.1)

    if data is None:
        showinfo('Настройка', 'Пожалуйста, выберите регион и МИС вручную')
        while True:
            res = askquestion('Подтверждение', 'Вы выбрали регион и МИС?')
            if res == 'yes':
                break
        data = getValues(browser)

    errors = ''
    if not selectOrg(browser, user['org_short']):
        errors += ' org'

    print('✅ Настроен пользователь:', user['username'])
    return errors, data

if __name__ == '__main__':
    Tk().withdraw()
    fullPath = askopenfilename()
    path = '/'.join(fullPath.split('/')[:-1])

    users = pd.read_csv(fullPath)
    browser = webdriver.Firefox()
    browser.get(f'{url}/gate/control/accounts/customuser/add/')
    waitUntil(browser, "Войти")

    login(browser)
    time.sleep(.95)
    errors = []

    data = None

    for i, user in users.iterrows():
        e = ''
        if addUser(browser, user['username'], user['password']):
            e, data = customizeUser(browser, user, data)
            time.sleep(.1)
            browser.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/form/div/div[3]/input[1]').click()  # Сохранить
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

    if errors:
        df = pd.DataFrame(errors)
        df.to_csv(path + '/' + 'rejects.csv')
