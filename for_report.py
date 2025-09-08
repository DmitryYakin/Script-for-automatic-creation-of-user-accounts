import pandas
import pandas as pd


input = pd.read_csv('Приморский.csv')

output = []

for i, row in input.iterrows():
    output.append({'MO': ' '.join([row['surname'], row['name'], row['patronymic'], row['email'], row['position'], row['org']]),
                   'region': row['region'],
                   'MIS': 'ЕЦП',
                   'login': row['username'],
                   'password': row['password'],
                   'date': '16.07.2025',
                   'user': 'Якин Д.М.'
                   })

pd.DataFrame(output).to_csv('report.csv')