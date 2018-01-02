import CIM

db = CIM.utils.db

# serv = CIM.Server()

# serv.start()

db.new_user("James", "password", 3)
u = db.get_user("James")
print(u)
#db.del_user("James")

