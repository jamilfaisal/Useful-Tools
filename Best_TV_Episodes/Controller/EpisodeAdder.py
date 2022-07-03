from Best_TV_Episodes.Model.TVShowEpisode import TVShowEpisode
from Best_TV_Episodes.utils import sanitize_input


class EpisodeAdder:

    @staticmethod
    def add_episodes(database, episode_title_unsanitized):
        entry = EpisodeAdder.sanitize_episode_entry(episode_title_unsanitized)
        if entry == -1:
            return -1
        else:
            EpisodeAdder.add_episode(database, entry[0], entry[1], entry[2])
            return 0

    @staticmethod
    def add_episode(database, season, episode, title):
        entry_key = str(season) + " " + str(episode)
        if entry_key in database:
            episode = database[entry_key]
            episode.increase()
            if episode.get_title() == "":
                episode.set_title(title)
        else:
            database[entry_key] = TVShowEpisode(season, episode, title)

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
