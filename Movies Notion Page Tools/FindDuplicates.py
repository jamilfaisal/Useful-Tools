import MoviesGetter


def find_duplicates(movie_lst):
    """
    Prints the title of movies that have duplicate entries in the Movies database
    :param movie_lst: List of all movies in the database as Movie instances
    """
    movie_title_release_year = {}
    for movie in movie_lst:
        if movie.title in movie_title_release_year and movie_title_release_year[movie.title] == movie.release_year:
            print(movie.title)
        else:
            movie_title_release_year[movie.title] = movie.release_year


def find_movie_duplicates():
    """
    Finds movies with duplicate entries in the Movies database
    """
    movie_list = MoviesGetter.get_movies_list()
    find_duplicates(movie_list)


if __name__ == '__main__':
    find_movie_duplicates()
