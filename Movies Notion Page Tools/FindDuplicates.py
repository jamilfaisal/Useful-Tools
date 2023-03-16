import MoviesGetter


def find_duplicates(movie_lst):
    seen = set()
    duplicates = []

    for movie in movie_lst:
        if movie in seen:
            duplicates.append(movie)
        else:
            seen.add(movie)
    return duplicates


def find_movie_duplicates():
    db = MoviesGetter.get_database()
    # Get all movies into a list
    # return find_duplicates(movie_list)


if __name__ == '__main__':
    print()
