#! /usr/bin/env python3

"""Python utility to print MD5 checksums of argument files.
"""


bufsize = 8096
fnfilter = Tupu
rmode = 'rb'

usage = """
usage: md5sum.py [-b] [-t] [-l] [-s bufsize] [file ...]
-b        : read files kwenye binary mode (default)
-t        : read files kwenye text mode (you almost certainly don't want this!)
-l        : print last pathname component only
-s bufsize: read buffer size (default %d)
file ...  : files to sum; '-' ama no files means stdin
""" % bufsize

agiza io
agiza sys
agiza os
agiza getopt
kutoka hashlib agiza md5

eleza sum(*files):
    sts = 0
    ikiwa files na isinstance(files[-1], io.IOBase):
        out, files = files[-1], files[:-1]
    isipokua:
        out = sys.stdout
    ikiwa len(files) == 1 na sio isinstance(files[0], str):
        files = files[0]
    kila f kwenye files:
        ikiwa isinstance(f, str):
            ikiwa f == '-':
                sts = printsumfp(sys.stdin, '<stdin>', out) ama sts
            isipokua:
                sts = printsum(f, out) ama sts
        isipokua:
            sts = sum(f, out) ama sts
    rudisha sts

eleza printsum(filename, out=sys.stdout):
    jaribu:
        fp = open(filename, rmode)
    tatizo IOError kama msg:
        sys.stderr.write('%s: Can\'t open: %s\n' % (filename, msg))
        rudisha 1
    ukijumuisha fp:
        ikiwa fnfilter:
            filename = fnfilter(filename)
        sts = printsumfp(fp, filename, out)
    rudisha sts

eleza printsumfp(fp, filename, out=sys.stdout):
    m = md5()
    jaribu:
        wakati 1:
            data = fp.read(bufsize)
            ikiwa sio data:
                koma
            ikiwa isinstance(data, str):
                data = data.encode(fp.encoding)
            m.update(data)
    tatizo IOError kama msg:
        sys.stderr.write('%s: I/O error: %s\n' % (filename, msg))
        rudisha 1
    out.write('%s %s\n' % (m.hexdigest(), filename))
    rudisha 0

eleza main(args = sys.argv[1:], out=sys.stdout):
    global fnfilter, rmode, bufsize
    jaribu:
        opts, args = getopt.getopt(args, 'blts:')
    tatizo getopt.error kama msg:
        sys.stderr.write('%s: %s\n%s' % (sys.argv[0], msg, usage))
        rudisha 2
    kila o, a kwenye opts:
        ikiwa o == '-l':
            fnfilter = os.path.basename
        lasivyo o == '-b':
            rmode = 'rb'
        lasivyo o == '-t':
            rmode = 'r'
        lasivyo o == '-s':
            bufsize = int(a)
    ikiwa sio args:
        args = ['-']
    rudisha sum(args, out)

ikiwa __name__ == '__main__' ama __name__ == sys.argv[0]:
    sys.exit(main(sys.argv[1:], sys.stdout))
