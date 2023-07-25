from src.MoviePicker import RandomMoviePicker

if __name__ == "__main__":
    while True:
        print("Select from the following options")
        print("1. Pick a random movie")
        user_choice = input()
        if user_choice == "1":
            RandomMoviePicker.pick_a_random_movie()
            break
        else:
            print("Try again")
