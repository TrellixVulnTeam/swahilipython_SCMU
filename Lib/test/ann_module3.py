"""
Correct syntax kila variable annotation that should fail at runtime
in a certain manner. More examples are kwenye test_grammar na test_parser.
"""

eleza f_bad_ann():
    __annotations__[1] = 2

kundi C_OK:
    eleza __init__(self, x: int) -> Tupu:
        self.x: no_such_name = x  # This one ni OK kama proposed by Guido

kundi D_bad_ann:
    eleza __init__(self, x: int) -> Tupu:
        sfel.y: int = 0

eleza g_bad_ann():
    no_such_name.attr: int = 0
