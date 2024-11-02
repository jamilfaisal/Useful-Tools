from imdb import Cinemagoer

from src.MoviePicker.IMDBSortedMoviePicker import get_imdb_rating_for_movie

if __name__ == "__main__":
    print("Enter movie name:")
    while True:
        user_choice = input()
        imdb_rating, imdb_movie, imdb_year = get_imdb_rating_for_movie(Cinemagoer(), user_choice)
        print("IMDB Rating: {} for {} ({})".format(imdb_rating, imdb_movie, imdb_year))
