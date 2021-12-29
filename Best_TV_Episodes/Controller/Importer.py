import tkinter
from tkinter.filedialog import askopenfilename


class Importer:

    def import_data(self):
        return self.parse_data(self.get_filename())

    @staticmethod
    def get_filename():
        root = tkinter.Tk()
        root.withdraw()
        root.wm_attributes('-topmost', 1)
        return askopenfilename(parent=root)

    def parse_data(self, filename):
        database = {}
        with open(filename, 'r') as f:
            data = f.readlines()
            for entry in data:
                if self.episode_adder.add_episodes(database, entry.strip()) == -1:
                    return -1
        return database

    def add_episode(self, entry):
        #TODO Complete
        pass