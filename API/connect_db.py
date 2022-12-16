import gzip
import json

from pymongo import MongoClient
from typing import Type, Dict, List


class MongoDB:
    """
    This is the main class for getting and posting information to our mongo database
    """
    def __init__(self, db="spotlight_main", collection="main"):
        self.client = self.get_mongo_client()
        self.db = self.client[db]
        self.collection = self.db[collection]

    def get_mongo_client(self):
        return MongoClient("mongodb+srv://user1:1234@spotlight.dd4uru6.mongodb.net/?retryWrites=true&w=majority")

    def update_entry(self):
        ...

    def insert_entry(self, entry:Dict):
        self.collection.insert_one(entry)

    def insert_many_entries(self, entries:List[Dict]):
        self.collection.insert_many(entries)
    
    def get_user_info(self, user_id):
        return self.collection.find_one({"user_id" : user_id})


from config import DATA_PATH
import os
import pandas as pd

["movie_id", "title", "genres", "user_id", "rating", "timestamp", "tag", "imdb_id", "tmdb_id"]
import csv
def convert_csv2dict(in_csv):
    data = []
    with csv.reader(in_csv, "r") as fh:
        for line in fh:
            if line.startswith("mov"):
                continue
            pline = line.strip().split(",")
            movie_id = pline[0]
            title = pline[1]
            genres:list = pline[2].split("|")
            user_id = pline[3].strip(".0")
            rating = pline[4]
            data.append(
                {
                    "movie_id": str(movie_id) if movie_id != "" else None,
                    "title": str(title) if title != "" else None,
                    "genres": genres,
                    "user_id": str(int(user_id)) if user_id != "" else None,
                    "rating": float(rating) if rating != "" else None
                })
    return data
        

todb = "/home/berk/Projects/spotlight/API/database_data.json"


with open(todb) as js:
    MongoDB().insert_many_entries(convert_csv2dict("/home/berk/Projects/spotlight/data/merged_ml_demo_data.csv"))
