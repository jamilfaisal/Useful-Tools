from imdb import Cinemagoer

from src.MoviePicker.utils import get_list_of_unwatched_movies

"""
TODO:
Check if csv file containing the ratings exists already. 
    If no, then run the getter and save results to csv file "IMDB_RATINGS_{MONTH}_{YEAR}". Columns: movie_title, release_year, rating
    If yes, then read csv_file and set IMDB ratings for movies in movie_list. Run getter for movies that are None and save new csv_file
"""


def ask_for_number_of_movies_to_show():
    while True:
        num_of_movies = input("Enter number of movies to show\n")
        if num_of_movies.isdigit():
            return int(num_of_movies)
        else:
            print("Try again")


def add_imdb_rating_to_movies(movie_list):
    for movie in movie_list:
        imdb_rating = get_imdb_rating_for_movie(Cinemagoer(), movie.title)
        print("Got rating for {}: {}".format(movie.title, imdb_rating))
        movie.set_imdb_rating(imdb_rating)


def get_imdb_rating_for_movie(cinemagoer, movie_title):
    imdb_results = cinemagoer.search_movie(movie_title)
    if imdb_results:
        movie_id = imdb_results[0].movieID
        imdb_movie = cinemagoer.get_movie(movie_id)
        return imdb_movie.data.get("rating")
    else:
        print("No IMDB results found for {}".format(movie_title))
        return None


def get_imdb_rating(movie):
    return movie.imdb_rating


def sort_movie_list_by_imdb_rating(movie_list, worst=False):
    if worst:
        return sorted(movie_list, key=get_imdb_rating, reverse=True)
    else:
        return sorted(movie_list, key=get_imdb_rating)


def display_movies(movie_list, number_of_movies):
    print("Movie\tRelease Year\tRating")
    for i in range(number_of_movies):
        movie = movie_list[i]
        print("{}\t{}\t{}".format(movie.title, movie.release_year, movie.imdb_rating), end="")


def pick_best_movies():
    number_of_movies = ask_for_number_of_movies_to_show()
    movie_list = get_list_of_unwatched_movies()
    print("Got movie list")
    add_imdb_rating_to_movies(movie_list)
    sorted_movie_list = sort_movie_list_by_imdb_rating(movie_list)
    print("Done sorting")
    display_movies(sorted_movie_list, number_of_movies)


def pick_worst_movies():
    number_of_movies = ask_for_number_of_movies_to_show()
    movie_list = get_list_of_unwatched_movies()
    print("Got movie list")
    add_imdb_rating_to_movies(movie_list)
    sorted_movie_list = sort_movie_list_by_imdb_rating(movie_list, True)
    print("Done sorting")
    display_movies(sorted_movie_list, number_of_movies)
