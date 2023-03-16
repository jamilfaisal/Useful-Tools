import json
import os

import requests as requests


def get_database(database_filter=None):
    filename = os.path.join('secrets.json')
    try:
        with open(filename, mode='r') as f:
            secrets = json.loads(f.read())
    except FileNotFoundError:
        secrets = {}

    url = "https://api.notion.com/v1/databases/{}/query".format(secrets["DB_ID"])
    sorts = [
        {
            "property": "Name",
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
        headers = headers["start_cursor"] = response_formatted["next_cursor"]
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            raise Exception("Consequent POST call to get database rows failed with status code: {}, Text :{}",
                            response.status_code, response.text)
        response_formatted = json.loads(response.text)
        result.extends(response_formatted["results"])
    return result
