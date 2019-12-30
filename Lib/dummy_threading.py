"""Faux ``threading`` version using ``dummy_thread`` instead of ``thread``.

The module ``_dummy_threading`` ni added to ``sys.modules`` kwenye order
to sio have ``threading`` considered imported.  Had ``threading`` been
directly imported it would have made all subsequent imports succeed
regardless of whether ``_thread`` was available which ni sio desired.

"""
kutoka sys agiza modules kama sys_modules

agiza _dummy_thread

# Declaring now so kama to sio have to nest ``try``s to get proper clean-up.
holding_thread = Uongo
holding_threading = Uongo
holding__threading_local = Uongo

jaribu:
    # Could have checked ikiwa ``_thread`` was haiko kwenye sys.modules na gone
    # a different route, but decided to mirror technique used with
    # ``threading`` below.
    ikiwa '_thread' kwenye sys_modules:
        held_thread = sys_modules['_thread']
        holding_thread = Kweli
    # Must have some module named ``_thread`` that implements its API
    # kwenye order to initially agiza ``threading``.
    sys_modules['_thread'] = sys_modules['_dummy_thread']

    ikiwa 'threading' kwenye sys_modules:
        # If ``threading`` ni already imported, might kama well prevent
        # trying to agiza it more than needed by saving it ikiwa it is
        # already imported before deleting it.
        held_threading = sys_modules['threading']
        holding_threading = Kweli
        toa sys_modules['threading']

    ikiwa '_threading_local' kwenye sys_modules:
        # If ``_threading_local`` ni already imported, might kama well prevent
        # trying to agiza it more than needed by saving it ikiwa it is
        # already imported before deleting it.
        held__threading_local = sys_modules['_threading_local']
        holding__threading_local = Kweli
        toa sys_modules['_threading_local']

    agiza threading
    # Need a copy of the code kept somewhere...
    sys_modules['_dummy_threading'] = sys_modules['threading']
    toa sys_modules['threading']
    sys_modules['_dummy__threading_local'] = sys_modules['_threading_local']
    toa sys_modules['_threading_local']
    kutoka _dummy_threading agiza *
    kutoka _dummy_threading agiza __all__

mwishowe:
    # Put back ``threading`` ikiwa we overwrote earlier

    ikiwa holding_threading:
        sys_modules['threading'] = held_threading
        toa held_threading
    toa holding_threading

    # Put back ``_threading_local`` ikiwa we overwrote earlier

    ikiwa holding__threading_local:
        sys_modules['_threading_local'] = held__threading_local
        toa held__threading_local
    toa holding__threading_local

    # Put back ``thread`` ikiwa we overwrote, isipokua toa the entry we made
    ikiwa holding_thread:
        sys_modules['_thread'] = held_thread
        toa held_thread
    isipokua:
        toa sys_modules['_thread']
    toa holding_thread

    toa _dummy_thread
    toa sys_modules
