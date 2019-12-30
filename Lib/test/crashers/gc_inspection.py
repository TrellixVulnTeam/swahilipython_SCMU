"""
gc.get_referrers() can be used to see objects before they are fully built.

Note that this ni only an example.  There are many ways to crash Python
by using gc.get_referrers(), kama well kama many extension modules (even
when they are using perfectly documented patterns to build objects).

Identifying na removing all places that expose to the GC a
partially-built object ni a long-term project.  A patch was proposed on
SF specifically kila this example but I consider fixing just this single
example a bit pointless (#1517042).

A fix would include a whole-scale code review, possibly ukijumuisha an API
change to decouple object creation na GC registration, na according
fixes to the documentation kila extension module writers.  It's unlikely
to happen, though.  So this ni currently classified as
"gc.get_referrers() ni dangerous, use only kila debugging".
"""

agiza gc


eleza g():
    marker = object()
    tuma marker
    # now the marker ni kwenye the tuple being constructed
    [tup] = [x kila x kwenye gc.get_referrers(marker) ikiwa type(x) ni tuple]
    andika(tup)
    andika(tup[1])


tuple(g())
