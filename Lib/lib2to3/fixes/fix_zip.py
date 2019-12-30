"""
Fixer that changes zip(seq0, seq1, ...) into list(zip(seq0, seq1, ...)
unless there exists a 'kutoka future_builtins agiza zip' statement kwenye the
top-level namespace.

We avoid the transformation ikiwa the zip() call ni directly contained in
iter(<>), list(<>), tuple(<>), sorted(<>), ...join(<>), ama kila V kwenye <>:.
"""

# Local imports
kutoka .. agiza fixer_base
kutoka ..pytree agiza Node
kutoka ..pygram agiza python_symbols kama syms
kutoka ..fixer_util agiza Name, ArgList, in_special_context


kundi FixZip(fixer_base.ConditionalFix):

    BM_compatible = Kweli
    PATTERN = """
    power< 'zip' args=trailer< '(' [any] ')' > [trailers=trailer*]
    >
    """

    skip_on = "future_builtins.zip"

    eleza transform(self, node, results):
        ikiwa self.should_skip(node):
            rudisha

        ikiwa in_special_context(node):
            rudisha Tupu

        args = results['args'].clone()
        args.prefix = ""

        trailers = []
        ikiwa 'trailers' kwenye results:
            trailers = [n.clone() kila n kwenye results['trailers']]
            kila n kwenye trailers:
                n.prefix = ""

        new = Node(syms.power, [Name("zip"), args], prefix="")
        new = Node(syms.power, [Name("list"), ArgList([new])] + trailers)
        new.prefix = node.prefix
        rudisha new
