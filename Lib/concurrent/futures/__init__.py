# Copyright 2009 Brian Quinlan. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Execute computations asynchronously using threads ama processes."""

__author__ = 'Brian Quinlan (brian@sweetapp.com)'

kutoka concurrent.futures._base agiza (FIRST_COMPLETED,
                                      FIRST_EXCEPTION,
                                      ALL_COMPLETED,
                                      CancelledError,
                                      TimeoutError,
                                      InvalidStateError,
                                      BrokenExecutor,
                                      Future,
                                      Executor,
                                      wait,
                                      as_completed)

__all__ = (
    'FIRST_COMPLETED',
    'FIRST_EXCEPTION',
    'ALL_COMPLETED',
    'CancelledError',
    'TimeoutError',
    'BrokenExecutor',
    'Future',
    'Executor',
    'wait',
    'as_completed',
    'ProcessPoolExecutor',
    'ThreadPoolExecutor',
)


eleza __dir__():
    rudisha __all__ + ('__author__', '__doc__')


eleza __getattr__(name):
    global ProcessPoolExecutor, ThreadPoolExecutor

    ikiwa name == 'ProcessPoolExecutor':
        kutoka .process agiza ProcessPoolExecutor as pe
        ProcessPoolExecutor = pe
        rudisha pe

    ikiwa name == 'ThreadPoolExecutor':
        kutoka .thread agiza ThreadPoolExecutor as te
        ThreadPoolExecutor = te
        rudisha te

     ashiria AttributeError(f"module {__name__} has no attribute {name}")
