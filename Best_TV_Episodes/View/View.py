from Best_TV_Episodes.Controller.Controller import Controller
from Best_TV_Episodes.utils import sanitize_input
from Best_TV_Episodes.View.messages import interface_messages, user_input_messages, error_messages, information_messages


class View:

    def __init__(self):
        self.controller = Controller(self)

    def main_interface(self):
        interface = interface_messages["main_interface"]
        while True:
            print(interface)
            choice = sanitize_input(input(user_input_messages["main_interface"]))
            if choice == -1:
                print(error_messages["invalid_choice"])
                continue
            elif choice == 1:
                self.controller.add_episodes()
            elif choice == 2:
                self.display_database()
            elif choice == 3:
                self.ask_import_data()
            elif choice == 4:
                self.controller.autosave()
            elif choice == 5:
                break

    def display_database(self):
        all_episodes_sorted = self.controller.get_all_episodes()
        if len(all_episodes_sorted) == 0:
            print(information_messages["no_episodes_found"])
        for ep in all_episodes_sorted:
            print(ep)

    def ask_import_data(self):
        choice = input(interface_messages["import_data"])
        if choice == 1:
            self.controller.import_paste_data()
        elif choice == 2:
            self.controller.import_from_file()
        elif choice == 3:
            return
        else:
            return

    @staticmethod
    def ask_episode_entry():
        return input(user_input_messages["enter_episode_format"])

    @staticmethod
    def enter_valid_entry():
        print(error_messages["invalid_entry"])
