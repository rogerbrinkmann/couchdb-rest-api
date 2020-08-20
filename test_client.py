import sys
import pprint
from couch import Server

if len(sys.argv) == 3:
    username = sys.argv[1]
    password = sys.argv[2]


server = Server(username, password)
print(server.info())

print(server.active_tasks())

# delete all user databases
dbs = server.all_dbs()
for db in dbs:
    if db.name not in ["_replicator", "_users"]:
        print(server.delete_database(db.name))

server.create_database("test-db")

all_dbs = server.all_dbs()
all_db_names = [db.name for db in all_dbs]

print(server.dbs_info(all_db_names))

print(server.cluster_setup())

