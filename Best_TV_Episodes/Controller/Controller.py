from Best_TV_Episodes.Controller.EpisodeAdder import EpisodeAdder
from Best_TV_Episodes.Controller.Importer import Importer


class Controller:
    def __init__(self, view):
        self.database = {}
        self.view = view
        self.episode_adder = EpisodeAdder()
        self.importer = Importer()

    def add_episodes(self):
        while True:
            season_episode_title_not_sanitized = self.view.ask_episode_entry()
            if season_episode_title_not_sanitized == "q":
                return None
            if self.episode_adder.add_episodes(self.database, season_episode_title_not_sanitized) == -1:
                self.view.enter_valid_entry()

    def get_all_episodes(self):
        all_episodes = [self.database[k] for k in self.database]
        all_episodes.sort(key=lambda x: x.count, reverse=True)
        return all_episodes

    def import_data(self):
        result = self.importer.import_data()
        if result is dict:
            self.database = result
            self.view.import_success()
        else:
            self.view.import_fail()
            print(result)
