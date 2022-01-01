from Best_TV_Episodes.Controller.EpisodeAdder import EpisodeAdder
from Best_TV_Episodes.Controller.DataPersist import Importer, Exporter


class Controller:
    def __init__(self, view):
        self.database = {}
        self.view = view

    def add_episodes(self):
        episode_adder = EpisodeAdder()
        while True:
            season_episode_title_not_sanitized = self.view.display_user_input("enter_episode_format")
            if season_episode_title_not_sanitized == "q":
                return None
            if episode_adder.add_episodes(self.database, season_episode_title_not_sanitized) == -1:
                self.view.display_error_message("invalid_entry")

    def get_all_episodes(self):
        all_episodes = [self.database[k] for k in self.database]
        all_episodes.sort(key=lambda x: x.count, reverse=True)
        return all_episodes

    def import_data(self):
        importer = Importer()
        result = importer.import_data()
        if type(result) is dict:
            self.database = result
            self.view.display_information_message("import_success")
        else:
            self.view.display_error_message("import_fail")

    def export_data(self):
        exporter = Exporter()
        file_name = self.view.display_user_input("enter_export_file_name")
        if exporter.export_data(self.database, file_name) == -1:
            self.view.display_error_message("export_fail")
        else:
            self.view.display_information_message("export_success")
