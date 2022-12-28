import torch
from connect_db import MongoDB
from typing import List, Dict
import tempfile
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
        self.all_movies_data = None

    def recommend(self):
        if not self.user_data:
            return None
        """
        Both of our models require indices for movies to give movie recommendations back
        """

        self.explicit_model = self.load_explicit_model()
        self.sequential_model = self.load_sequential_model()
        self.all_movies_data = self.get_movies_data_from_db()

        previous_movies = self.get_previously_watched_movies()
        exp_recommend_movies = self.get_recommendations_from_explicit_model()
        #seq_recommend_movies = self.get_recommendations_from_sequential_model()
        recommended_movies = exp_recommend_movies #+ seq_recommend_movies
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
        items = self.all_movies_data
        ratings = self.explicit_model.predict(
            user_ids=int(self.user_id),
            item_ids=items
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
        return list(set(map(str, recommended_movies)).difference(set(map(str, previous_movies))))

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
            if movie_dict is None: continue
            recommended_movies.append({"movie_id":movie_id, "title":movie_dict["title"], "genres":movie_dict["genres"]})
        return recommended_movies

    def get_movies_data_from_db(self):
        movie_id_set = set()
        for data in list(self.MONGO_ACCESS_USERS.get_info({})):
            if "movie_id" not in data: continue
            movie_id = int(data["movie_id"])
            if movie_id > self.explicit_model._num_items or movie_id > self.sequential_model._num_items: continue
            movie_id_set.add(movie_id)
        return np.array(list(movie_id_set))

