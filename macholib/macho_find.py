#!/usr/bin/env python

from macholib._cmdline import main as _main


def print_file(fp, path):
    print >>fp, path

def main():
    _main(print_file)

if __name__ == '__main__':
    try:
        main(print_file)
    except KeyboardInterrupt:
        pass
