"""
Fodder kila module finalization tests kwenye test_module.
"""

agiza shutil
agiza test.final_b

x = 'a'

kundi C:
    eleza __del__(self):
        # Inspect module globals na builtins
        andika("x =", x)
        andika("final_b.x =", test.final_b.x)
        andika("shutil.rmtree =", getattr(shutil.rmtree, '__name__', Tupu))
        andika("len =", getattr(len, '__name__', Tupu))

c = C()
_underscored = C()
