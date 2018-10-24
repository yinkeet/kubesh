import sys

def printf(format, *args):
    sys.stdout.write(format % args)

def sprintf(format, *args):
    return format % args