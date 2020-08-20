import json
import uuid
import copy
import requests
from requests.auth import HTTPBasicAuth


# Fauxton: visit http://127.0.0.1:5984/_utils/
# always use self generated uuid, because that will ensure only one document actually gets created
class Conflict(Exception):
    pass

class Unauthorized(Exception):
    pass


class Api:
    """
    Baseclass to handle communication with the CouchDB Server Api
    """
    def __init__(self, base_url, username, password):
        self.session = requests.Session()
        url = "/".join((base_url, "_session"))
        headers = {"Content-Type": "application/json"}
        payload = json.dumps({"name": username, "password": password})
        response = self.session.post(url, headers=headers, data=payload)
        if response.status_code == 200:
            print("Connected successfully.")
        elif response.status_code == 401:
            raise Unauthorized("could not authenticate with the CouchDB server.")
        else:
            raise Exception("Something went wrong.")

    def get(self, url, **kwargs):
        if not kwargs.get("headers"):
            headers = {"Content-Type": "application/json"}
        else:
            headers = kwargs["headers"]
        params = kwargs.get("params")
        response = self.session.get(url, headers=headers, params=params)
        return response.status_code, json.loads(response.content)

    def post(self, url: str, **kwargs):
        if not kwargs.get("headers"):
            headers = {"Content-Type": "application/json"}
        else:
            headers = kwargs["headers"]
        data = json.dumps(kwargs.get("data"))
        response = self.session.post(url, headers=headers, data=data)
        return response.status_code, json.loads(response.content)
    
    def put(self, url: str, headers=None, data=None):
        if not headers:
            headers = {"Content-Type": "application/json"}
        response = self.session.put(url, headers=headers, data=data)
        return response.status_code, json.loads(response.content)
    
    def delete(self, url, headers=None):
        if not headers:
            headers = {"Content-Type": "application/json"}
        response = self.session.delete(url, headers=headers)
        return response.status_code, json.loads(response.content)


class Database:
    """
    represents a CouchDB database, its properties and the functions that can be perfomed on it
    """
    def __init__(self, server, name):
        self.server = server
        self.name = name
        self.base_url = "/".join((server.base_url, name))

    def all_docs(self, **kwargs):
        url = "/".join((self.base_url, "_all_docs"))
        if kwargs.get("data"):
            _, json_data = self.server.post(url, **kwargs)
        else:
            _, json_data = self.server.get(url, **kwargs)
        return json_data

    def save(self, doc) -> dict:
        """
        save a document to the database
        """
        _doc = copy.copy(doc)
        if "_id" not in _doc:
            _doc["_id"] = uuid.uuid4().hex

        url = "/".join([self.base_url, _doc["_id"]])
        json_data = json.dumps(_doc).encode("utf-8")
        status_code, json_data = self.server.put(url, data=json_data)
        if status_code == 409:
            raise Conflict(json_data["reason"])
        if "rev" in json_data and json_data["rev"] is not None:
            _doc["_rev"] = json_data["rev"]

        return _doc


class Server(Api):
    """
    represents a CouchDB server, its properties and the functions that can be perfomed on it
    """
    def __init__(self, username, password, ip_address="127.0.0.1", port="5984"):
        self.base_url = f"http://{ip_address}:{port}"
        super().__init__(self.base_url, username, password)


    def all_dbs(self) -> dict:
        """
        Get all databases on the server
        args:
            none
        return:
            list(Database): list of all databases on the server
        """
        url = "/".join((self.base_url, "_all_dbs"))
        _, json_data = self.get(url)
        return [Database(self, name) for name in json_data]

    def active_tasks(self) -> dict:
        """
        Get list of active running tasks
        """
        url = "/".join((self.base_url, "_active_tasks"))
        _, json_data = self.get(url)
        return json_data

    def dbs_info(self, databases) -> dict:
        """
        Get infomation on a list of databases
        """
        url = "/".join((self.base_url, "_dbs_info"))
        json_data = json.dumps({"keys": databases})
        _, json_data = self.post(url, data=json_data)
        return json_data

    def cluster_setup(self, cluster_setup_data=None) -> dict:
        """
        Get cluster setup info or 
        if cluster setup data is supplied,
        configure the cluster setup
        """
        url = "/".join((self.base_url, "_cluster_setup"))
        if cluster_setup_data:
            data = json.dumps(cluster_setup_data)
            _, json_data = self.post(url, data=data)
        else:
            _, json_data = self.get(url)
        return json_data



    def info(self) -> dict:
        """
        Get some basic info about the CouchDB server
        """
        url = "/".join((self.base_url,))
        _, json_data = self.get(url)
        return json_data

    def create_database(self, database) -> Database:
        """
        Create a new database on the server
        """
        url = "/".join((self.base_url, database))
        status_code, json_data = self.put(url)
        if status_code == 201:
            return Database(self, database)
        elif status_code == 412:
            raise Conflict((json_data["error"], json_data["reason"]))

    def delete_database(self, database) -> dict:
        """
        Delete a database
        """
        url = "/".join((self.base_url, database))
        _, json_data = self.delete(url)
        return json_data
