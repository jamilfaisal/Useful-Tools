import json
import os

import requests as requests

from src.Data.Movie import Movie


def get_database(database_filter=None):
    """
    Gets all movies from the Movies database using Notion API
    :param database_filter: Optional filtering of the database
    :return: The Notion API GET response
    """
    filename = os.path.join('src/secrets.json')
    try:
        with open(filename, mode='r') as f:
            secrets = json.loads(f.read())
    except FileNotFoundError:
        secrets = {}

    url = "https://api.notion.com/v1/databases/{}/query".format(secrets["DB_ID"])
    sorts = [
        {
            "property": "Movie",
            "direction": "ascending"
        }
    ]
    headers = {
        "accept": "application/json",
        "Notion-Version": "2022-06-28",
        "content-type": "application/json",
        "Authorization": secrets["AUTH"]
    }
    if database_filter is None:
        payload = {
            "sorts": sorts
        }
    else:
        payload = {
            "filter": database_filter,
            "sorts": sorts
        }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        raise Exception("First POST call to get database rows failed with status code: {}, Text :{}",
                        response.status_code, response.text)
    response_formatted = json.loads(response.text)
    result = response_formatted["results"]
    # Notion Pagination limits results returned to 100 rows. Need to make further calls to get all rows of the database
    while response_formatted["has_more"]:
        payload["start_cursor"] = response_formatted["next_cursor"]
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            raise Exception("Consequent POST call to get database rows failed with status code: {}, Text :{}",
                            response.status_code, response.text)
        response_formatted = json.loads(response.text)
        result += response_formatted["results"]
    return result


def convert_to_movies_list(db):
    """
    Converts all entries from the Notion API GET response into Movie instances
    :param db: The Notion API GET response
    :return: A list of Movie instances
    """
    movie_list = []
    for movie_notion_page in db:
        movie_title = movie_notion_page["properties"]["Movie"]["title"][0]["text"]["content"]
        movie_release_year = movie_notion_page["properties"]["Release Year"]["number"]
        movie_list.append(Movie(movie_title, movie_release_year, movie_notion_page))
    return movie_list


def get_movies_list(database_filter=None):
    """
    Gets all movies from the Movie database as Movie instances
    :return: A list of Movie instances
    """
    return convert_to_movies_list(get_database(database_filter))
