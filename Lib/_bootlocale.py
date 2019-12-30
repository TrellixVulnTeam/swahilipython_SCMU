"""A minimal subset of the locale module used at interpreter startup
(imported by the _io module), kwenye order to reduce startup time.

Don't agiza directly kutoka third-party code; use the `locale` module instead!
"""

agiza sys
agiza _locale

ikiwa sys.platform.startswith("win"):
    eleza getpreferredencoding(do_setlocale=Kweli):
        ikiwa sys.flags.utf8_mode:
            rudisha 'UTF-8'
        rudisha _locale._getdefaultlocale()[1]
isipokua:
    jaribu:
        _locale.CODESET
    except AttributeError:
        ikiwa hasattr(sys, 'getandroidapilevel'):
            # On Android langinfo.h na CODESET are missing, na UTF-8 is
            # always used kwenye mbstowcs() na wcstombs().
            eleza getpreferredencoding(do_setlocale=Kweli):
                rudisha 'UTF-8'
        isipokua:
            eleza getpreferredencoding(do_setlocale=Kweli):
                ikiwa sys.flags.utf8_mode:
                    rudisha 'UTF-8'
                # This path kila legacy systems needs the more complex
                # getdefaultlocale() function, agiza the full locale module.
                agiza locale
                rudisha locale.getpreferredencoding(do_setlocale)
    isipokua:
        eleza getpreferredencoding(do_setlocale=Kweli):
            assert sio do_setlocale
            ikiwa sys.flags.utf8_mode:
                rudisha 'UTF-8'
            result = _locale.nl_langinfo(_locale.CODESET)
            ikiwa sio result na sys.platform == 'darwin':
                # nl_langinfo can rudisha an empty string
                # when the setting has an invalid value.
                # Default to UTF-8 kwenye that case because
                # UTF-8 ni the default charset on OSX and
                # returning nothing will crash the
                # interpreter.
                result = 'UTF-8'
            rudisha result
