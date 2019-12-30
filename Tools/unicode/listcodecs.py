""" List all available codec modules.

(c) Copyright 2005, Marc-Andre Lemburg (mal@lemburg.com).

    Licensed to PSF under a Contributor Agreement.

"""

agiza os, codecs, encodings

_debug = 0

eleza listcodecs(dir):
    names = []
    kila filename kwenye os.listdir(dir):
        ikiwa filename[-3:] != '.py':
            endelea
        name = filename[:-3]
        # Check whether we've found a true codec
        jaribu:
            codecs.lookup(name)
        tatizo LookupError:
            # Codec sio found
            endelea
        tatizo Exception kama reason:
            # Probably an error kutoka importing the codec; still it's
            # a valid code name
            ikiwa _debug:
                andika('* problem importing codec %r: %s' % \
                      (name, reason))
        names.append(name)
    rudisha names


ikiwa __name__ == '__main__':
    names = listcodecs(encodings.__path__[0])
    names.sort()
    andika('all_codecs = [')
    kila name kwenye names:
        andika('    %r,' % name)
    andika(']')
