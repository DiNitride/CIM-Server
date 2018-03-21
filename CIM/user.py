
class User:
    """
    Base class to represent a connected user
    """

    def __init__(self, usr, passwd, permlvl):
        """
        Constructor defining attributes for user
        """
        self.usr = usr
        self.passwd = passwd
        self.permlvl = permlvl

    def __str__(self):
        """
        Internal Python method that is called when an instance of the class is printed to the console
        """
        return self.usr
