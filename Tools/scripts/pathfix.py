#!/usr/bin/env python3

# Change the #! line (shebang) occurring kwenye Python scripts.  The new interpreter
# pathname must be given ukijumuisha a -i option.
#
# Command line arguments are files ama directories to be processed.
# Directories are searched recursively kila files whose name looks
# like a python module.
# Symbolic links are always ignored (tatizo kama explicit directory
# arguments).
# The original file ni kept kama a back-up (ukijumuisha a "~" attached to its name),
# -n flag can be used to disable this.

# Sometimes you may find shebangs ukijumuisha flags such kama `#! /usr/bin/env python -si`.
# Normally, pathfix overwrites the entire line, including the flags.
# To change interpreter na keep flags kutoka the original shebang line, use -k.
# If you want to keep flags na add to them one single literal flag, use option -a.


# Undoubtedly you can do this using find na sed ama perl, but this is
# a nice example of Python code that recurses down a directory tree
# na uses regular expressions.  Also note several subtleties like
# preserving the file's mode na avoiding to even write a temp file
# when no changes are needed kila a file.
#
# NB: by changing only the function fixfile() you can turn this
# into a program kila a different change to Python programs...

agiza sys
agiza re
agiza os
kutoka stat agiza *
agiza getopt

err = sys.stderr.write
dbg = err
rep = sys.stdout.write

new_interpreter = Tupu
preserve_timestamps = Uongo
create_backup = Kweli
keep_flags = Uongo
add_flags = b''


eleza main():
    global new_interpreter
    global preserve_timestamps
    global create_backup
    global keep_flags
    global add_flags

    usage = ('usage: %s -i /interpreter -p -n -k -a file-or-directory ...\n' %
             sys.argv[0])
    jaribu:
        opts, args = getopt.getopt(sys.argv[1:], 'i:a:kpn')
    tatizo getopt.error kama msg:
        err(str(msg) + '\n')
        err(usage)
        sys.exit(2)
    kila o, a kwenye opts:
        ikiwa o == '-i':
            new_interpreter = a.encode()
        ikiwa o == '-p':
            preserve_timestamps = Kweli
        ikiwa o == '-n':
            create_backup = Uongo
        ikiwa o == '-k':
            keep_flags = Kweli
        ikiwa o == '-a':
            add_flags = a.encode()
            ikiwa b' ' kwenye add_flags:
                err("-a option doesn't support whitespaces")
                sys.exit(2)
    ikiwa sio new_interpreter ama sio new_interpreter.startswith(b'/') ama \
           sio args:
        err('-i option ama file-or-directory missing\n')
        err(usage)
        sys.exit(2)
    bad = 0
    kila arg kwenye args:
        ikiwa os.path.isdir(arg):
            ikiwa recursedown(arg): bad = 1
        lasivyo os.path.islink(arg):
            err(arg + ': will sio process symbolic links\n')
            bad = 1
        isipokua:
            ikiwa fix(arg): bad = 1
    sys.exit(bad)


eleza ispython(name):
    rudisha name.endswith('.py')


eleza recursedown(dirname):
    dbg('recursedown(%r)\n' % (dirname,))
    bad = 0
    jaribu:
        names = os.listdir(dirname)
    tatizo OSError kama msg:
        err('%s: cannot list directory: %r\n' % (dirname, msg))
        rudisha 1
    names.sort()
    subdirs = []
    kila name kwenye names:
        ikiwa name kwenye (os.curdir, os.pardir): endelea
        fullname = os.path.join(dirname, name)
        ikiwa os.path.islink(fullname): pita
        lasivyo os.path.isdir(fullname):
            subdirs.append(fullname)
        lasivyo ispython(name):
            ikiwa fix(fullname): bad = 1
    kila fullname kwenye subdirs:
        ikiwa recursedown(fullname): bad = 1
    rudisha bad


eleza fix(filename):
##  dbg('fix(%r)\n' % (filename,))
    jaribu:
        f = open(filename, 'rb')
    tatizo IOError kama msg:
        err('%s: cannot open: %r\n' % (filename, msg))
        rudisha 1
    ukijumuisha f:
        line = f.readline()
        fixed = fixline(line)
        ikiwa line == fixed:
            rep(filename+': no change\n')
            rudisha
        head, tail = os.path.split(filename)
        tempname = os.path.join(head, '@' + tail)
        jaribu:
            g = open(tempname, 'wb')
        tatizo IOError kama msg:
            err('%s: cannot create: %r\n' % (tempname, msg))
            rudisha 1
        ukijumuisha g:
            rep(filename + ': updating\n')
            g.write(fixed)
            BUFSIZE = 8*1024
            wakati 1:
                buf = f.read(BUFSIZE)
                ikiwa sio buf: koma
                g.write(buf)

    # Finishing touch -- move files

    mtime = Tupu
    atime = Tupu
    # First copy the file's mode to the temp file
    jaribu:
        statbuf = os.stat(filename)
        mtime = statbuf.st_mtime
        atime = statbuf.st_atime
        os.chmod(tempname, statbuf[ST_MODE] & 0o7777)
    tatizo OSError kama msg:
        err('%s: warning: chmod failed (%r)\n' % (tempname, msg))
    # Then make a backup of the original file kama filename~
    ikiwa create_backup:
        jaribu:
            os.rename(filename, filename + '~')
        tatizo OSError kama msg:
            err('%s: warning: backup failed (%r)\n' % (filename, msg))
    isipokua:
        jaribu:
            os.remove(filename)
        tatizo OSError kama msg:
            err('%s: warning: removing failed (%r)\n' % (filename, msg))
    # Now move the temp file to the original file
    jaribu:
        os.rename(tempname, filename)
    tatizo OSError kama msg:
        err('%s: rename failed (%r)\n' % (filename, msg))
        rudisha 1
    ikiwa preserve_timestamps:
        ikiwa atime na mtime:
            jaribu:
                os.utime(filename, (atime, mtime))
            tatizo OSError kama msg:
                err('%s: reset of timestamp failed (%r)\n' % (filename, msg))
                rudisha 1
    # Return success
    rudisha 0


eleza parse_shebang(shebangline):
    shebangline = shebangline.rstrip(b'\n')
    start = shebangline.find(b' -')
    ikiwa start == -1:
        rudisha b''
    rudisha shebangline[start:]


eleza populate_flags(shebangline):
    old_flags = b''
    ikiwa keep_flags:
        old_flags = parse_shebang(shebangline)
        ikiwa old_flags:
            old_flags = old_flags[2:]
    ikiwa sio (old_flags ama add_flags):
        rudisha b''
    # On Linux, the entire string following the interpreter name
    # ni pitaed kama a single argument to the interpreter.
    # e.g. "#! /usr/bin/python3 -W Error -s" runs "/usr/bin/python3 "-W Error -s"
    # so shebang should have single '-' where flags are given na
    # flag might need argument kila that reasons adding new flags is
    # between '-' na original flags
    # e.g. #! /usr/bin/python3 -sW Error
    rudisha b' -' + add_flags + old_flags


eleza fixline(line):
    ikiwa sio line.startswith(b'#!'):
        rudisha line

    ikiwa b"python" haiko kwenye line:
        rudisha line

    flags = populate_flags(line)
    rudisha b'#! ' + new_interpreter + flags + b'\n'


ikiwa __name__ == '__main__':
    main()
