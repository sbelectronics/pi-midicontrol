import os
import signal
import subprocess
from threading import Thread

from mididb import MidiFileDatabase


class PlayerThread(Thread):
    def __init__(self, player, filename):
        super(PlayerThread, self).__init__()
        self.player = player
        self.process = None
        self.filename = filename
        self.daemon = True

    def success_return(self):
        self.player.play_complete(self, error=None)

    def fail_return(self):
        self.player.play_complete(self, error="failed in player")

    def run(self):
        args = ["aplaymidi", "--port", "128:1", self.filename]
        self.process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn = os.setsid)
        (stdout, stderr) = self.process.communicate()
        if (self.process.returncode == 0):
            self.success_return()
        else:
            self.fail_return()

    def stop(self):
        if self.process:
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)

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
        self.player_thread = PlayerThread(self, os.path.join(path, fn))
        self.player_thread.start()
        self.update_status()

    def play_complete(self, player_thread, error):
        if (error):
            self.update_status(error = error)

        self.player_thread = None
        self.idle = True
