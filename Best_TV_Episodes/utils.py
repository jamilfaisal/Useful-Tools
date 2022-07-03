def sanitize_input(choice: str):
    try:
        choice = int(choice)
        return choice
    except ValueError:
        return -1


def sanitize_timer(choice: str):
    try:
        timer = int(choice)
        if timer <= 9:
            return -1
        return timer
    except ValueError:
        return -1
