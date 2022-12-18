### This script will handle requests coming from front_end, and will return recommended movies
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

class Input(BaseModel):
    user_id:int
    genre:Optional[str] = None

class Output(BaseModel):
    movie_id:Optional[int]
    movie_title:str
    rating:float


app = FastAPI(title="Movie recommendation")
@app.get("/")
def homepage():
    """
    Just a homepage for our api
    """
    return {"Homepage\ngo to data or prediction pages for our Recommender services"}
#@app.route("/data")
def datapage():
    """
    Shows data (and maybe some graphics plots)
    """
    pass

@app.get("/get_movies")#, response_model=Output)
def get_recommended_movies(user_id):
    """
    this function will take user input from front
    and deliver it to recommender model to process
    also triggers sending recommender outputs to front
    """
    from connect_db import MongoDB
    ##Ask to MongoDB if user exists
    user_info = MongoDB("user1", "1234").get_user(user_id)
    if user_info:
        ##from process_data.recommend_movies import recommender
        ##return recommender(user_id)
        return {"movie_ids": [2], "movie_titles": ["something in the way"], "ratings": [3.6]}
    return {}

@app.post("/rating")
def post_user_rating(user_id, movie_id, rating):
    from connect_db import MongoDB
    ##Ask to MongoDB if user exists
    return MongoDB("user1", "1234").post_user_rating(user_id, movie_id, rating)