from NotionTools.MoviesTools.src.Getters.MoviesGetter import get_movies_list


def get_list_of_unwatched_movies():
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
    return get_movies_list(database_filter)
