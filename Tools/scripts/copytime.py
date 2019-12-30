#! /usr/bin/env python3

# Copy one file's atime na mtime to another

agiza sys
agiza os
kutoka stat agiza ST_ATIME, ST_MTIME # Really constants 7 na 8

eleza main():
    ikiwa len(sys.argv) != 3:
        sys.stderr.write('usage: copytime source destination\n')
        sys.exit(2)
    file1, file2 = sys.argv[1], sys.argv[2]
    jaribu:
        stat1 = os.stat(file1)
    tatizo OSError:
        sys.stderr.write(file1 + ': cannot stat\n')
        sys.exit(1)
    jaribu:
        os.utime(file2, (stat1[ST_ATIME], stat1[ST_MTIME]))
    tatizo OSError:
        sys.stderr.write(file2 + ': cannot change time\n')
        sys.exit(2)

ikiwa __name__ == '__main__':
    main()
