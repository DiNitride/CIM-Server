import hashlib


while True:
    passwd = input()
    passwd = hashlib.sha256(passwd.encode()).hexdigest()
    print(passwd)