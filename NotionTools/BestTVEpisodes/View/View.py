from NotionTools.BestTVEpisodes.Controller.Controller import Controller
from NotionTools.BestTVEpisodes.Utils.utils import sanitize_input
from NotionTools.BestTVEpisodes.View.messages import interface_messages, user_input_messages, error_messages, information_messages


class View:

    def __init__(self):
        self.controller = Controller(self)

    def main_interface(self):
        while True:
            self.display_interface()
            choice = sanitize_input(self.display_user_input("main_interface"))
            if choice == -1:
                self.display_error_message("invalid_choice")
                continue
            elif choice == 1:
                self.controller.add_episodes()
            elif choice == 2:
                self.display_database()
            elif choice == 3:
                self.controller.import_data()
            elif choice == 4:
                self.controller.export_data()
            elif choice == 5:
                self.controller.autosave()
            elif choice == 6:
                self.controller.exit()
                break

    def display_interface(self):
        if self.controller.autosaver is None:
            interface = interface_messages["main_interface_autosave_off"]
        else:
            interface = interface_messages["main_interface_autosave_on"]
        print(interface)

    def display_database(self):
        all_episodes = self.controller.get_all_episodes()
        if len(all_episodes) == 0:
            print(information_messages["no_episodes_found"])
            return
        for ep in all_episodes:
            print(ep)

    @staticmethod
    def display_error_message(key):
        print(error_messages[key])

    @staticmethod
    def display_user_input(key):
        return input(user_input_messages[key])

    @staticmethod
    def display_information_message(key):
        print(information_messages[key])
