
###TODO: write a script that takes user_id as input, movie_ids as output


def load_model(wanted_model):
    """
    This function loads a pre-trained model.
    Either from pickle or ML-flow
    """
    model = ...
    if wanted_model == "sequential":
        #Load sequential model
        model
    elif wanted_model == "explicit":
        #Load explicit model
        model

    return model


def get_movie_recommendations_from_model(user_id, model):
    """
    This function gets all movie recommendations for the given user_id
    """
    pass


def filter_recommended_movies(users_watched_movies:set, expected_genre:str, movie_ids_with_genre:dict):
    """
    This function filters predicted movies based on genre and already watched status
    """
    filtered_movies = set()
    for movie_id, genres in movie_ids_with_genre.items():
        if expected_genre not in genres or movie_id in users_watched_movies:
            continue
        filtered_movies.add(movie_id)
    return filtered_movies


def order_filtered_movies(number_of_expected_movies:int=5):
    """
    this function orders the recommended and filtered movies and returns top #number_of_expected_movies
    """
    pass

def process_get_movie_recommendations(user_id, *args):
    model = load_model("")
    movies = get_movie_recommendations_from_model(user_id, model)
    fltr_movies = filter_recommended_movies(*args)
    return order_filtered_movies(5)

##TODO: sequential --> needs a playlist
##TODO: explicit --> user_id