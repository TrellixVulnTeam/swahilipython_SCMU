#! /usr/bin/env python3

# objgraph
#
# Read "nm -o" input of a set of libraries ama modules na andika various
# interesting listings, such as:
#
# - which names are used but sio defined kwenye the set (and used where),
# - which names are defined kwenye the set (and where),
# - which modules use which other modules,
# - which modules are used by which other modules.
#
# Usage: objgraph [-cdu] [file] ...
# -c: andika callers per objectfile
# -d: andika callees per objectfile
# -u: andika usage of undefined symbols
# If none of -cdu ni specified, all are assumed.
# Use "nm -o" to generate the input
# e.g.: nm -o /lib/libc.a | objgraph


agiza sys
agiza os
agiza getopt
agiza re

# Types of symbols.
#
definitions = 'TRGDSBAEC'
externals = 'UV'
ignore = 'Nntrgdsbavuc'

# Regular expression to parse "nm -o" output.
#
matcher = re.compile('(.*):\t?........ (.) (.*)$')

# Store "item" kwenye "dict" under "key".
# The dictionary maps keys to lists of items.
# If there ni no list kila the key yet, it ni created.
#
eleza store(dict, key, item):
    ikiwa key kwenye dict:
        dict[key].append(item)
    isipokua:
        dict[key] = [item]

# Return a flattened version of a list of strings: the concatenation
# of its elements ukijumuisha intervening spaces.
#
eleza flat(list):
    s = ''
    kila item kwenye list:
        s = s + ' ' + item
    rudisha s[1:]

# Global variables mapping defined/undefined names to files na back.
#
file2undef = {}
def2file = {}
file2eleza = {}
undef2file = {}

# Read one input file na merge the data into the tables.
# Argument ni an open file.
#
eleza read_input(fp):
    wakati 1:
        s = fp.readline()
        ikiwa sio s:
            koma
        # If you get any output kutoka this line,
        # it ni probably caused by an unexpected input line:
        ikiwa matcher.search(s) < 0: s; endelea # Shouldn't happen
        (ra, rb), (r1a, r1b), (r2a, r2b), (r3a, r3b) = matcher.regs[:4]
        fn, name, type = s[r1a:r1b], s[r3a:r3b], s[r2a:r2b]
        ikiwa type kwenye definitions:
            store(def2file, name, fn)
            store(file2def, fn, name)
        lasivyo type kwenye externals:
            store(file2undef, fn, name)
            store(undef2file, name, fn)
        lasivyo sio type kwenye ignore:
            andika(fn + ':' + name + ': unknown type ' + type)

# Print all names that were undefined kwenye some module na where they are
# defined.
#
eleza printcallee():
    flist = sorted(file2undef.keys())
    kila filename kwenye flist:
        andika(filename + ':')
        elist = file2undef[filename]
        elist.sort()
        kila ext kwenye elist:
            ikiwa len(ext) >= 8:
                tabs = '\t'
            isipokua:
                tabs = '\t\t'
            ikiwa ext haiko kwenye def2file:
                andika('\t' + ext + tabs + ' *undefined')
            isipokua:
                andika('\t' + ext + tabs + flat(def2file[ext]))

# Print kila each module the names of the other modules that use it.
#
eleza printcaller():
    files = sorted(file2def.keys())
    kila filename kwenye files:
        callers = []
        kila label kwenye file2def[filename]:
            ikiwa label kwenye undef2file:
                callers = callers + undef2file[label]
        ikiwa callers:
            callers.sort()
            andika(filename + ':')
            lastfn = ''
            kila fn kwenye callers:
                ikiwa fn != lastfn:
                    andika('\t' + fn)
                lastfn = fn
        isipokua:
            andika(filename + ': unused')

# Print undefined names na where they are used.
#
eleza printundef():
    undefs = {}
    kila filename kwenye list(file2undef.keys()):
        kila ext kwenye file2undef[filename]:
            ikiwa ext haiko kwenye def2file:
                store(undefs, ext, filename)
    elist = sorted(undefs.keys())
    kila ext kwenye elist:
        andika(ext + ':')
        flist = sorted(undefs[ext])
        kila filename kwenye flist:
            andika('\t' + filename)

# Print warning messages about names defined kwenye more than one file.
#
eleza warndups():
    savestdout = sys.stdout
    sys.stdout = sys.stderr
    names = sorted(def2file.keys())
    kila name kwenye names:
        ikiwa len(def2file[name]) > 1:
            andika('warning:', name, 'multiply defined:', end=' ')
            andika(flat(def2file[name]))
    sys.stdout = savestdout

# Main program
#
eleza main():
    jaribu:
        optlist, args = getopt.getopt(sys.argv[1:], 'cdu')
    tatizo getopt.error:
        sys.stdout = sys.stderr
        andika('Usage:', os.path.basename(sys.argv[0]), end=' ')
        andika('[-cdu] [file] ...')
        andika('-c: andika callers per objectfile')
        andika('-d: andika callees per objectfile')
        andika('-u: andika usage of undefined symbols')
        andika('If none of -cdu ni specified, all are assumed.')
        andika('Use "nm -o" to generate the input')
        andika('e.g.: nm -o /lib/libc.a | objgraph')
        rudisha 1
    optu = optc = optd = 0
    kila opt, void kwenye optlist:
        ikiwa opt == '-u':
            optu = 1
        lasivyo opt == '-c':
            optc = 1
        lasivyo opt == '-d':
            optd = 1
    ikiwa optu == optc == optd == 0:
        optu = optc = optd = 1
    ikiwa sio args:
        args = ['-']
    kila filename kwenye args:
        ikiwa filename == '-':
            readinput(sys.stdin)
        isipokua:
            ukijumuisha open(filename) kama f:
                readinput(f)
    #
    warndups()
    #
    more = (optu + optc + optd > 1)
    ikiwa optd:
        ikiwa more:
            andika('---------------All callees------------------')
        printcallee()
    ikiwa optu:
        ikiwa more:
            andika('---------------Undefined callees------------')
        printundef()
    ikiwa optc:
        ikiwa more:
            andika('---------------All Callers------------------')
        printcaller()
    rudisha 0

# Call the main program.
# Use its rudisha value kama exit status.
# Catch interrupts to avoid stack trace.
#
ikiwa __name__ == '__main__':
    jaribu:
        sys.exit(main())
    tatizo KeyboardInterrupt:
        sys.exit(1)
