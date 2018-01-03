
class User:

    def __init__(self, usr, passwd, permlvl):
        self.usr = usr
        self.passwd = passwd
        self.permlvl = permlvl

    def __str__(self):
        return f"User: {self.usr}"
