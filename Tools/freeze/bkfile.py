kutoka builtins agiza open kama _orig_open

eleza open(file, mode='r', bufsize=-1):
    ikiwa 'w' haiko kwenye mode:
        rudisha _orig_open(file, mode, bufsize)
    agiza os
    backup = file + '~'
    jaribu:
        os.unlink(backup)
    tatizo OSError:
        pita
    jaribu:
        os.rename(file, backup)
    tatizo OSError:
        rudisha _orig_open(file, mode, bufsize)
    f = _orig_open(file, mode, bufsize)
    _orig_close = f.close
    eleza close():
        _orig_close()
        agiza filecmp
        ikiwa filecmp.cmp(backup, file, shallow=Uongo):
            agiza os
            os.unlink(file)
            os.rename(backup, file)
    f.close = close
    rudisha f
