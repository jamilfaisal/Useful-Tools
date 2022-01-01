import os
import pickle
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

    @staticmethod
    def parse_data(file_name):
        if os.path.getsize(file_name) > 0:
            with open(file_name, "rb") as f:
                return pickle.load(f)


class Exporter:
    @staticmethod
    def export_data(database, file_name):
        file_path = os.path.join("Saved Data", file_name + ".pkl")
        if validate_file_name(file_path) == 1:
            with open(file_path, "wb") as f:
                pickle.dump(database, f)
        else:
            return -1


def validate_file_name(file_name):
    try:
        with open(file_name, 'x'):  # OSError if file exists or is invalid
            return 1
    except OSError:
        return -1
