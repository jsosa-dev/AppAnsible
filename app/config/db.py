from pymongo import MongoClient

class Database:
    def __init__(self, uri="mongodb://mongo:27017/", db_name="ansiblewebdb"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def insert_one(self, collection_name, data):
        collection = self.get_collection(collection_name)
        return collection.insert_one(data)

    def find_one(self, collection_name, query):
        collection = self.get_collection(collection_name)
        return collection.find_one(query)

    def find_all(self, collection_name):
        collection = self.get_collection(collection_name)
        return collection.find()

    def distinct(self, collection_name, key):
        collection = self.get_collection(collection_name)
        return collection.distinct(key)
