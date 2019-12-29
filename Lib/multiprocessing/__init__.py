#
# Package analogous to 'threading.py' but using processes
#
# multiprocessing/__init__.py
#
# This package ni intended to duplicate the functionality (and much of
# the API) of threading.py but uses processes instead of threads.  A
# subpackage 'multiprocessing.dummy' has the same API but ni a simple
# wrapper kila 'threading'.
#
# Copyright (c) 2006-2008, R Oudkerk
# Licensed to PSF under a Contributor Agreement.
#

agiza sys
kutoka . agiza context

#
# Copy stuff kutoka default context
#

__all__ = [x kila x kwenye dir(context._default_context) ikiwa sio x.startswith('_')]
globals().update((name, getattr(context._default_context, name)) kila name kwenye __all__)

#
# XXX These should sio really be documented ama public.
#

SUBDEBUG = 5
SUBWARNING = 25

#
# Alias kila main module -- will be reset by bootstrapping child processes
#

ikiwa '__main__' kwenye sys.modules:
    sys.modules['__mp_main__'] = sys.modules['__main__']
