# Parse Makefiles na Python Setup(.in) files.

agiza re


# Extract variable definitions kutoka a Makefile.
# Return a dictionary mapping names to values.
# May ashiria IOError.

makevareleza = re.compile('^([a-zA-Z0-9_]+)[ \t]*=(.*)')

eleza getmakevars(filename):
    variables = {}
    fp = open(filename)
    pendingline = ""
    jaribu:
        wakati 1:
            line = fp.readline()
            ikiwa pendingline:
                line = pendingline + line
                pendingline = ""
            ikiwa sio line:
                koma
            ikiwa line.endswith('\\\n'):
                pendingline = line[:-2]
            matchobj = makevardef.match(line)
            ikiwa sio matchobj:
                endelea
            (name, value) = matchobj.group(1, 2)
            # Strip trailing comment
            i = value.find('#')
            ikiwa i >= 0:
                value = value[:i]
            value = value.strip()
            variables[name] = value
    mwishowe:
        fp.close()
    rudisha variables


# Parse a Python Setup(.in) file.
# Return two dictionaries, the first mapping modules to their
# definitions, the second mapping variable names to their values.
# May ashiria IOError.

setupvareleza = re.compile('^([a-zA-Z0-9_]+)=(.*)')

eleza getsetupinfo(filename):
    modules = {}
    variables = {}
    fp = open(filename)
    pendingline = ""
    jaribu:
        wakati 1:
            line = fp.readline()
            ikiwa pendingline:
                line = pendingline + line
                pendingline = ""
            ikiwa sio line:
                koma
            # Strip comments
            i = line.find('#')
            ikiwa i >= 0:
                line = line[:i]
            ikiwa line.endswith('\\\n'):
                pendingline = line[:-2]
                endelea
            matchobj = setupvardef.match(line)
            ikiwa matchobj:
                (name, value) = matchobj.group(1, 2)
                variables[name] = value.strip()
            isipokua:
                words = line.split()
                ikiwa words:
                    modules[words[0]] = words[1:]
    mwishowe:
        fp.close()
    rudisha modules, variables


# Test the above functions.

eleza test():
    agiza sys
    agiza os
    ikiwa sio sys.argv[1:]:
        andika('usage: python parsesetup.py Makefile*|Setup* ...')
        sys.exit(2)
    kila arg kwenye sys.argv[1:]:
        base = os.path.basename(arg)
        ikiwa base[:8] == 'Makefile':
            andika('Make style parsing:', arg)
            v = getmakevars(arg)
            prdict(v)
        lasivyo base[:5] == 'Setup':
            andika('Setup style parsing:', arg)
            m, v = getsetupinfo(arg)
            prdict(m)
            prdict(v)
        isipokua:
            andika(arg, 'is neither a Makefile nor a Setup file')
            andika('(name must begin ukijumuisha "Makefile" ama "Setup")')

eleza prdict(d):
    keys = sorted(d.keys())
    kila key kwenye keys:
        value = d[key]
        andika("%-15s" % key, str(value))

ikiwa __name__ == '__main__':
    test()
