"""
Fixer that changes zip(seq0, seq1, ...) into list(zip(seq0, seq1, ...)
unless there exists a 'kutoka future_builtins agiza zip' statement in the
top-level namespace.

We avoid the transformation ikiwa the zip() call is directly contained in
iter(<>), list(<>), tuple(<>), sorted(<>), ...join(<>), or for V in <>:.
"""

# Local agizas
kutoka .. agiza fixer_base
kutoka ..pytree agiza Node
kutoka ..pygram agiza python_symbols as syms
kutoka ..fixer_util agiza Name, ArgList, in_special_context


kundi FixZip(fixer_base.ConditionalFix):

    BM_compatible = True
    PATTERN = """
    power< 'zip' args=trailer< '(' [any] ')' > [trailers=trailer*]
    >
    """

    skip_on = "future_builtins.zip"

    eleza transform(self, node, results):
        ikiwa self.should_skip(node):
            return

        ikiwa in_special_context(node):
            rudisha None

        args = results['args'].clone()
        args.prefix = ""

        trailers = []
        ikiwa 'trailers' in results:
            trailers = [n.clone() for n in results['trailers']]
            for n in trailers:
                n.prefix = ""

        new = Node(syms.power, [Name("zip"), args], prefix="")
        new = Node(syms.power, [Name("list"), ArgList([new])] + trailers)
        new.prefix = node.prefix
        rudisha new
