from random import choice
from src.Getters.MoviesGetter import get_movies_list


def print_movie_choice(movie_choice):
    print("{}, {}".format(movie_choice.title, movie_choice.release_year), end="")


def pick_a_random_movie_from_list(movie_list):
    # Randomly pick 1 choice from the list
    random_movie = choice(movie_list)

    # Print choice in a pretty way
    print_movie_choice(random_movie)

    # Remove movie from the list
    movie_list.remove(random_movie)
    check_if_all_movies_are_picked(movie_list)

    # Run the above process in a loop
    print("\nPress 'Enter' to randomly pick another movie! Input anything else to exit.", end="")
    while True:
        if input() == "":
            random_movie = choice(movie_list)
            print_movie_choice(random_movie)
            movie_list.remove(random_movie)
            check_if_all_movies_are_picked(movie_list)
        else:
            break


def check_if_all_movies_are_picked(movie_list):
    if len(movie_list) == 0:
        print("All movies have been picked")
        exit(0)


def pick_a_random_movie_with_person_wants_to_watch(name_of_person):
    database_filter = {
        "and": [
            {
                "property": "Wants to Watch",
                "people": {
                    "contains": name_of_person  # TODO: Get the UUID based on the name of the person
                }
            },
            {
                "or": [
                    {
                        "property": "Watch Status",
                        "select": {
                            "equals": "Not Watched"
                        }
                    },
                    {
                        "property": "Watch Status",
                        "select": {
                            "equals": "Watching"
                        }
                    },
                    {
                        "property": "Watch Status",
                        "select": {
                            "equals": "Rewatch"
                        }
                    }
                ]
            }
        ]
    }
    movie_list = get_movies_list(database_filter)
    pick_a_random_movie_from_list(movie_list)


def pick_a_random_movie():
    # Get a list of movies from the database filtered by "Watch Status" == "Not Watched" or "Watching" or "Rewatch"
    database_filter = {
        "or": [
            {
                "property": "Watch Status",
                "select": {
                    "equals": "Not Watched"
                }
            },
            {
                "property": "Watch Status",
                "select": {
                    "equals": "Watching"
                }
            },
            {
                "property": "Watch Status",
                "select": {
                    "equals": "Rewatch"
                }
            }
        ]
    }
    movie_list = get_movies_list(database_filter)
    pick_a_random_movie_from_list(movie_list)
