import os
import select
import signal
import subprocess
import sys
import time
from threading import Thread

from mididb import MidiFileDatabase, DEFAULT_DIR


class PlayerThread(Thread):
    def __init__(self, player, filename):
        print "player init"
        super(PlayerThread, self).__init__()
        self.player = player
        self.process = None
        self.filename = filename
        self.daemon = True
        self.no_notify = False
        self.done = False
        self.stopping = False

    def success_return(self):
        if not self.no_notify:
            self.player.play_complete(self, error=None)

    def fail_return(self, stderr):
        if not self.no_notify:
            self.player.play_complete(self, error=stderr)

    def run(self):
        # sleep to see if the user is skipping fast. If so, then self.stopping will be set while we are
        # sleeping.
        time.sleep(0.2)

        # if the stop signal was received before we even started, then short-circuit and return immediately
        if self.stopping:
            self.fail_return(stderr = "stopped")
            self.done = True
            return

        try:
            args = ["aplaymidi", "--port", "128:1", '"' + self.filename + '"']
            self.process = subprocess.Popen(" ".join(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, preexec_fn = os.setsid)
            print "started", self.process.pid

            stdout = []
            stderr = []
            read_set = [self.process.stdout, self.process.stderr]
            while read_set:
                rlist, wlist, xlist = select.select(read_set, [], [], 0.1)
                if self.process.stdout in rlist:
                    data = os.read(self.process.stdout.fileno(), 1024)
                    if (data == ""):
                        read_set.remove(self.process.stdout)
                    stdout.append(data)
                if self.process.stderr in rlist:
                    data = os.read(self.process.stderr.fileno(), 1024)
                    if (data == ""):
                        read_set.remove(self.process.stderr)
                    stderr.append(data)
                if self.stopping:
                    self.kill_process()

            stdout = "\n".join(stdout)
            stderr = "\n".join(stderr)
            if stderr:
                sys.stderr.write(stderr)
            if (self.process.returncode == 0):
                self.success_return()
            else:
                self.fail_return(stderr=stderr)
        finally:
            print "done"
            self.done = True

    def kill_process(self):
        os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)

    def stop(self, no_notify=False, wait=False):
        self.no_notify = no_notify
        self.stopping = True
        if wait:
            while (not self.done):
                time.sleep(0.1)

class MidiPlayer(MidiFileDatabase):
    def __init__(self, root = DEFAULT_DIR):
        super(MidiPlayer, self).__init__(root)
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
        fd = open("/dev/ttyS0","w", 0) # was /dev/ttyAMA0
        for i in range(0, 16):
            fd.write(chr(0xB0 + i))
            fd.write(chr(123))
            fd.write(chr(0))

    def shutdown(self):
        if self.player_thread:
            self.player_thread.stop(no_notify=True, wait=True)
            self.all_notes_off()

#if __name__ == "__main__":
#    t = PlayerThread(player=None, filename="files/C/C.ANDREWS.Yesterday man.MID")
#    t.run()
