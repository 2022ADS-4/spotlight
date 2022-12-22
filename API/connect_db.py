from pymongo import MongoClient
from typing import Dict, List


class MongoDB:
    """
    This is the main class for getting and posting information to our mongo database
    """
    def __init__(self, db_access_key="user1", db_pass="1234",  db="spotlight_main", collection="main",):
        self.db_access_key = "user1" if db_access_key is None else db_access_key
        self.db_pass="1234" if db_pass is None else db_pass
        self.db="spotlight_main" if db is None else db
        self.collection="main" if collection is None else collection
        self.client = self.get_mongo_client(db_access_key, db_pass)
        self.db = self.client[db]
        self.collection = self.db[collection]

    def get_mongo_client(self, db_access_key, db_pass):
        return MongoClient(f"mongodb+srv://{db_access_key}:{db_pass}@spotlight.dd4uru6.mongodb.net/?retryWrites=true&w=majority")

    def update_entry(self, prev_entry, new_entry):
        from pymongo import ReturnDocument
        self.collection.find_one_and_update(prev_entry[0], {"$set": new_entry}, return_document=ReturnDocument.AFTER)

    def insert_entry(self, entry:Dict):
        self.collection.insert_one(entry)

    def insert_many_entries(self, entries:List[Dict]):
        return self.collection.insert_many(entries)

    def delete_entry(self, entry:Dict):
        return self.collection.delete_one(entry, comment=f"deleted {entry}")

    def get_one_info(self, query:Dict):
        return self.collection.find_one(query)
    
    def get_info(self, query:Dict):
        return [entry for entry in self.collection.find(query)]

    def get_user_movie_rating(self, user_id, movie_id):
        return self.get_info({"user_id": user_id, "movie_id": movie_id})

    def get_user(self, user_id):
        return self.get_info({"user_id": user_id})

    def post_user_rating(self, user_id, movie_id, rating):
        query_dict = {"user_id": user_id, "movie_id": movie_id, "rating": rating}
        user_previous = self.get_info({"user_id": user_id, "movie_id": movie_id})
        if user_previous:
            return self.update_entry(user_previous, query_dict)
        return self.insert_entry(query_dict)

    def delete_user_entry(self, user_id, movie_id):
        return self.delete_entry({"user_id": user_id, "movie_id": movie_id})

    def get_movie(self, movie_id):
        return self.get_one_info({"movie_id": movie_id})
        
    def load_db_access_credentials(self):
        with open("./credentials.txt", "r") as fh:
            for line in fh:
                if "user=" in line:
                    user = line.strip().split("=")[-1]
                    self.db_access_key = user
                elif "pass=" in line:
                    passw = line.strip().split("=")[-1]
                    self.db_pass = passw

    # functions from Thor:
    # tested for sequence model. works!

    def save_sequence_model(self, model, model_infos):
        query_dict = {"sequence_model": model, "model_info": model_infos}
        model_previous = self.get_info({"sequence_model": model, "model_info": model_infos})
        if model_previous:
            return self.update_entry(model_previous, query_dict)
        return self.insert_entry(query_dict)
    
    def save_explicit_model(self, model):
        query_dict = {"explicit_model": model}
        model_previous = self.get_info({"explicit_model": model})
        if model_previous:
            return self.update_entry(model_previous, query_dict)
        return self.insert_entry(query_dict)
    
    def get_explicit_model(self, model):
        query_dict = {"explicit_model": model}
        data = self.collection.find_one(query_dict)
        with open("explicit_model.pt","wb") as f:
            f.write(data["explicit_model"])
        return None
    
    def get_sequence_model(self, model):
        query_dict = {"sequence_model": model}
        data = self.collection.find_one(query_dict)
        with open("sequence_model.pt","wb") as f:
            f.write(data["sequence_model"])
        with open("sequence_model.txt","wb") as f:
            f.write(data["model_info"])
        return None