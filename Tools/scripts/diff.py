#!/usr/bin/env python3
""" Command line interface to difflib.py providing diffs kwenye four formats:

* ndiff:    lists every line na highlights interline changes.
* context:  highlights clusters of changes kwenye a before/after format.
* unified:  highlights clusters of changes kwenye an inline format.
* html:     generates side by side comparison ukijumuisha change highlights.

"""

agiza sys, os, difflib, argparse
kutoka datetime agiza datetime, timezone

eleza file_mtime(path):
    t = datetime.fromtimestamp(os.stat(path).st_mtime,
                               timezone.utc)
    rudisha t.astimezone().isoformat()

eleza main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', action='store_true', default=Uongo,
                        help='Produce a context format diff (default)')
    parser.add_argument('-u', action='store_true', default=Uongo,
                        help='Produce a unified format diff')
    parser.add_argument('-m', action='store_true', default=Uongo,
                        help='Produce HTML side by side diff '
                             '(can use -c na -l kwenye conjunction)')
    parser.add_argument('-n', action='store_true', default=Uongo,
                        help='Produce a ndiff format diff')
    parser.add_argument('-l', '--lines', type=int, default=3,
                        help='Set number of context lines (default 3)')
    parser.add_argument('fromfile')
    parser.add_argument('tofile')
    options = parser.parse_args()

    n = options.lines
    fromfile = options.fromfile
    tofile = options.tofile

    fromdate = file_mtime(fromfile)
    todate = file_mtime(tofile)
    ukijumuisha open(fromfile) kama ff:
        fromlines = ff.readlines()
    ukijumuisha open(tofile) kama tf:
        tolines = tf.readlines()

    ikiwa options.u:
        diff = difflib.unified_diff(fromlines, tolines, fromfile, tofile, fromdate, todate, n=n)
    lasivyo options.n:
        diff = difflib.ndiff(fromlines, tolines)
    lasivyo options.m:
        diff = difflib.HtmlDiff().make_file(fromlines,tolines,fromfile,tofile,context=options.c,numlines=n)
    isipokua:
        diff = difflib.context_diff(fromlines, tolines, fromfile, tofile, fromdate, todate, n=n)

    sys.stdout.writelines(diff)

ikiwa __name__ == '__main__':
    main()
