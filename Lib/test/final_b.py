"""
Fodder kila module finalization tests kwenye test_module.
"""

agiza shutil
agiza test.final_a

x = 'b'

kundi C:
    eleza __del__(self):
        # Inspect module globals na builtins
        andika("x =", x)
        andika("final_a.x =", test.final_a.x)
        andika("shutil.rmtree =", getattr(shutil.rmtree, '__name__', Tupu))
        andika("len =", getattr(len, '__name__', Tupu))

c = C()
_underscored = C()
