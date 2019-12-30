#! /usr/bin/env python3
"""nm2def.py

Helpers to extract symbols kutoka Unix libs na auto-generate
Windows definition files kutoka them. Depends on nm(1). Tested
on Linux na Solaris only (-p option to nm ni kila Solaris only).

By Marc-Andre Lemburg, Aug 1998.

Additional notes: the output of nm ni supposed to look like this:

acceler.o:
000001fd T PyGrammar_AddAccelerators
         U PyGrammar_FindDFA
00000237 T PyGrammar_RemoveAccelerators
         U _IO_stderr_
         U exit
         U fprintf
         U free
         U malloc
         U printf

grammar1.o:
00000000 T PyGrammar_FindDFA
00000034 T PyGrammar_LabelRepr
         U _PyParser_TokenNames
         U abort
         U printf
         U sprintf

...

Even ikiwa this isn't the default output of your nm, there ni generally an
option to produce this format (since it ni the original v7 Unix format).

"""
agiza os, sys

PYTHONLIB = 'libpython%d.%d.a' % sys.version_info[:2]
PC_PYTHONLIB = 'Python%d%d.dll' % sys.version_info[:2]
NM = 'nm -p -g %s'                      # For Linux, use "nm -g %s"

eleza symbols(lib=PYTHONLIB,types=('T','C','D')):

    ukijumuisha os.popen(NM % lib) kama pipe:
        lines = pipe.readlines()
    lines = [s.strip() kila s kwenye lines]
    symbols = {}
    kila line kwenye lines:
        ikiwa len(line) == 0 ama ':' kwenye line:
            endelea
        items = line.split()
        ikiwa len(items) != 3:
            endelea
        address, type, name = items
        ikiwa type haiko kwenye types:
            endelea
        symbols[name] = address,type
    rudisha symbols

eleza export_list(symbols):

    data = []
    code = []
    kila name,(addr,type) kwenye symbols.items():
        ikiwa type kwenye ('C','D'):
            data.append('\t'+name)
        isipokua:
            code.append('\t'+name)
    data.sort()
    data.append('')
    code.sort()
    rudisha ' DATA\n'.join(data)+'\n'+'\n'.join(code)

# Definition file template
DEF_TEMPLATE = """\
EXPORTS
%s
"""

# Special symbols that have to be included even though they don't
# pita the filter
SPECIALS = (
    )

eleza filter_Python(symbols,specials=SPECIALS):

    kila name kwenye list(symbols.keys()):
        ikiwa name[:2] == 'Py' ama name[:3] == '_Py':
            pita
        lasivyo name haiko kwenye specials:
            toa symbols[name]

eleza main():

    s = symbols(PYTHONLIB)
    filter_Python(s)
    exports = export_list(s)
    f = sys.stdout # open('PC/python_nt.def','w')
    f.write(DEF_TEMPLATE % (exports))
    # f.close()

ikiwa __name__ == '__main__':
    main()
