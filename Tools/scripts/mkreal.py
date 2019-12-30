#! /usr/bin/env python3

# mkreal
#
# turn a symlink to a directory into a real directory

agiza sys
agiza os
kutoka stat agiza *

join = os.path.join

error = 'mkreal error'

BUFSIZE = 32*1024

eleza mkrealfile(name):
    st = os.stat(name) # Get the mode
    mode = S_IMODE(st[ST_MODE])
    linkto = os.readlink(name) # Make sure again it's a symlink
    ukijumuisha open(name, 'rb') kama f_in: # This ensures it's a file
        os.unlink(name)
        ukijumuisha open(name, 'wb') kama f_out:
            wakati 1:
                buf = f_in.read(BUFSIZE)
                ikiwa sio buf: koma
                f_out.write(buf)
    os.chmod(name, mode)

eleza mkrealdir(name):
    st = os.stat(name) # Get the mode
    mode = S_IMODE(st[ST_MODE])
    linkto = os.readlink(name)
    files = os.listdir(name)
    os.unlink(name)
    os.mkdir(name, mode)
    os.chmod(name, mode)
    linkto = join(os.pardir, linkto)
    #
    kila filename kwenye files:
        ikiwa filename haiko kwenye (os.curdir, os.pardir):
            os.symlink(join(linkto, filename), join(name, filename))

eleza main():
    sys.stdout = sys.stderr
    progname = os.path.basename(sys.argv[0])
    ikiwa progname == '-c': progname = 'mkreal'
    args = sys.argv[1:]
    ikiwa sio args:
        andika('usage:', progname, 'path ...')
        sys.exit(2)
    status = 0
    kila name kwenye args:
        ikiwa sio os.path.islink(name):
            andika(progname+':', name+':', 'sio a symlink')
            status = 1
        isipokua:
            ikiwa os.path.isdir(name):
                mkrealdir(name)
            isipokua:
                mkrealfile(name)
    sys.exit(status)

ikiwa __name__ == '__main__':
    main()
