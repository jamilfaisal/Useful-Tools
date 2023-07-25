import json
import os
import requests as requests


def get_user(name):
    # TODO: Complete this function
    filename = os.path.join('src/secrets.json')
    try:
        with open(filename, mode='r') as f:
            secrets = json.loads(f.read())
    except FileNotFoundError:
        secrets = {}

    url = "https://api.notion.com/v1/users/"
