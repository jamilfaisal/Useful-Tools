from src.MoviePicker import RandomMoviePicker, IMDBSortedMoviePicker

if __name__ == "__main__":
    while True:
        print("Select from the following options")
        print("1. Pick a random movie")
        print("2. Pick best movies based on IMDB")
        print("3. Pick worst movies based on IMDB")
        user_choice = input()
        if user_choice == "1":
            RandomMoviePicker.pick_a_random_movie()
            break
        elif user_choice == "2":
            IMDBSortedMoviePicker.pick_best_movies()
            break
        else:
            print("Try again")
