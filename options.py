from optparse import OptionParser
from mididb import DEFAULT_DIR

def parse_options():
    parser = OptionParser()
    parser.add_option("-d", "--dir", dest="dir", help="directory to find midi files", metavar="DIR", default=DEFAULT_DIR, action="store", type="string")
    parser.add_option("-w", "--writecatalog", dest="writecatalog", help="write catalog", action="store_true", default=False)

    return parser.parse_args()
