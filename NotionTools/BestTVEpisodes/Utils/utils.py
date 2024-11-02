def sanitize_input(choice: str):
    try:
        choice = int(choice)
        return choice
    except ValueError:
        return -1


def sanitize_timer(choice: str):
    try:
        timer = int(choice)
        if timer <= 4:
            return -1
        return timer
    except ValueError:
        return -1


def validate_file_name(file_name):
    if file_name == '':
        raise Exception("Invalid file path.")
    else:
        return file_name


def get_all_episodes(database):
    all_episodes = [database[k] for k in database]
    all_episodes.sort(key=lambda x: x.season)
    all_episodes.sort(key=lambda x: x.count, reverse=True)
    return all_episodes
