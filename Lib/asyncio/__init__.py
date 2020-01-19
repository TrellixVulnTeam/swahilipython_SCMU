"""The asyncio package, tracking PEP 3156."""

# flake8: noqa

agiza sys

# This relies on each of the submodules having an __all__ variable.
kutoka .base_events agiza *
kutoka .coroutines agiza *
kutoka .events agiza *
kutoka .exceptions agiza *
kutoka .futures agiza *
kutoka .locks agiza *
kutoka .protocols agiza *
kutoka .runners agiza *
kutoka .queues agiza *
kutoka .streams agiza *
kutoka .subprocess agiza *
kutoka .tasks agiza *
kutoka .transports agiza *

# Exposed for _asynciomodule.c to implement now deprecated
# Task.all_tasks() method.  This function will be removed in 3.9.
kutoka .tasks agiza _all_tasks_compat  # NoQA

__all__ = (base_events.__all__ +
           coroutines.__all__ +
           events.__all__ +
           exceptions.__all__ +
           futures.__all__ +
           locks.__all__ +
           protocols.__all__ +
           runners.__all__ +
           queues.__all__ +
           streams.__all__ +
           subprocess.__all__ +
           tasks.__all__ +
           transports.__all__)

ikiwa sys.platform == 'win32':  # pragma: no cover
    kutoka .windows_events agiza *
    __all__ += windows_events.__all__
isipokua:
    kutoka .unix_events agiza *  # pragma: no cover
    __all__ += unix_events.__all__
