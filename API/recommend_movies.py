from connect_db import MongoDB
from typing import List, Dict
class RecommendMovies:
    MONGO_ACCESS = MongoDB()

    def __init__(self, user_id, explicit_model, sequential_model):
        self.user_id = user_id
        self.user_data:List[Dict] = self.get_user_data(user_id)
        self.explicit_model = explicit_model
        self.sequential_model= sequential_model

    def recommend(self):
        if not self.user_data:
            return None
        previous_movies = self.get_previously_watched_movies()
        exp_recommend_movies = self.get_recommendations_from_explicit_model()
        seq_recommend_movies = self.get_recommendations_from_sequential_model()
        #exp_recommend_movies = set()
        filtered_movies = self.filter_previously_watched_movies(exp_recommend_movies, previous_movies)
        return self.get_movie_title_and_genre(filtered_movies)

    def rate_movie(self, movie_id, rating):
        if not self.user_data:
            return None
        self.MONGO_ACCESS.post_user_rating(self.user_id, movie_id, rating=rating)
        return True
    def get_user_data(self,user_id):
        return self.MONGO_ACCESS.get_user(user_id)

    def get_recommendations_from_explicit_model(self):
        ##TODO: load explicit model, ask user_id, get movie ids
        ##TODO: connect it to the explicit model thing
        return ["12", "11", "99"]
        #return self.explicit_model(self.user_id)


    def get_recommendations_from_sequential_model(self):
        ##TODO: load sequential model, ask user_id, get movie ids
        pass
        #return self.sequential_model(self.user_id)

    def get_previously_watched_movies(self):
        return [movie_data["movie_id"] for movie_data in self.user_data]

    @staticmethod
    def filter_previously_watched_movies(recommended_movies, previous_movies):
        return list(set(recommended_movies).difference(set(previous_movies)))

    def get_movie_title_and_genre(self, movie_ids:List):
        recommended_movies = []
        for movie_id in movie_ids:
            movie_dict = self.MONGO_ACCESS.get_movie(movie_id)
            recommended_movies.append({"title":movie_dict["title"], "genres":movie_dict["genres"]})
        return recommended_movies