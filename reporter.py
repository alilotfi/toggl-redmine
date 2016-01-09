import sys


class Color:
    HEADER = '\033[95m'
    INFO = '\033[94m'
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    FAILURE = '\033[91m'
    END_COLOR = '\033[0m'


def report(status, color=None, end='\n'):
    string = '%s'
    if color:
        string = color + string + Color.END_COLOR

    string += end

    sys.stdout.write(string % status)
    sys.stdout.flush()
