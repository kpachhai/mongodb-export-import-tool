#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import the MongoClient class
from pymongo import MongoClient
from bson import ObjectId

# import the Pandas library
import pandas
# import the NumPy library as an alias
import numpy as np

# these libraries are optional
import os
import time


OLD_MONGO_HOST = "mongodb://mongoadmin:mongopass@localhost:37018/myFirstDatabase?authSource=admin"
NEW_MONGO_HOST = "mongodb+srv://mongoadmin:mongopass@localhost:27017/myFirstDatabase?retryWrites=true&w=majority"

# build a new client instance of MongoClient
mongo_client_old = MongoClient(OLD_MONGO_HOST)
mongo_client_new = MongoClient(NEW_MONGO_HOST)

# start time of script
start_time = time.time()

for db_name in mongo_client_old.list_database_names():
    if(db_name.startswith("hive")):
        directory = db_name

        root_directory = "./mongodb-backup"
        # Check whether the specified path exists or not
        isExist = os.path.exists(root_directory)
        if not isExist:
            # Create a new directory because it does not exist
            os.makedirs(root_directory)

        os.mkdir(os.path.join(root_directory, directory))
        db = mongo_client_old[db_name]
        print("db: {}".format(db_name))

        # Create the corresponding database in the new mongodb instance
        db_new = mongo_client_new[db_name]

        for col_name in db.list_collection_names():
            print("collection: {}".format(col_name))

            # Create the corresponding column in the new mongodb instance
            col_new = db_new[col_name]
            col_new.delete_many({})

            # make an API call to the MongoDB server
            cursor = db[col_name].find()

            # extract the list of documents from cursor obj
            mongo_docs = list(cursor)

            # create an empty DataFrame for storing documents
            docs = pandas.DataFrame(columns=[])

            # iterate over the list of MongoDB dict documents
            for doc in mongo_docs:
                # convert ObjectId() to str
                doc["_id"] = str(doc["_id"])

                # get document _id from dict
                doc_id = doc["_id"]

                # create a Series obj from the MongoDB dict
                series_obj = pandas.Series(doc, name=doc_id)

                # append the MongoDB Series obj to the DataFrame obj
                docs = docs.append(series_obj)
            # export the MongoDB documents as a JSON file
            docs.to_json(
                "{}/{}/{}.json".format(root_directory, db_name, col_name))

            docs.reset_index(inplace=True)
            docs_dict = docs.to_dict("records")

            if(docs_dict):
                for doc in docs_dict:
                    doc["_id"] = ObjectId(doc["_id"])
                    del doc["index"]
                col_new.insert_many(docs_dict)
            else:
                # We need to do this for empty collections so we at least create the collection
                col_new.insert_one({})
                col_new.delete_many({})


print("time elapsed:", time.time()-start_time)
