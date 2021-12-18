def sanitize_input(choice: str):
    try:
        choice = int(choice)
        return choice
    except ValueError:
        return -1


def sanitize_entry(user_input: str):
    user_input_split = user_input.split(" ")
    if len(user_input_split) < 2 or len(user_input_split) == 3 or (len(user_input_split) > 3
                                                                   and user_input_split[2] != "-"):
        return -1
    season = sanitize_input(user_input_split[0])
    if season == -1:
        return -1
    episode = sanitize_input(user_input_split[1])
    if episode == -1:
        return -1
    title = ""
    if len(user_input_split) > 3:
        for i in range(3, len(user_input_split)):
            title += user_input_split[i]
    return [season, episode, title]
