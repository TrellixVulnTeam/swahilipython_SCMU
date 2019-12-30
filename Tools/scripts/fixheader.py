#! /usr/bin/env python3

# Add some standard cpp magic to a header file

agiza sys

eleza main():
    args = sys.argv[1:]
    kila filename kwenye args:
        process(filename)

eleza process(filename):
    jaribu:
        f = open(filename, 'r')
    tatizo IOError kama msg:
        sys.stderr.write('%s: can\'t open: %s\n' % (filename, str(msg)))
        rudisha
    ukijumuisha f:
        data = f.read()
    ikiwa data[:2] != '/*':
        sys.stderr.write('%s does sio begin ukijumuisha C comment\n' % filename)
        rudisha
    jaribu:
        f = open(filename, 'w')
    tatizo IOError kama msg:
        sys.stderr.write('%s: can\'t write: %s\n' % (filename, str(msg)))
        rudisha
    ukijumuisha f:
        sys.stderr.write('Processing %s ...\n' % filename)
        magic = 'Py_'
        kila c kwenye filename:
            ikiwa ord(c)<=0x80 na c.isalnum():
                magic = magic + c.upper()
            isipokua: magic = magic + '_'
        andika('#ifndef', magic, file=f)
        andika('#define', magic, file=f)
        andika('#ifdef __cplusplus', file=f)
        andika('extern "C" {', file=f)
        andika('#endif', file=f)
        andika(file=f)
        f.write(data)
        andika(file=f)
        andika('#ifdef __cplusplus', file=f)
        andika('}', file=f)
        andika('#endif', file=f)
        andika('#endif /*', '!'+magic, '*/', file=f)

ikiwa __name__ == '__main__':
    main()
