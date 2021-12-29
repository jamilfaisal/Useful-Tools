from Best_TV_Episodes.utils import sanitize_entry
from Best_TV_Episodes.Model.TVShowEpisode import TVShowEpisode
from Best_TV_Episodes.Controller.Importer import Importer


class Controller:
    def __init__(self, view):
        self.database = {}
        self.view = view
        self.importer = Importer(self.database)

    def add_episodes(self):
        while True:
            season_episode_title_not_sanitized = self.view.ask_episode_entry()
            if season_episode_title_not_sanitized == "q":
                return None
            entry = sanitize_entry(season_episode_title_not_sanitized)
            if entry == -1:
                self.view.enter_valid_entry()
            else:
                self.add_episode(entry[0], entry[1], entry[2])

    def add_episode(self, season, episode, title):
        entry_key = str(season) + " " + str(episode)
        if entry_key in self.database:
            episode = self.database[entry_key]
            episode.increase()
            if episode.get_title() == "":
                episode.set_title(title)
        else:
            self.database[entry_key] = TVShowEpisode(season, episode, title)

    def get_all_episodes(self):
        all_episodes = [self.database[k] for k in self.database]
        all_episodes.sort(key=lambda x: x.count, reverse=True)
        return all_episodes

    def import_paste_data(self):
        pass


