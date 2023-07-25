class Movie:

    def __init__(self, title, release_year, notion_page):
        self.title = title
        self.release_year = release_year
        self.notion_page = notion_page
        self.imdb_rating = None

    def set_imdb_rating(self, rating):
        self.imdb_rating = rating
