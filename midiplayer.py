import os
import signal
import subprocess
import sys
import time
from threading import Thread

from mididb import MidiFileDatabase


class PlayerThread(Thread):
    def __init__(self, player, filename):
        super(PlayerThread, self).__init__()
        self.player = player
        self.process = None
        self.filename = filename
        self.daemon = True
        self.no_notify = False
        self.done = False

    def success_return(self):
        if not self.no_notify:
            self.player.play_complete(self, error=None)

    def fail_return(self, stderr):
        if not self.no_notify:
            self.player.play_complete(self, error=stderr)

    def run(self):
        args = ["aplaymidi", "--port", "128:1", '"' + self.filename + '"']
        # print " ".join(args)
        self.process = subprocess.Popen(" ".join(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn = os.setsid)
        (stdout, stderr) = self.process.communicate()
        if stderr:
            sys.stderr.write(stderr)
        if (self.process.returncode == 0):
            self.success_return()
        else:
            self.fail_return(stderr=stderr)
        self.done = True

    def stop(self, no_notify=False):
        self.no_notify = no_notify
        if self.process:
            print "sending kill signal"
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
        while not self.done:
            time.sleep(0.1)

class MidiPlayer(MidiFileDatabase):
    def __init__(self):
        super(MidiPlayer, self).__init__()
        self.player_thread = None
        self.idle = True

    def update_status(self, error=None):
        pass

    def change_event(self):
        self.idle = False
        (path, fn) = self.cur_song

        if self.player_thread:
            self.player_thread.stop(no_notify=True)
            self.all_notes_off()

        self.player_thread = PlayerThread(self, os.path.join(path, fn))
        self.player_thread.start()
        self.update_status()

    def play_complete(self, player_thread, error):
        if (error):
            self.update_status(error = error)

        self.player_thread = None
        self.idle = True

    def all_notes_off(self):
        fd = open("/dev/ttyAMA0","w", 0)
        for i in range(0, 16):
            fd.write(chr(0xB0 + i))
            fd.write(chr(123))
            fd.write(chr(0))

    def shutdown(self):
        if self.player_thread:
            self.player_thread.stop(no_notify=True)
            self.all_notes_off()

#if __name__ == "__main__":
#    t = PlayerThread(player=None, filename="files/C/C.ANDREWS.Yesterday man.MID")
#    t.run()
