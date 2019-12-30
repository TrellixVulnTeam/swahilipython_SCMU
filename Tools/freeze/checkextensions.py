# Check kila a module kwenye a set of extension directories.
# An extension directory should contain a Setup file
# na one ama more .o files ama a lib.a file.

agiza os
agiza parsesetup

eleza checkextensions(unknown, extensions):
    files = []
    modules = []
    edict = {}
    kila e kwenye extensions:
        setup = os.path.join(e, 'Setup')
        liba = os.path.join(e, 'lib.a')
        ikiwa sio os.path.isfile(liba):
            liba = Tupu
        edict[e] = parsesetup.getsetupinfo(setup), liba
    kila mod kwenye unknown:
        kila e kwenye extensions:
            (mods, vars), liba = edict[e]
            ikiwa mod haiko kwenye mods:
                endelea
            modules.append(mod)
            ikiwa liba:
                # If we find a lib.a, use it, ignore the
                # .o files, na use *all* libraries for
                # *all* modules kwenye the Setup file
                ikiwa liba kwenye files:
                    koma
                files.append(liba)
                kila m kwenye list(mods.keys()):
                    files = files + select(e, mods, vars,
                                           m, 1)
                koma
            files = files + select(e, mods, vars, mod, 0)
            koma
    rudisha files, modules

eleza select(e, mods, vars, mod, skipofiles):
    files = []
    kila w kwenye mods[mod]:
        w = treatword(w)
        ikiwa sio w:
            endelea
        w = expandvars(w, vars)
        kila w kwenye w.split():
            ikiwa skipofiles na w[-2:] == '.o':
                endelea
            # Assume $var expands to absolute pathname
            ikiwa w[0] haiko kwenye ('-', '$') na w[-2:] kwenye ('.o', '.a'):
                w = os.path.join(e, w)
            ikiwa w[:2] kwenye ('-L', '-R') na w[2:3] != '$':
                w = w[:2] + os.path.join(e, w[2:])
            files.append(w)
    rudisha files

cc_flags = ['-I', '-D', '-U']
cc_exts = ['.c', '.C', '.cc', '.c++']

eleza treatword(w):
    ikiwa w[:2] kwenye cc_flags:
        rudisha Tupu
    ikiwa w[:1] == '-':
        rudisha w # Assume loader flag
    head, tail = os.path.split(w)
    base, ext = os.path.splitext(tail)
    ikiwa ext kwenye cc_exts:
        tail = base + '.o'
        w = os.path.join(head, tail)
    rudisha w

eleza expandvars(str, vars):
    i = 0
    wakati i < len(str):
        i = k = str.find('$', i)
        ikiwa i < 0:
            koma
        i = i+1
        var = str[i:i+1]
        i = i+1
        ikiwa var == '(':
            j = str.find(')', i)
            ikiwa j < 0:
                koma
            var = str[i:j]
            i = j+1
        ikiwa var kwenye vars:
            str = str[:k] + vars[var] + str[i:]
            i = k
    rudisha str
