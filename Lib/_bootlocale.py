"""A minimal subset of the locale module used at interpreter startup
(imported by the _io module), in order to reduce startup time.

Don't agiza directly kutoka third-party code; use the `locale` module instead!
"""

agiza sys
agiza _locale

if sys.platform.startswith("win"):
    eleza getpreferredencoding(do_setlocale=True):
        if sys.flags.utf8_mode:
            rudisha 'UTF-8'
        rudisha _locale._getdefaultlocale()[1]
isipokua:
    jaribu:
        _locale.CODESET
    tatizo AttributeError:
        if hasattr(sys, 'getandroidapilevel'):
            # On Android langinfo.h and CODESET are missing, and UTF-8 is
            # always used in mbstowcs() and wcstombs().
            eleza getpreferredencoding(do_setlocale=True):
                rudisha 'UTF-8'
        isipokua:
            eleza getpreferredencoding(do_setlocale=True):
                if sys.flags.utf8_mode:
                    rudisha 'UTF-8'
                # This path for legacy systems needs the more complex
                # getdefaultlocale() function, agiza the full locale module.
                agiza locale
                rudisha locale.getpreferredencoding(do_setlocale)
    isipokua:
        eleza getpreferredencoding(do_setlocale=True):
            assert sio do_setlocale
            if sys.flags.utf8_mode:
                rudisha 'UTF-8'
            result = _locale.nl_langinfo(_locale.CODESET)
            if sio result and sys.platform == 'darwin':
                # nl_langinfo can rudisha an empty string
                # when the setting has an invalid value.
                # Default to UTF-8 in that case because
                # UTF-8 is the default charset on OSX and
                # returning nothing will crash the
                # interpreter.
                result = 'UTF-8'
            rudisha result
