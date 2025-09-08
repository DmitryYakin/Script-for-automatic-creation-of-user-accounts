import secrets
import string
import re


# generate a simple n letter password

n = 12
alphabet = string.ascii_letters + string.digits + string.punctuation
alphabet = re.sub(r'@|\(|\)|\'|\|,|;"', '', alphabet)

print(''.join([secrets.choice(alphabet) for i in range(n)]))
