import os.path

import torch
from connect_db import MongoDB
from typing import List, Dict
class RecommendMovies:
    MONGO_ACCESS = MongoDB(collection="models")

    def __init__(self, user_id):
        self.user_id = user_id
        self.user_data:List[Dict] = self.get_user_data(user_id)
        self.explicit_model = self.load_explicit_model()
        self.sequential_model= self.load_sequential_model()

    def recommend(self):
        if not self.user_data:
            return None
        previous_movies = self.get_previously_watched_movies()
        exp_recommend_movies = self.get_recommendations_from_explicit_model()
        seq_recommend_movies = self.get_recommendations_from_sequential_model()
        recommended_movies = exp_recommend_movies + seq_recommend_movies
        filtered_movies = self.filter_previously_watched_movies(recommended_movies, previous_movies)
        return self.get_movie_title_and_genre(filtered_movies)

    def rate_movie(self, movie_id, rating):
        if not self.user_data:
            return None
        self.MONGO_ACCESS.post_user_rating(self.user_id, movie_id, rating=rating)
        return True
    def get_user_data(self,user_id):
        return self.MONGO_ACCESS.get_user(user_id)

    def get_recommendations_from_explicit_model(self, n_movies=10):
        import numpy as np
        from process_data.process_movie_data import MovieLens
        dataset=MovieLens.download_data_from_db()
        ratings = self.sequential_model.predict(user_ids=self.user_id)
        indices = np.argpartition(ratings, -n_movies)[-n_movies:]
        best_movie_ids = indices[np.argsort(ratings[indices])]
        return [dataset.item_ids[i] for i in best_movie_ids]

    def get_recommendations_from_sequential_model(self):
        return self.sequential_model(self.user_id)

    def get_previously_watched_movies(self):
        return [movie_data["movie_id"] for movie_data in self.user_data]

    @staticmethod
    def filter_previously_watched_movies(recommended_movies, previous_movies):
        return list(set(recommended_movies).difference(set(previous_movies)))

    def load_sequential_model(self):
        seq_model_path = self.MONGO_ACCESS.get_sequential_model()
        return torch.load(seq_model_path)

    def load_explicit_model(self):
        #exp_model_path = self.MONGO_ACCESS.get_explicit_model()
        from config import DATA_PATH
        exp_model_path = os.path.join(DATA_PATH, "explicit.pt")
        return torch.load(exp_model_path)

    def get_movie_title_and_genre(self, movie_ids:List):
        recommended_movies = []
        for movie_id in movie_ids:
            movie_dict = self.MONGO_ACCESS.get_movie(movie_id)
            recommended_movies.append({"title":movie_dict["title"], "genres":movie_dict["genres"]})
        return recommended_movies