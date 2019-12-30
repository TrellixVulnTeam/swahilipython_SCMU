"""
Input kila test_profile.py na test_cprofile.py.

IMPORTANT: This stuff ni touchy. If you modify anything above the
test kundi you'll have to regenerate the stats by running the two
test files.

*ALL* NUMBERS kwenye the expected output are relevant.  If you change
the formatting of pstats, please don't just regenerate the expected
output without checking very carefully that sio a single number has
changed.
"""

agiza sys

# In order to have reproducible time, we simulate a timer kwenye the global
# variable 'TICKS', which represents simulated time kwenye milliseconds.
# (We can't use a helper function increment the timer since it would be
# included kwenye the profile na would appear to consume all the time.)
TICKS = 42000

eleza timer():
    rudisha TICKS

eleza testfunc():
    # 1 call
    # 1000 ticks total: 270 ticks local, 730 ticks kwenye subfunctions
    global TICKS
    TICKS += 99
    helper()                            # 300
    helper()                            # 300
    TICKS += 171
    factorial(14)                       # 130

eleza factorial(n):
    # 23 calls total
    # 170 ticks total, 150 ticks local
    # 3 primitive calls, 130, 20 na 20 ticks total
    # including 116, 17, 17 ticks local
    global TICKS
    ikiwa n > 0:
        TICKS += n
        rudisha mul(n, factorial(n-1))
    isipokua:
        TICKS += 11
        rudisha 1

eleza mul(a, b):
    # 20 calls
    # 1 tick, local
    global TICKS
    TICKS += 1
    rudisha a * b

eleza helper():
    # 2 calls
    # 300 ticks total: 20 ticks local, 260 ticks kwenye subfunctions
    global TICKS
    TICKS += 1
    helper1()                           # 30
    TICKS += 2
    helper1()                           # 30
    TICKS += 6
    helper2()                           # 50
    TICKS += 3
    helper2()                           # 50
    TICKS += 2
    helper2()                           # 50
    TICKS += 5
    helper2_indirect()                  # 70
    TICKS += 1

eleza helper1():
    # 4 calls
    # 30 ticks total: 29 ticks local, 1 tick kwenye subfunctions
    global TICKS
    TICKS += 10
    hasattr(C(), "foo")                 # 1
    TICKS += 19
    lst = []
    lst.append(42)                      # 0
    sys.exc_info()                      # 0

eleza helper2_indirect():
    helper2()                           # 50
    factorial(3)                        # 20

eleza helper2():
    # 8 calls
    # 50 ticks local: 39 ticks local, 11 ticks kwenye subfunctions
    global TICKS
    TICKS += 11
    hasattr(C(), "bar")                 # 1
    TICKS += 13
    subhelper()                         # 10
    TICKS += 15

eleza subhelper():
    # 8 calls
    # 10 ticks total: 8 ticks local, 2 ticks kwenye subfunctions
    global TICKS
    TICKS += 2
    kila i kwenye range(2):                  # 0
        jaribu:
            C().foo                     # 1 x 2
        except AttributeError:
            TICKS += 3                  # 3 x 2

kundi C:
    eleza __getattr__(self, name):
        # 28 calls
        # 1 tick, local
        global TICKS
        TICKS += 1
         ashiria AttributeError
