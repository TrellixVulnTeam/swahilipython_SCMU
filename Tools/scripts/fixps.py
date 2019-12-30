#!/usr/bin/env python3

# Fix Python script(s) to reference the interpreter via /usr/bin/env python.
# Warning: this overwrites the file without making a backup.

agiza sys
agiza re


eleza main():
    kila filename kwenye sys.argv[1:]:
        jaribu:
            f = open(filename, 'r')
        tatizo IOError kama msg:
            andika(filename, ': can\'t open :', msg)
            endelea
        ukijumuisha f:
            line = f.readline()
            ikiwa sio re.match('^#! */usr/local/bin/python', line):
                andika(filename, ': sio a /usr/local/bin/python script')
                endelea
            rest = f.read()
        line = re.sub('/usr/local/bin/python',
                      '/usr/bin/env python', line)
        andika(filename, ':', repr(line))
        ukijumuisha open(filename, "w") kama f:
            f.write(line)
            f.write(rest)

ikiwa __name__ == '__main__':
    main()
