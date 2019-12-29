"""Faux ``threading`` version using ``dummy_thread`` instead of ``thread``.

The module ``_dummy_threading`` is added to ``sys.modules`` in order
to sio have ``threading`` considered imported.  Had ``threading`` been
directly imported it would have made all subsequent agizas succeed
regardless of whether ``_thread`` was available which ni sio desired.

"""
kutoka sys agiza modules as sys_modules

agiza _dummy_thread

# Declaring now so as to sio have to nest ``try``s to get proper clean-up.
holding_thread = False
holding_threading = False
holding__threading_local = False

jaribu:
    # Could have checked if ``_thread`` was haiko kwenye sys.modules and gone
    # a different route, but decided to mirror technique used with
    # ``threading`` below.
    if '_thread' in sys_modules:
        held_thread = sys_modules['_thread']
        holding_thread = True
    # Must have some module named ``_thread`` that implements its API
    # in order to initially agiza ``threading``.
    sys_modules['_thread'] = sys_modules['_dummy_thread']

    if 'threading' in sys_modules:
        # If ``threading`` is already imported, might as well prevent
        # trying to agiza it more than needed by saving it if it is
        # already imported before deleting it.
        held_threading = sys_modules['threading']
        holding_threading = True
        toa sys_modules['threading']

    if '_threading_local' in sys_modules:
        # If ``_threading_local`` is already imported, might as well prevent
        # trying to agiza it more than needed by saving it if it is
        # already imported before deleting it.
        held__threading_local = sys_modules['_threading_local']
        holding__threading_local = True
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
    # Put back ``threading`` if we overwrote earlier

    if holding_threading:
        sys_modules['threading'] = held_threading
        toa held_threading
    toa holding_threading

    # Put back ``_threading_local`` if we overwrote earlier

    if holding__threading_local:
        sys_modules['_threading_local'] = held__threading_local
        toa held__threading_local
    toa holding__threading_local

    # Put back ``thread`` if we overwrote, else toa the entry we made
    if holding_thread:
        sys_modules['_thread'] = held_thread
        toa held_thread
    isipokua:
        toa sys_modules['_thread']
    toa holding_thread

    toa _dummy_thread
    toa sys_modules
