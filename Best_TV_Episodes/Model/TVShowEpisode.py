class TVShowEpisode:

    def __init__(self, season: int, episode: int, title: str):
        self.season = season
        self.episode = episode
        self.title = title
        self.count = 1

    def increase(self):
        self.count += 1

    def set_title(self, title):
        self.title = title

    def get_title(self):
        return self.title

    def __repr__(self):
        if self.title != "":
            return "{}x{} - {} (Count: {})".format(self.season, self.episode, self.title, self.count)
        else:
            return "{}x{} (Count: {})".format(self.season, self.episode, self.count)
