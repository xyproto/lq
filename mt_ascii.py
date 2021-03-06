#!/usr/bin/python
# -*- coding: ascii -*-

import os
import os.path
from sys import exit, argv

COLUMN_WIDTH = 16
MAX_COLUMNS = 5


def white(s):
    """Color text white in a terminal."""
    return "\033[1;37m" + s + "\033[0m"


def green(s):
    """Color text green in a terminal."""
    return "\033[1;32m" + s + "\033[0m"


def blue(s):
    """Color text blue in a terminal."""
    return "\033[1;34m" + s + "\033[0m"


def cyan(s):
    """Color text cyan in a terminal."""
    return "\033[1;36m" + s + "\033[0m"


def gray(s):
    """Color text gray in a terminal."""
    return "\033[1;30m" + s + "\033[0m"


def red(s):
    """Color text red in a terminal."""
    return "\033[1;31m" + s + "\033[0m"


def col(dirname):
    """
    Generate a column of text by listing the contents of a directory.
    Returns a list with strings.
    """
    column = []
    try:
        dirnames = os.listdir(dirname)
    except OSError:
        return column + ['denied']

    dirnames.sort()
    for fn in dirnames:
        fullname = os.path.join(dirname, fn)
        decoration = ""
        if os.path.isdir(fullname):
            decoration = os.sep
        elif os.access(fullname, os.X_OK):
            decoration = "*"
        elif os.path.islink(fullname):
            decoration = "@"
        column += ["|-- " + fn + decoration]
    if column:
        column[-1] = '`' + column[-1][1:]
    return column


def utf8ify(s):
    """Create a representation of the string that print() is willing to use"""
    return s.encode("utf8", "replace").decode("utf8")


def listcolumns(maxlen, lines, colrange):
    """
    Print one full screenwidth of columns, while shortening and coloring the
    entries. Takes the maximum number of lines to print, a dictionary of lines
    where the column number is the key and a range of which colums should be
    printed. Returns nothing.
    """
    colwidth = COLUMN_WIDTH
    for linenr in range(maxlen):
        line = ""
        for colnr in colrange:
            isdir = False
            islink = False
            isexec = False
            isdenied = False
            if colnr in lines:
                rows = lines[colnr]
                if len(rows) > linenr:
                    field = rows[linenr]
                    if field.endswith(os.sep):
                        isdir = True
                    elif field.endswith("*"):
                        isexec = True
                    elif field.endswith("@"):
                        islink = True
                    elif field == "denied":
                        isdenied = True
                    spaces = (colwidth - len(field)) * " "
                    if linenr == 0:
                        if len(field) >= (colwidth-1):
                            field = field[:colwidth-4] + "..."
                            spaces += " "
                    elif len(field) >= colwidth:
                        field = field[:colwidth-4] + "..."
                        spaces += " "
                    if (" " in field) and (linenr > 0):
                        first, second = field.split(" ", 1)
                        if second:
                            if second.startswith("."):
                                second = gray(second)
                            elif isdir:
                                second = blue(second)
                            elif isexec:
                                second = green(second[:-1] + " ")
                            elif islink:
                                second = cyan(second)
                        if second:
                            field = gray(first) + " " + second
                        else:
                            field = first
                    elif linenr == 0:
                        if field.startswith("."):
                            field = gray(field)
                        else:
                            field = white(field)
                    elif isdenied:
                        field = red(field)
                    line += field + spaces
                else:
                    line += colwidth * " "
        if line.strip():
            print(utf8ify(line.rstrip()))


def runlc(curdir="."):

    # Generate the columns by filling the dictionary named "lines"
    # by calling "col" for each directory.
    try:
        l = os.listdir(curdir)
    except FileNotFoundError:
        print(white("not found: ") + red(curdir))
        return
    l.sort()
    lines = {}
    colnr = 0
    maxlen = 0
    for dirname in l:
        if os.path.isdir(os.path.join(curdir, dirname)):
            lines[colnr] = [dirname] + col(os.path.join(curdir, dirname))
            if len(lines[colnr]) > maxlen:
                maxlen = len(lines[colnr])
            colnr += 1
    maxcol = colnr - 1

    # List the columns by calling "listcolumns" for each range of columns.
    if maxcol < MAX_COLUMNS:
        listcolumns(maxlen, lines, range(maxcol+1))
    else:
        start = 0
        while start <= maxcol:
            stop = start + MAX_COLUMNS
            if stop > maxcol:
                stop = maxcol + 1
            listcolumns(maxlen, lines, range(start, stop))
            print("\n")
            start += MAX_COLUMNS


def main():
    try:
        if argv[1:]:
            for dirname in argv[1:]:
                runlc(os.path.expanduser(dirname))
        else:
            runlc(os.path.expanduser("."))
    except KeyboardInterrupt:
        print("\n")
        exit(130)


if __name__ == "__main__":
    main()
