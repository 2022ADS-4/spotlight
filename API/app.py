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
def get_recommended_movies(user_id, genre=None):
    """
        this function will take user input from front
        and deliver it to recommender model to process
        also triggers sending recommender outputs to front
        """
    # from data_process import run_data_process
    # movies_recommendations:dict = run_data_process.get_recommendations(user_data)
    user_db = ["1", "2", "3", "12", "13", "41", "51"]
    if user_id in user_db: ###mock data, will change
        return {"movie_ids": [2], "movie_titles": ["something in the way"], "ratings": [3.6]}
    return {"movie_ids": [None], "movie_titles": [None], "ratings": [None]}