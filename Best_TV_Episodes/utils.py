def sanitize_input(choice: str):
    try:
        choice = int(choice)
        return choice
    except ValueError:
        return -1
