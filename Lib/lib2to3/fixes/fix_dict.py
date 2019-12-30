# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer kila dict methods.

d.keys() -> list(d.keys())
d.items() -> list(d.items())
d.values() -> list(d.values())

d.iterkeys() -> iter(d.keys())
d.iteritems() -> iter(d.items())
d.itervalues() -> iter(d.values())

d.viewkeys() -> d.keys()
d.viewitems() -> d.items()
d.viewvalues() -> d.values()

Except kwenye certain very specific contexts: the iter() can be dropped
when the context ni list(), sorted(), iter() ama for...in; the list()
can be dropped when the context ni list() ama sorted() (but sio iter()
or for...in!). Special contexts that apply to both: list(), sorted(), tuple()
set(), any(), all(), sum().

Note: iter(d.keys()) could be written kama iter(d) but since the
original d.iterkeys() was also redundant we don't fix this.  And there
are (rare) contexts where it makes a difference (e.g. when pitaing it
as an argument to a function that introspects the argument).
"""

# Local agizas
kutoka .. agiza pytree
kutoka .. agiza patcomp
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Name, Call, Dot
kutoka .. agiza fixer_util


iter_exempt = fixer_util.consuming_calls | {"iter"}


kundi FixDict(fixer_base.BaseFix):
    BM_compatible = Kweli

    PATTERN = """
    power< head=any+
         trailer< '.' method=('keys'|'items'|'values'|
                              'iterkeys'|'iteritems'|'itervalues'|
                              'viewkeys'|'viewitems'|'viewvalues') >
         parens=trailer< '(' ')' >
         tail=any*
    >
    """

    eleza transform(self, node, results):
        head = results["head"]
        method = results["method"][0] # Extract node kila method name
        tail = results["tail"]
        syms = self.syms
        method_name = method.value
        isiter = method_name.startswith("iter")
        isview = method_name.startswith("view")
        ikiwa isiter ama isview:
            method_name = method_name[4:]
        assert method_name kwenye ("keys", "items", "values"), repr(method)
        head = [n.clone() kila n kwenye head]
        tail = [n.clone() kila n kwenye tail]
        special = sio tail na self.in_special_context(node, isiter)
        args = head + [pytree.Node(syms.trailer,
                                   [Dot(),
                                    Name(method_name,
                                         prefix=method.prefix)]),
                       results["parens"].clone()]
        new = pytree.Node(syms.power, args)
        ikiwa sio (special ama isview):
            new.prefix = ""
            new = Call(Name("iter" ikiwa isiter isipokua "list"), [new])
        ikiwa tail:
            new = pytree.Node(syms.power, [new] + tail)
        new.prefix = node.prefix
        rudisha new

    P1 = "power< func=NAME trailer< '(' node=any ')' > any* >"
    p1 = patcomp.compile_pattern(P1)

    P2 = """for_stmt< 'for' any 'in' node=any ':' any* >
            | comp_for< 'for' any 'in' node=any any* >
         """
    p2 = patcomp.compile_pattern(P2)

    eleza in_special_context(self, node, isiter):
        ikiwa node.parent ni Tupu:
            rudisha Uongo
        results = {}
        ikiwa (node.parent.parent ni sio Tupu na
               self.p1.match(node.parent.parent, results) na
               results["node"] ni node):
            ikiwa isiter:
                # iter(d.iterkeys()) -> iter(d.keys()), etc.
                rudisha results["func"].value kwenye iter_exempt
            isipokua:
                # list(d.keys()) -> list(d.keys()), etc.
                rudisha results["func"].value kwenye fixer_util.consuming_calls
        ikiwa sio isiter:
            rudisha Uongo
        # kila ... kwenye d.iterkeys() -> kila ... kwenye d.keys(), etc.
        rudisha self.p2.match(node.parent, results) na results["node"] ni node
