import cPickle
from operator import itemgetter
import os

#DEFAULT_DIR = "../../midisong/130000_Pop_Rock_Classical_Videogame_EDM_MIDI_Archive[6_19_15]"
DEFAULT_DIR = "files"

class MidiFileDatabase(object):
    def __init__(self, root = DEFAULT_DIR):
        self.root = root
        self.folders = {}
        self.count = 0

        fn = os.path.join(root, "midi-catalog.cpickle")
        if os.path.exists(fn):
            self.folders = cPickle.load(open(fn))
        else:
            self.load_filenames("root", root)
            for k in self.folders.keys():
                self.folders[k] = sorted(self.folders[k], key=itemgetter(1))

        self.folder_names = sorted(self.folders.keys())

        self.cur_folder_index = 0
        self.cur_file_index = 0

        self.folder_common_prefix = self.find_common_prefix()

    def find_common_prefix(self):
        prefix_len = 1
        common_prefix = ""
        while (prefix_len <= len(self.folder_names[0].split("/"))):
            prefix = "/".join(self.folder_names[0].split("/")[:prefix_len]) + "/"
            for name in self.folder_names:
                if not (name.startswith(prefix)):
                    return common_prefix
            common_prefix=prefix
            prefix_len += 1
        return ""

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
    def cur_folder_name(self):
        return self.folder_names[self.cur_folder_index]

    @property
    def cur_folder(self):
        return self.folders[self.cur_folder_name]

    @property
    def cur_song(self):
        return self.cur_folder[self.cur_file_index]

    def change_event(self):
        pass

    def next_major(self, no_event=False):
        index = 0
        tries = 0
        orig_folder_index = self.cur_folder_index
        orig_name = self.folder_names[self.cur_folder_index]
        while True:
            self.next_folder(no_event=True)
            cur_name = self.folder_names[self.cur_folder_index]
            cur_prefix = cur_name.split("/")[index]
            orig_prefix = orig_name.split("/")[index]
            if (cur_prefix != orig_prefix):
                break

            tries += 1
            if (tries > 1000):
                tries = 0
                index += 1
                self.cur_folder_index = orig_folder_index

        if not no_event:
            self.change_event()

    def prev_major(self, no_event=False):
        index = 0
        tries = 0
        orig_folder_index = self.cur_folder_index
        orig_name = self.folder_names[self.cur_folder_index]
        while True:
            self.prev_folder(no_event=True)
            cur_name = self.folder_names[self.cur_folder_index]
            cur_prefix = cur_name.split("/")[index]
            orig_prefix = orig_name.split("/")[index]
            if (cur_prefix != orig_prefix):
                break

            tries += 1
            if (tries > 1000):
                tries = 0
                index += 1
                self.cur_folder_index = orig_folder_index

        if not no_event:
            self.change_event()

    def next_folder(self, amount=1, no_event=False):
        self.cur_folder_index += amount
        if (self.cur_folder_index >= len(self.folder_names)):
            self.cur_folder_index = 0
        self.cur_file_index = 0
        if (not no_event):
            self.change_event()

    def prev_folder(self, amount=1, no_event=False):
        self.cur_folder_index -= amount
        if (self.cur_folder_index < 0):
            self.cur_folder_index = len(self.folder_names)-1
        self.cur_file_index = 0
        if (not no_event):
            self.change_event()

    def next_file(self, amount=1):
        folder = self.cur_folder
        self.cur_file_index += amount
        if (self.cur_file_index >= len(folder)):
            self.next_folder(no_event=True)
        self.change_event()

    def prev_file(self, amount=1):
        self.cur_file_index -= amount
        if (self.cur_file_index <0):
            self.prev_folder(no_event=True)
            self.cur_file_index = len(self.cur_folder)-1
        self.change_event()

    def write_catalog(self):
        fn = os.path.join(self.root, "midi-catalog.cpickle")
        cPickle.dump(self.folders, open(fn,"w"))

def main():
    db = MidiFileDatabase()
    print "Loaded ", db.count, "files into database"

if __name__ == "__main__":
    main()
