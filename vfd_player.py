import select
import sys
import termios
import tty
import smbus

from mididb import DEFAULT_DIR
from midiplayer import MidiPlayer
from options import parse_options

from ioexpand import MCP23017
from vfdcontrol import VFDController, trimpad

class VFDMidiPlayer(MidiPlayer):
    def __init__(self, root=DEFAULT_DIR, display=None):
        super(VFDMidiPlayer, self).__init__(root)
        self.display = display

    def update_status(self, error=None):
        if (error):
            print "Error: ", error

        self.display.setPosition(0,0)
        self.display.writeStr(trimpad(self.cur_song[0][-16:], 16))
        self.display.setPosition(0, 1)
        self.display.writeStr(trimpad(self.cur_song[1], 16))

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

    print "n - next file"
    print "p - previous file"
    print "> - next sub-folder"
    print "< - previous sub-folder"
    print "] - next major-folder"
    print "[ - previous major-folder"
    print "q - quit"

    print ""

    stdin_fd = sys.stdin.fileno()
    new_term = termios.tcgetattr(stdin_fd)
    old_term = termios.tcgetattr(stdin_fd)
    new_term[3] = (new_term[3] & ~termios.ICANON & ~termios.ECHO)
    termios.tcsetattr(stdin_fd, termios.TCSAFLUSH, new_term)

    try:
        while True:
            if player.idle:
                player.next_file()

            dr,dw,de = select.select([sys.stdin], [], [], 0.1)
            if dr != []:
                ch = sys.stdin.read(1)

                #ch = getchar()
                if (ch == "n"):
                    player.next_file()
                elif (ch == "p"):
                    player.prev_file()
                elif (ch == ">"):
                    player.next_folder()
                elif (ch == "<"):
                    player.prev_folder()
                elif (ch == "]"):
                    player.next_major()
                elif (ch == "["):
                    player.prev_major()
                elif (ch == "q"):
                    break
    finally:
        player.shutdown()
        termios.tcsetattr(stdin_fd, termios.TCSAFLUSH, old_term)

if __name__ == "__main__":
    main()