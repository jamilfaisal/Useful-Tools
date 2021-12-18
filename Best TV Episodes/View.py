from Controller import Controller
from utils import sanitize_input


class View:

    def __init__(self):
        self.controller = Controller(self)

    def main_interface(self):
        interface = "1. Add Episodes\n2. Display Database\n3. Exit"
        while True:
            print(interface)
            choice = sanitize_input(input("Enter option: "))
            if choice == -1:
                print("Please enter a valid choice!")
                continue
            elif choice == 1:
                self.controller.add_episodes()
            elif choice == 2:
                self.display_database()
            elif choice == 3:
                break

    def display_database(self):
        all_episodes_sorted = self.controller.get_all_episodes()
        if len(all_episodes_sorted) == 0:
            print("No episodes entered!")
        for ep in all_episodes_sorted:
            print(ep)

    @staticmethod
    def ask_episode_entry():
        return input("Enter:  (Format: SEASON EPISODE - TITLE) (TITLE is optional) (enter 'q' to go back)\n")

    @staticmethod
    def enter_valid_entry():
        print("Enter a valid entry!")


main = View()
main.main_interface()
