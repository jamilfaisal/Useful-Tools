from random import choice
from MoviesGetter import get_movies_list


def print_movie_choice(movie_choice):
    print("{}, {}".format(movie_choice.title, movie_choice.release_year))


def pick_a_random_movie_from_list(movie_list):
    # Randomly pick 1 choice from the list
    random_movie = choice(movie_list)

    # Print choice in a pretty way
    print_movie_choice(random_movie)

    # Remove movie from the list
    movie_list.remove(random_movie)
    if len(movie_list) == 0:
        print("No other choices possible!")
        exit(0)

    # Run the above process in a loop
    print("Press 'Enter' to randomly pick another movie!")
    while True:
        if input() == "":
            random_movie = choice(movie_list)
            print_movie_choice(random_movie)
            movie_list.remove(random_movie)
            if len(movie_list) == 0:
                print("No other choices possible!")
                exit(0)
        else:
            break


def pick_a_random_movie_with_person_wants_to_watch(name_of_person):
    database_filter = {
        "and": [
            {
                "property": "Wants to Watch",
                "people": {
                    "contains": name_of_person # TODO: Get the UUID based on the name of the person
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


if __name__ == '__main__':
    pick_a_random_movie()
    # pick_a_random_movie_with_person_wants_to_watch("")
