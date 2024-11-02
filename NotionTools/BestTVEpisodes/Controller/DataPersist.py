import os
import pickle
import time
import threading
import tkinter
from tkinter.filedialog import askopenfilename, asksaveasfilename

from NotionTools.BestTVEpisodes.Utils.utils import sanitize_timer, validate_file_name


class Importer:

    def import_data(self):
        return self.parse_data(self.get_filename())

    @staticmethod
    def get_filename():
        root = tkinter.Tk()
        root.withdraw()
        root.wm_attributes('-topmost', 1)
        return validate_file_name(askopenfilename(parent=root))

    @staticmethod
    def parse_data(file_name):
        if os.path.getsize(file_name) > 0:
            with open(file_name, "rb") as f:
                return pickle.load(f)


class Exporter:

    @staticmethod
    def export(database):
        file_path = Exporter.get_filepath()
        Exporter.export_data(database, file_path)

    @staticmethod
    def get_filepath():
        root = tkinter.Tk()
        root.withdraw()
        root.wm_attributes('-topmost', 1)
        return validate_file_name(asksaveasfilename(filetypes=(("pkl file", "*.pkl"),), defaultextension='.pkl'))

    @staticmethod
    def export_data(database, file_path):
        with open(file_path, "wb") as f:
            pickle.dump(database, f)


# Modified based on https://stackoverflow.com/a/40965385
class AutoSave:

    def __init__(self, controller):
        # Export arguments
        self.controller = controller
        self.file_path = Exporter.get_filepath()
        # Autosave runs every interval seconds
        self.interval = sanitize_timer(self.controller.view.display_user_input("enter_autosave_number_of_seconds"))
        # Threading Attributes
        self.thread_timer = None
        self.autosave_running_status = False
        self.next_call = None

    def autosave_first_start(self):
        if self.file_path == -1:
            self.controller.view.display_error_message("invalid_file_path")
            return -1
        if self.interval == -1:
            self.controller.view.display_error_message("autosave_invalid_timer")
            return -1

        self.next_call = time.time()
        self.autosave_start()

    def autosave_start(self):
        if self.autosave_running_status is False:
            self.next_call += self.interval
            self.thread_timer = threading.Timer(self.next_call - time.time(), self.autosave_run)
            self.thread_timer.start()
            self.autosave_running_status = True

    def autosave_run(self):
        self.autosave_running_status = False
        self.autosave_start()
        Exporter.export_data(self.controller.database, self.file_path)

    def autosave_stop(self):
        self.thread_timer.cancel()
        self.autosave_running_status = False
