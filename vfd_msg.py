import select
import sys
import time
import tty
import smbus

from ioexpand import MCP23017, MCP23017_threadsafe
from vfdcontrol import VFDController, trimpad, COLOR_GREEN, COLOR_RED, COLOR_NONE

def main():
    bus = smbus.SMBus(1)
    display = VFDController(MCP23017(bus, 0x20))

    display.setDisplay(True, False, False)
    display.cls()
    display.set_color(COLOR_NONE)

    display.writeStr(sys.argv[1])

if __name__ == "__main__":
    main()
