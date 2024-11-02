from NotionTools.BestTVEpisodes.Controller.EpisodeAdder import EpisodeAdder
from NotionTools.BestTVEpisodes.Controller.DataPersist import Importer, Exporter, AutoSave
from NotionTools.BestTVEpisodes.Utils.utils import get_all_episodes


class Controller:
    def __init__(self, view):
        self.database = {}
        self.view = view
        self.autosaver = None
        self.episode_adder = EpisodeAdder()

    def add_episodes(self):
        while True:
            season_episode_title_unsanitized = self.view.display_user_input("enter_episode_format")
            if season_episode_title_unsanitized == "q":
                return None
            if self.episode_adder.add_episodes(self.database, season_episode_title_unsanitized) == -1:
                self.view.display_error_message("invalid_entry")

    def get_all_episodes(self):
        return get_all_episodes(self.database)

    def import_data(self):
        result = Importer().import_data()
        if type(result) is dict and len(result) != 0:
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
                self.autosaver = None
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
