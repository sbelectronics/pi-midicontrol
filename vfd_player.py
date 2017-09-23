import select
import sys
import termios
import time
import tty
import smbus

from mididb import DEFAULT_DIR
from midiplayer import MidiPlayer
from options import parse_options

from ioexpand import MCP23017, MCP23017_threadsafe
from vfdcontrol import VFDController, trimpad

CURSOR_SONG = "song"
CURSOR_FOLDER = "folder"

class VFDMidiPlayer(MidiPlayer):
    def __init__(self, root=DEFAULT_DIR, display=None):
        super(VFDMidiPlayer, self).__init__(root)
        self.display = display
        self.cursor = CURSOR_SONG

    def update_status(self, error=None):
        if (error):
            print "Error: ", error

        if self.cursor == CURSOR_SONG:
            cursor_folder=" "
            cursor_song=">"
        else:
            cursor_folder=">"
            cursor_song=" "

        folder_name = self.cur_folder_name[len(self.folder_common_prefix):]

        self.display.setPosition(0,0)
        self.display.writeStr(cursor_folder + trimpad(folder_name[-15:], 15))
        self.display.setPosition(0,1)
        self.display.writeStr(cursor_song + trimpad(self.cur_song[1], 15))

    def poll(self):
        # button3 toggles between folder and song
        if self.display.poller.get_button3_event():
            if self.cursor == CURSOR_SONG:
                self.cursor = CURSOR_FOLDER
            else:
                self.cursor = CURSOR_SONG
            self.update_status()

        delta = self.display.poller.get_delta()

        if (delta!=0):
            print delta

        fastmode = not self.display.button2_state

        if delta > 0:
            if self.cursor==CURSOR_FOLDER:
                if fastmode:
                    self.next_major()
                else:
                    self.next_folder(delta)
            else:
                if fastmode:
                    self.next_file(delta*10)
                else:
                    self.next_file(delta)
        elif delta < 0:
            if self.cursor==CURSOR_FOLDER:
                if fastmode:
                    self.prev_major()
                else:
                    self.prev_folder(-delta)
            else:
                if fastmode:
                    self.prev_file(-delta*10)
                else:
                    self.prev_file(-delta)

        if self.idle:
            self.next_file()

def getchar():
    fd = sys.stdin.fileno()
    old_tcattr = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_tcattr)
    return ch

def main():
    (options, args) = parse_options()

    bus = smbus.SMBus(1)
    display = VFDController(MCP23017(bus, 0x20))

    display.setDisplay(True, False, False)
    display.cls()

    player = VFDMidiPlayer(root = options.dir, display=display)

    print "Loaded ", player.count, "files into database"

    if (options.writecatalog):
        player.write_catalog()
        print "catalog saved"
        return

    stdin_fd = sys.stdin.fileno()
    new_term = termios.tcgetattr(stdin_fd)
    old_term = termios.tcgetattr(stdin_fd)
    new_term[3] = (new_term[3] & ~termios.ICANON & ~termios.ECHO)
    termios.tcsetattr(stdin_fd, termios.TCSAFLUSH, new_term)

    try:
        while True:
            player.poll()
            time.sleep(0.1)

    finally:
        player.shutdown()
        termios.tcsetattr(stdin_fd, termios.TCSAFLUSH, old_term)

if __name__ == "__main__":
    main()