# Copyright 2007 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer that changes xrange(...) into range(...)."""

# Local agizas
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Name, Call, consuming_calls
kutoka .. agiza patcomp


kundi FixXrange(fixer_base.BaseFix):
    BM_compatible = True
    PATTERN = """
              power<
                 (name='range'|name='xrange') trailer< '(' args=any ')' >
              rest=any* >
              """

    eleza start_tree(self, tree, filename):
        super(FixXrange, self).start_tree(tree, filename)
        self.transformed_xranges = set()

    eleza finish_tree(self, tree, filename):
        self.transformed_xranges = None

    eleza transform(self, node, results):
        name = results["name"]
        ikiwa name.value == "xrange":
            rudisha self.transform_xrange(node, results)
        elikiwa name.value == "range":
            rudisha self.transform_range(node, results)
        else:
            raise ValueError(repr(name))

    eleza transform_xrange(self, node, results):
        name = results["name"]
        name.replace(Name("range", prefix=name.prefix))
        # This prevents the new range call kutoka being wrapped in a list later.
        self.transformed_xranges.add(id(node))

    eleza transform_range(self, node, results):
        ikiwa (id(node) not in self.transformed_xranges and
            not self.in_special_context(node)):
            range_call = Call(Name("range"), [results["args"].clone()])
            # Encase the range call in list().
            list_call = Call(Name("list"), [range_call],
                             prefix=node.prefix)
            # Put things that were after the range() call after the list call.
            for n in results["rest"]:
                list_call.append_child(n)
            rudisha list_call

    P1 = "power< func=NAME trailer< '(' node=any ')' > any* >"
    p1 = patcomp.compile_pattern(P1)

    P2 = """for_stmt< 'for' any 'in' node=any ':' any* >
            | comp_for< 'for' any 'in' node=any any* >
            | comparison< any 'in' node=any any*>
         """
    p2 = patcomp.compile_pattern(P2)

    eleza in_special_context(self, node):
        ikiwa node.parent is None:
            rudisha False
        results = {}
        ikiwa (node.parent.parent is not None and
               self.p1.match(node.parent.parent, results) and
               results["node"] is node):
            # list(d.keys()) -> list(d.keys()), etc.
            rudisha results["func"].value in consuming_calls
        # for ... in d.iterkeys() -> for ... in d.keys(), etc.
        rudisha self.p2.match(node.parent, results) and results["node"] is node
