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
    from recommend_movies import RecommendMovies
    return RecommendMovies(user_id, None, None).recommend()

@app.post("/rating")
def post_user_rating(user_id, movie_id, rating):
    from recommend_movies import RecommendMovies
    return RecommendMovies(user_id, None, None).rate_movie(movie_id, rating)