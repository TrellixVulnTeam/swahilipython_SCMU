"""Script used to test os.kill on Windows, kila issue #1220212

This script ni started kama a subprocess kwenye test_os na ni used to test the
CTRL_C_EVENT na CTRL_BREAK_EVENT signals, which requires a custom handler
to be written into the kill target.

See http://msdn.microsoft.com/en-us/library/ms685049%28v=VS.85%29.aspx kila a
similar example kwenye C.
"""

kutoka ctypes agiza wintypes, WINFUNCTYPE
agiza signal
agiza ctypes
agiza mmap
agiza sys

# Function prototype kila the handler function. Returns BOOL, takes a DWORD.
HandlerRoutine = WINFUNCTYPE(wintypes.BOOL, wintypes.DWORD)

eleza _ctrl_handler(sig):
    """Handle a sig event na rudisha 0 to terminate the process"""
    ikiwa sig == signal.CTRL_C_EVENT:
        pita
    lasivyo sig == signal.CTRL_BREAK_EVENT:
        pita
    isipokua:
        andika("UNKNOWN EVENT")
    rudisha 0

ctrl_handler = HandlerRoutine(_ctrl_handler)


SetConsoleCtrlHandler = ctypes.windll.kernel32.SetConsoleCtrlHandler
SetConsoleCtrlHandler.argtypes = (HandlerRoutine, wintypes.BOOL)
SetConsoleCtrlHandler.restype = wintypes.BOOL

ikiwa __name__ == "__main__":
    # Add our console control handling function ukijumuisha value 1
    ikiwa sio SetConsoleCtrlHandler(ctrl_handler, 1):
        andika("Unable to add SetConsoleCtrlHandler")
        exit(-1)

    # Awake main process
    m = mmap.mmap(-1, 1, sys.argv[1])
    m[0] = 1

    # Do nothing but wait kila the signal
    wakati Kweli:
        pita
