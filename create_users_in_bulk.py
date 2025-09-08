import pandas as pd
import secrets
import string
import re
# from passlib.hash import pbkdf2_sha256
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Custom pbkdf2
#PBKDF2PasswordHasher.salt_entropy = 120

# Alphabet for password generation
alphabetPassword = string.ascii_letters + string.digits + string.punctuation
# Replace "bad" symbols
alphabetPassword = re.sub(r'@|\(|\)|\'|\|,|;"', '', alphabetPassword)

# Dictionary for trasliteration
slovar = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
          'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
          'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h',
          'ц': 'c', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e',
          'ю': 'u', 'я': 'ya', 'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'YO',
          'Ж': 'ZH', 'З': 'Z', 'И': 'I', 'Й': 'I', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
          'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H',
          'Ц': 'C', 'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SCH', 'Ъ': '', 'Ы': 'y', 'Ь': '', 'Э': 'E',
          'Ю': 'U', 'Я': 'YA', ',': '', '?': '', ' ': '_', '~': '', '!': '', '@': '', '#': '',
          '$': '', '%': '', '^': '', '&': '', '*': '', '(': '', ')': '', '-': '', '=': '', '+': '',
          ':': '', ';': '', '<': '', '>': '', '\'': '', '"': '', '\\': '', '/': '', '№': '',
          '[': '', ']': '', '{': '', '}': '', 'ґ': '', 'ї': '', 'є': '', 'Ґ': 'g', 'Ї': 'i',
          'Є': 'e', '—': ''}

#For collision detection
usernames = []
def genPass(n=10):
    return ''.join(secrets.choice(alphabetPassword) for i in range(n))


def transliterate(name):
    for key in slovar:
        name = name.replace(key, slovar[key])
    return name

def generateUser(name,
                 surname,
                 patronymic,
                 #email,
                 region,
                 # maxLen=0,
                 ending=0):
    print(name, surname)
    # login = transliterate('_'.join([region, name, surname]))
    login = transliterate(f'{region}_{name[0]}{surname}')

    i = 1
    while login in usernames:
        end = str(i)
        if i == 1:
            login += end
        login = login[:-len(end)] + end
        i += 1

    usernames.append(login)

    password = genPass()
    # Trim login
    # if maxLen > 0:
    #     login = login[:maxLen-1-ending]

    # Add ending to avoid potential collision
    if ending > 0:
        login += '_' + ''.join(secrets.choice(string.digits) for i in range(ending))

    return (login.lower( ), password)


def parseFile1(path, region):
    people = pd.read_excel(path)
    people.dropna(how='any')  # Fix excel bullshit, doesn`t work

    print('People', len(people))
    people = people.drop_duplicates(subset=['full_name', 'MO'], keep='last')
    print('No dupes', len(people))

    parsedPeople = []
    for i, person in people.iterrows():
        if type(person['full_name']) == str and person['full_name'] != '':
            print(person['full_name'])
            fullName = re.sub('\n', ' ', person['full_name'])
            fullName = fullName.split(' ')
            parsedPeople.append({
                                 'surname': fullName[0],
                                 'name': fullName[1],
                                 'patronymic': fullName[2],
                                 'email': re.sub(r'\n| ', '', person['email']),   #fix formatting
                                 'position': re.sub(r'\\\n', ' ', person['position']),
                                 'org': re.sub(r'\n', ' ', person['MO']),
                                 # 'region': region
                                })


    return parsedPeople


def parseFile2(path, region):
    people = pd.read_excel(path)
    people.dropna(how='any')  # Fix excel bullshit, doesn`t work

    parsedPeople = []

    for i, person in people.iterrows():
        if True:
            # print(person)
            parsedPeople.append({
                'surname': person['surname'],
                'name': person['name'],
                'patronymic': person['patronymic'],
                'email': re.sub(r'\n| ', '', person['email']),  # fix formatting
                'position': re.sub(r'\\\n', ' ', person['position']),
                'org': re.sub(r'\n', ' ', person['MO']),
                # 'region': region
                })

    return parsedPeople


def parseFile(path, region):
    code = int(path.split('/')[-1].split('.')[0][0])
    print(path)
    print(code)

    if code == 1:
        return parseFile1(path, region)
    if code == 2:
        return parseFile2(path, region)

    print('Code invalid!')
    quit(1)


def getHospitalIDs(people):
    peopleDF = pd.DataFrame(people)
    orgDict = {}

    print(f'Enter code for hospitals')
    for org in peopleDF['org'].unique():
        id = int(input(f'{org}: '))
        orgDict[org] = id

    return orgDict

if __name__ == '__main__':
    # user = generateUser('Миролюбов',
    #                     "Арсений",
    #                     "Константинович",
    #                     #"example@karelia.ru",
    #                     'Карелия')
    # print(user)

    region = input('Enter region: ')
    # regionID = int(input("Enter region id: "))
    # hisID = int(input'Enter his(мис) id: ')

    users = []
    usersDB = []

    # Region specific
    # regionID = 19
    Tk().withdraw()
    fullPath = askopenfilename()
    path = '/'.join(fullPath.split('/')[:-1])

    # Parse all users from file

    people = parseFile(fullPath, region)

    # orgDict = getHospitalIDs(people)

    # print(orgDict)

    for person in people:
        login, password = generateUser(person['name'],
                                               person['surname'],
                                               person['patronymic'],
                                               region,
                                               # 10,
                                               # 4
                                               )

        person['username'] = login
        person['password'] = password

        org_short = ''

        try:
            org_short = re.search(r".*[\"|«](.*)[\"|»].*", person['org']).group(1)
        except:
            org_short = person['org']

        users.append(person)
        usersDB.append({'name': person['name'],
                        'surname': person['surname'],
                        'patronymic': person['patronymic'],
                        'username': login,
                        'password': password,
                        # 'last_name': person['surname'],
                        # 'first_name':  person['name'],
                        # 'second_name': person['patronymic'],
                        'email': person['email'],
                        # 'region_id': regionID,
                        # 'hospital_id': orgDict['org'],
                        # 'payment_rate_id': 1,
                        # 'his_id': hisID,
                        # 'is_staff': "true",
                        'position': person['position'],
                        'org': person['org'],
                        'org_short': org_short,
                        'region': region,
                        })

    # print(users)
    print(f'Collected {len(users)}, users')

    df = pd.DataFrame(users)
    df.to_csv(path + '/' + 'out.csv')

    df2 = pd.DataFrame(usersDB)

    df2.to_csv(path + '/' + f'{region}.csv')
