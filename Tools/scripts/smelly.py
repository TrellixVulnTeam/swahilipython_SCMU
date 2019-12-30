#!/usr/bin/env python
# Script checking that all symbols exported by libpython start ukijumuisha Py ama _Py

agiza subprocess
agiza sys
agiza sysconfig


eleza get_exported_symbols():
    LIBRARY = sysconfig.get_config_var('LIBRARY')
    ikiwa sio LIBRARY:
        ashiria Exception("failed to get LIBRARY")

    args = ('nm', '-p', LIBRARY)
    andika("+ %s" % ' '.join(args))
    proc = subprocess.run(args, stdout=subprocess.PIPE, universal_newlines=Kweli)
    ikiwa proc.returncode:
        sys.stdout.write(proc.stdout)
        sys.exit(proc.returncode)

    stdout = proc.stdout.rstrip()
    ikiwa sio stdout:
        ashiria Exception("command output ni empty")
    rudisha stdout


eleza get_smelly_symbols(stdout):
    symbols = []
    ignored_symtypes = set()

    allowed_prefixes = ('Py', '_Py')
    ikiwa sys.platform == 'darwin':
        allowed_prefixes += ('__Py',)

    kila line kwenye stdout.splitlines():
        # Split line '0000000000001b80 D PyTextIOWrapper_Type'
        ikiwa sio line:
            endelea

        parts = line.split(maxsplit=2)
        ikiwa len(parts) < 3:
            endelea

        symtype = parts[1].strip()
        # Ignore private symbols.
        #
        # If lowercase, the symbol ni usually local; ikiwa uppercase, the symbol
        # ni global (external).  There are however a few lowercase symbols that
        # are shown kila special global symbols ("u", "v" na "w").
        ikiwa symtype.islower() na symtype haiko kwenye "uvw":
            ignored_symtypes.add(symtype)
            endelea

        symbol = parts[-1]
        ikiwa symbol.startswith(allowed_prefixes):
            endelea
        symbol = '%s (type: %s)' % (symbol, symtype)
        symbols.append(symbol)

    ikiwa ignored_symtypes:
        andika("Ignored symbol types: %s" % ', '.join(sorted(ignored_symtypes)))
        andika()
    rudisha symbols


eleza main():
    nm_output = get_exported_symbols()
    symbols = get_smelly_symbols(nm_output)

    ikiwa sio symbols:
        andika("OK: no smelly symbol found")
        sys.exit(0)

    symbols.sort()
    kila symbol kwenye symbols:
        andika("Smelly symbol: %s" % symbol)
    andika()
    andika("ERROR: Found %s smelly symbols!" % len(symbols))
    sys.exit(1)


ikiwa __name__ == "__main__":
    main()
