from Best_TV_Episodes.Controller.EpisodeAdder import EpisodeAdder
from Best_TV_Episodes.Controller.DataPersist import Importer, Exporter, AutoSave


class Controller:
    def __init__(self, view):
        self.database = {}
        self.view = view
        self.autosaver = None

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
        all_episodes.sort(key=lambda x: x.season)
        all_episodes.sort(key=lambda x: x.count, reverse=True)
        return all_episodes

    def import_data(self):
        result = Importer().import_data()
        if type(result) is dict:
            self.database = result
            self.view.display_information_message("import_success")
        else:
            self.view.display_error_message("import_fail")

    def export_data(self):
        if Exporter().export(self.database) == -1:
            self.view.display_error_message("export_fail")
        else:
            self.view.display_information_message("export_success")

    def autosave(self):
        if self.autosaver is None:
            self.autosaver = AutoSave(self)
            if self.autosaver.autosave_first_start() == -1:
                self.view.display_error_message("autosave_fail")
            else:
                self.view.display_information_message("autosave_turned_on")
        else:
            self.autosaver.autosave_stop()
            self.autosaver = None
            self.view.display_information_message("autosave_turned_off")

    def exit(self):
        if self.autosaver:
            self.autosaver.autosave_stop()
            self.autosaver = None
        exit(0)
