#! /usr/bin/env python3

# pdeps
#
# Find dependencies between a bunch of Python modules.
#
# Usage:
#       pdeps file1.py file2.py ...
#
# Output:
# Four tables separated by lines like '--- Closure ---':
# 1) Direct dependencies, listing which module imports which other modules
# 2) The inverse of (1)
# 3) Indirect dependencies, ama the closure of the above
# 4) The inverse of (3)
#
# To do:
# - command line options to select output type
# - option to automatically scan the Python library kila referenced modules
# - option to limit output to particular modules


agiza sys
agiza re
agiza os


# Main program
#
eleza main():
    args = sys.argv[1:]
    ikiwa sio args:
        andika('usage: pdeps file.py file.py ...')
        rudisha 2
    #
    table = {}
    kila arg kwenye args:
        process(arg, table)
    #
    andika('--- Uses ---')
    printresults(table)
    #
    andika('--- Used By ---')
    inv = inverse(table)
    printresults(inv)
    #
    andika('--- Closure of Uses ---')
    reach = closure(table)
    printresults(reach)
    #
    andika('--- Closure of Used By ---')
    invreach = inverse(reach)
    printresults(invreach)
    #
    rudisha 0


# Compiled regular expressions to search kila agiza statements
#
m_agiza = re.compile('^[ \t]*from[ \t]+([^ \t]+)[ \t]+')
m_kutoka = re.compile('^[ \t]*import[ \t]+([^#]+)')


# Collect data kutoka one file
#
eleza process(filename, table):
    ukijumuisha open(filename) kama fp:
        mod = os.path.basename(filename)
        ikiwa mod[-3:] == '.py':
            mod = mod[:-3]
        table[mod] = list = []
        wakati 1:
            line = fp.readline()
            ikiwa sio line: koma
            wakati line[-1:] == '\\':
                nextline = fp.readline()
                ikiwa sio nextline: koma
                line = line[:-1] + nextline
            m_found = m_import.match(line) ama m_from.match(line)
            ikiwa m_found:
                (a, b), (a1, b1) = m_found.regs[:2]
            isipokua: endelea
            words = line[a1:b1].split(',')
            # print '#', line, words
            kila word kwenye words:
                word = word.strip()
                ikiwa word haiko kwenye list:
                    list.append(word)


# Compute closure (this ni kwenye fact totally general)
#
eleza closure(table):
    modules = list(table.keys())
    #
    # Initialize reach ukijumuisha a copy of table
    #
    reach = {}
    kila mod kwenye modules:
        reach[mod] = table[mod][:]
    #
    # Iterate until no more change
    #
    change = 1
    wakati change:
        change = 0
        kila mod kwenye modules:
            kila mo kwenye reach[mod]:
                ikiwa mo kwenye modules:
                    kila m kwenye reach[mo]:
                        ikiwa m haiko kwenye reach[mod]:
                            reach[mod].append(m)
                            change = 1
    #
    rudisha reach


# Invert a table (this ni again totally general).
# All keys of the original table are made keys of the inverse,
# so there may be empty lists kwenye the inverse.
#
eleza inverse(table):
    inv = {}
    kila key kwenye table.keys():
        ikiwa key haiko kwenye inv:
            inv[key] = []
        kila item kwenye table[key]:
            store(inv, item, key)
    rudisha inv


# Store "item" kwenye "dict" under "key".
# The dictionary maps keys to lists of items.
# If there ni no list kila the key yet, it ni created.
#
eleza store(dict, key, item):
    ikiwa key kwenye dict:
        dict[key].append(item)
    isipokua:
        dict[key] = [item]


# Tabulate results neatly
#
eleza printresults(table):
    modules = sorted(table.keys())
    maxlen = 0
    kila mod kwenye modules: maxlen = max(maxlen, len(mod))
    kila mod kwenye modules:
        list = sorted(table[mod])
        andika(mod.ljust(maxlen), ':', end=' ')
        ikiwa mod kwenye list:
            andika('(*)', end=' ')
        kila ref kwenye list:
            andika(ref, end=' ')
        andika()


# Call main na honor exit status
ikiwa __name__ == '__main__':
    jaribu:
        sys.exit(main())
    tatizo KeyboardInterrupt:
        sys.exit(1)
