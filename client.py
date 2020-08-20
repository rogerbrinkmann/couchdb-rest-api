import sys
import pprint
from couch import Server

if len(sys.argv) == 3:
    username = sys.argv[1]
    password = sys.argv[2]


server = Server(username, password)


# delete all user databases
dbs = server.all_dbs()
for db in dbs:
    if db.name not in ["_replicator", "_users"]:
        server.delete_database(db.name)

test_db = server.create_database("test-db")

persons = [
    {
        "firstname": "John",
        "lastname": "Doe",
        "age": 31,
        "address": {
            "city": "Frankfurt",
            "street": "Mainstreet",
            "housenumber": "34",
            "ZIP-Code": "12345",
        },
    },
    {
        "firstname": "Monika",
        "lastname": "Mustermann",
        "age": 32,
        "address": {
            "city": "Berlin",
            "street": "Highstreet",
            "housenumber": "36",
            "ZIP-Code": "67890",
        },
    },
    {
        "firstname": "James ",
        "lastname": "Jelly",
        "age": 33,
        "address": {
            "city": "Jo_Burg",
            "street": "Lowstreet",
            "housenumber": "12",
            "ZIP-Code": "11223",
        },
    },
]

docs = []
for person in persons:
    docs.append(test_db.save(person))

all_docs = test_db.all_docs(params={"limit": "2", "descending": "true"})
all_docs = test_db.all_docs(data={"limit": 2})

pprint.pprint(all_docs)
