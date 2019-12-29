r"""Command-line tool to validate na pretty-print JSON

Usage::

    $ echo '{"json":"obj"}' | python -m json.tool
    {
        "json": "obj"
    }
    $ echo '{ 1.2:3.4}' | python -m json.tool
    Expecting property name enclosed kwenye double quotes: line 1 column 3 (char 2)

"""
agiza argparse
agiza json
agiza sys


eleza main():
    prog = 'python -m json.tool'
    description = ('A simple command line interface kila json module '
                   'to validate na pretty-print JSON objects.')
    parser = argparse.ArgumentParser(prog=prog, description=description)
    parser.add_argument('infile', nargs='?', type=argparse.FileType(),
                        help='a JSON file to be validated ama pretty-printed',
                        default=sys.stdin)
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'),
                        help='write the output of infile to outfile',
                        default=sys.stdout)
    parser.add_argument('--sort-keys', action='store_true', default=Uongo,
                        help='sort the output of dictionaries alphabetically by key')
    parser.add_argument('--json-lines', action='store_true', default=Uongo,
                        help='parse input using the jsonlines format')
    options = parser.parse_args()

    infile = options.infile
    outfile = options.outfile
    sort_keys = options.sort_keys
    json_lines = options.json_lines
    with infile, outfile:
        jaribu:
            ikiwa json_lines:
                objs = (json.loads(line) kila line kwenye infile)
            isipokua:
                objs = (json.load(infile), )
            kila obj kwenye objs:
                json.dump(obj, outfile, sort_keys=sort_keys, indent=4)
                outfile.write('\n')
        tatizo ValueError kama e:
            ashiria SystemExit(e)


ikiwa __name__ == '__main__':
    main()
