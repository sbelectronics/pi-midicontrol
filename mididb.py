from operator import itemgetter
import os

#DEFAULT_DIR = "../../midisong/130000_Pop_Rock_Classical_Videogame_EDM_MIDI_Archive[6_19_15]"
DEFAULT_DIR = "files"

class MidiFileDatabase(object):
    def __init__(self, root = DEFAULT_DIR):
        self.root = root
        self.folders = {}
        self.count = 0
        self.load_filenames("root", root)
        self.folder_names = sorted(self.folders.keys())

        import pdb
        pdb.set_trace()
        for k in self.folders.keys():
            self.folders[k] = sorted(self.folders[k], key=itemgetter(1))

        self.cur_folder_index = 0
        self.cur_file_index = 0


    def load_filenames(self, folder, path):
        for fn in os.listdir(path):
            if (fn.startswith(".")):
                continue
            pathname = os.path.join(path, fn)
            if os.path.isdir(pathname):
                self.load_filenames(os.path.join(folder, fn), pathname)
            elif pathname.lower().endswith(".mid"):
                if not folder in self.folders:
                    self.folders[folder] = []
                self.folders[folder].append( (path, fn) )
                self.count += 1

    @property
    def cur_folder(self):
        return self.folders[self.folder_names[self.cur_folder_index]]

    @property
    def cur_song(self):
        return self.cur_folder[self.cur_file_index]

    def change_event(self):
        pass

    def next_folder(self, amount=1, no_event=False):
        self.cur_folder_index += 1
        if (self.cur_folder_index >= len(self.folder_names)):
            self.cur_folder_index = 0
        self.cur_file_index = 0
        if (not no_event):
            self.change_event()

    def prev_folder(self, amount=1, no_event=False):
        self.cur_folder_index -= 1
        if (self.cur_folder_index < 0):
            self.cur_folder_index = len(self.folder_names)-1
        self.cur_file_index = 0
        if (not no_event):
            self.change_event()

    def next_file(self, amount=1):
        folder = self.cur_folder
        self.cur_file_index += 1
        if (self.cur_file_index >= len(folder)):
            self.next_folder(no_event=True)
        self.change_event()

    def prev_file(self, amount=1):
        self.cur_file_index -= 1
        if (self.cur_file_index <0):
            self.prev_folder(no_event=True)
            self.cur_file_index = len(self.cur_folder)-1
        self.change_event()

def main():
    db = MidiFileDatabase()
    print "Loaded ", db.count, "files into database"

if __name__ == "__main__":
    main()
