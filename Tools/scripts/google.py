#! /usr/bin/env python3

"""Script to search ukijumuisha Google

Usage:
    python3 google.py [search terms]
"""

agiza sys
agiza urllib.parse
agiza webbrowser


eleza main(args):
    eleza quote(arg):
        ikiwa ' ' kwenye arg:
            arg = '"%s"' % arg
        rudisha urllib.parse.quote_plus(arg)

    qstring = '+'.join(quote(arg) kila arg kwenye args)
    url = urllib.parse.urljoin('https://www.google.com/search', '?q=' + qstring)
    webbrowser.open(url)

ikiwa __name__ == '__main__':
    main(sys.argv[1:])
