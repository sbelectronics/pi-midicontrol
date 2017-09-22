import time
from ioexpand import MCP23017

BIT_ENC_A = 0x01
BIT_ENC_B = 0x02
BIT_ENC_SW = 0x04
BIT_ENC_B = 0x08
BIT_ENC_G = 0x10
BIT_ENC_R = 0x20
BIT_BUTTON1 = 0x40
BIT_BUTTON2 = 0x80

BIT_RS = 0x01
BIT_E = 0x02
BIT_DB4 = 0x04
BIT_DB5 = 0x08
BIT_DB6 = 0x10
BIT_DB7 = 0x20
BIT_WR = 0x40
BIT_BUTTON3 = 0x80

# amount of time to hold E high or low. Seems like 0 works just fine, the display can be clocked as fast as we can
# clock it.
E_TICK = 0 # 0.0001

class VFDController(object):

    def __init__(self, io):
        self.io = io

        self.io.set_iodir(0, BIT_ENC_A | BIT_ENC_B | BIT_ENC_SW | BIT_BUTTON1 | BIT_BUTTON2)
        self.io.set_iodir(1, BIT_BUTTON3)

        self.io.set_pullup(0, BIT_ENC_A | BIT_ENC_B | BIT_ENC_SW | BIT_BUTTON1 | BIT_BUTTON2)
        self.io.set_pullup(1, BIT_BUTTON3)

        self.io.set_gpio(1,0)

        self.reset()

    def writeNibble(self, data, rs=0):
        self.io.set_gpio(1, rs | (data << 2) | BIT_E)    # raise E to write
        if (E_TICK): time.sleep(E_TICK)
        self.io.set_gpio(1, rs | (data << 2))            # clear E
        if (E_TICK): time.sleep(E_TICK)

    def readNibble(self, rs=0):
        self.io.set_gpio(1, BIT_WR)
        self.io.set_gpio(1, BIT_WR | BIT_E)
        if (E_TICK): time.sleep(E_TICK)
        v = (self.io.get_gpio(1) >> 2) & 0x0F
        self.io.set_gpio(1, BIT_WR)
        self.io.set_gpio(1, 0)
        if (E_TICK): time.sleep(E_TICK)
        return v

    def waitNotBusy(self):
        self.io.set_iodir(1, BIT_DB4 | BIT_DB5 | BIT_DB6 | BIT_DB7 | BIT_BUTTON3)
        while True:
            v = self.readNibble(rs=0) << 4
            v = v + self.readNibble(rs=0)
            #print "busy_check %X" % v
            if (v & 0x80) == 0:
                break
        self.io.set_iodir(1, BIT_BUTTON3)

    def writeCmd(self, c):
        self.writeNibble(c>>4, rs=0)
        self.writeNibble(c&0x0F, rs=0)
        self.waitNotBusy()

    def writeData(self, c):
        self.writeNibble(c>>4, rs=1)
        self.writeNibble(c&0x0F, rs=1)
        #self.waitNotBusy()

    def writeStr(self, s):
        for c in s:
            self.writeData(ord(c))

    def reset(self):
        self.writeNibble(0x3, rs=0)
        time.sleep(0.02)
        self.writeNibble(0x3, rs=0)
        time.sleep(0.01)
        self.writeNibble(0x3, rs=0)
        time.sleep(0.001)

        self.writeNibble(0x2, rs=0)
        self.waitNotBusy()
        self.writeCmd(0x28)    # DL, 4-bit / 2-line
        self.setDisplay(display=True, cursor=True, blink=False)

    def cls(self):
        self.writeCmd(0x01)
        time.sleep(0.005)

    def setPosition(self, x, y):
        self.writeCmd(0x80 | (0x40*y + x))
        time.sleep(0.005)

    def setDirection(self, leftToRight, autoScroll):
        cmd = 4
        if leftToRight:
            cmd = cmd | 2
        if autoScroll:
            cmd = cmd | 1

        self.writeCmd(cmd)

    def setDisplay(self, display, cursor, blink):
        cmd = 8
        if display:
            cmd = cmd | 4
        if cursor:
            cmd = cmd | 2
        if blink:
            cmd = cmd | 1

        self.writeCmd(cmd)

"""
    BufferedDisplay

    The start of a buffered display object, to only send the diff to the VFD. Needs work.
"""
class BufferedDisplay(object):
    def __init__(self, display):
        self.display = display

        self.width = 16
        self.height = 2

        self.buf_lines = [" " * self.width, " " * self.width]
        self.buf_last = [" " * self.width, " " * self.width]

    def bufSetPosition(self, x, y):
        buf_x = x
        buf_y = y

    def scroll(self):
        for i in range(0, self.height - 1):
            self.buf_lines[i] = self.buf_lines[i + 1]

    def bufWrite(self, str):
        for ch in str:
            self.buf_lines[self.buf_y][self.buf_x] = ch
            self.buf_x = self.buf_x + 1
            if (self.buf_x >= self.width):
                self.buf_x = 0
                self.buf_y = self.buf_y + 1
                if (self.buf_y >= self.height):
                    self.scroll()
                    self.buf_y = self.height-1
                    self.buf_lines[self.buf_y] = " " * self.width

    def bufUpdate(self):
        pass
        # implement this...

def trimpad(x, l):
    if len(x) < l:
        x = x + " " * (l-len(x))
    return x[:l]

""" 
    main: A simple datetime demo.
"""

def main():
    import smbus
    from datetime import datetime

    bus = smbus.SMBus(1)
    display = VFDController(MCP23017(bus, 0x20))

    display.setDisplay(True, False, False)
    display.cls()

    while True:
        (date, time) = str(datetime.now()).split(" ")
        display.setPosition(0,0)
        display.writeStr(trimpad(date,16))
        display.setPosition(0,1)
        display.writeStr(trimpad(time, 16))


if __name__ == "__main__":
    main()