from Best_TV_Episodes.utils import sanitize_input
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
            entry = self.sanitize_episode_entry(season_episode_title_not_sanitized)
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

    @staticmethod
    def sanitize_episode_entry(user_input: str):
        user_input_split = user_input.split(" ")
        if len(user_input_split) < 2 or len(user_input_split) == 3 or (len(user_input_split) > 3
                                                                       and user_input_split[2] != "-"):
            return -1
        season = sanitize_input(user_input_split[0])
        if season == -1:
            return -1
        episode = sanitize_input(user_input_split[1])
        if episode == -1:
            return -1
        title = ""
        if len(user_input_split) > 3:
            for i in range(3, len(user_input_split)):
                title += user_input_split[i] + " "
        return [season, episode, title[:-1]]

    def get_all_episodes(self):
        all_episodes = [self.database[k] for k in self.database]
        all_episodes.sort(key=lambda x: x.count, reverse=True)
        return all_episodes

    def import_paste_data(self):
        pass
