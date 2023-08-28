from imdb import Cinemagoer

from src.MoviePicker.IMDBSortedMoviePicker import get_imdb_rating_for_movie

if __name__ == "__main__":
    print("Enter movie name:")
    while True:
        user_choice = input()
        imdb_rating = get_imdb_rating_for_movie(Cinemagoer(), user_choice)
        print("IMDB Rating: {}".format(imdb_rating))
