import torch
from connect_db import MongoDB
from typing import List, Dict
import tempfile
from process_data.process_movie_data import MovieLens
import numpy as np


class RecommendMovies:
    MONGO_ACCESS_MODELS = MongoDB(collection="models")
    MONGO_ACCESS_USERS = MongoDB()

    def __init__(self, user_id):
        self.user_id = user_id
        self.user_data:List[Dict] = self.get_user_data(user_id)
        self.explicit_model_file = tempfile.mktemp(prefix="explicit")
        self.sequential_model_file = tempfile.mktemp(prefix="sequence")

        self.explicit_model = None
        self.sequential_model = None

    def recommend(self):
        if not self.user_data:
            return None
        """
        Both of our models require indices for movies to give movie recommendations back
        """
        self.all_movies_data = np.array(set(int(data["movie_id"]) for data in MovieLens.download_data_from_db() if "movie_id" in data))

        self.explicit_model = self.load_explicit_model()
        self.sequential_model = self.load_sequential_model()

        previous_movies = self.get_previously_watched_movies()
        exp_recommend_movies = self.get_recommendations_from_explicit_model()
        seq_recommend_movies = self.get_recommendations_from_sequential_model()
        recommended_movies = exp_recommend_movies + seq_recommend_movies
        filtered_movies = self.filter_previously_watched_movies(recommended_movies, previous_movies)
        return self.get_movie_title_and_genre(filtered_movies)

    def rate_movie(self, movie_id, rating):
        if not self.user_data:
            return None
        self.MONGO_ACCESS_USERS.post_user_rating(self.user_id, movie_id, rating=rating)
        return True

    def get_user_data(self,user_id):
        return self.MONGO_ACCESS_USERS.get_user(user_id)

    def get_recommendations_from_explicit_model(self, n_movies=10):

        ratings = self.explicit_model.predict(
            user_ids=int(self.user_id),
            item_ids=self.all_movies_data
        )
        indices = np.argpartition(ratings, -n_movies)[-n_movies:]
        best_movie_ids = indices[np.argsort(ratings[indices])]
        return [i for i in best_movie_ids]

    def get_recommendations_from_sequential_model(self, n_movies=10):
        ratings = self.sequential_model.predict(
            sequences=[int(user_data["movie_id"]) for user_data in self.user_data],
            item_ids=self.all_movies_data
        )
        indices = np.argpartition(ratings, -n_movies)[-n_movies:]
        best_movie_ids = indices[np.argsort(ratings[indices])]
        return [movie_id for movie_id in best_movie_ids]

    def get_previously_watched_movies(self):
        return [movie_data["movie_id"] for movie_data in self.user_data]

    @staticmethod
    def filter_previously_watched_movies(recommended_movies, previous_movies):
        return list(set(recommended_movies).difference(set(previous_movies)))

    def load_sequential_model(self):
        explicit_binary_file = self.MONGO_ACCESS_MODELS.get_sequence_model()
        with open(self.sequential_model_file, "wb") as f:
            f.write(explicit_binary_file)
        return torch.load(self.sequential_model_file)

    def load_explicit_model(self):
        explicit_binary_file = self.MONGO_ACCESS_MODELS.get_explicit_model()
        with open(self.explicit_model_file, "wb") as f:
            f.write(explicit_binary_file)
        return torch.load(self.explicit_model_file)

    def get_movie_title_and_genre(self, movie_ids:List):
        recommended_movies = []
        for movie_id in movie_ids:
            movie_dict = self.MONGO_ACCESS_USERS.get_movie(movie_id)
            recommended_movies.append({"title":movie_dict["title"], "genres":movie_dict["genres"]})
        return recommended_movies

###TODO MAKE THIS FUNCTION WORK!!!
print(RecommendMovies("13").recommend())