kutoka lib2to3.fixer_base agiza BaseFix
kutoka lib2to3.fixer_util agiza Name

kundi FixParrot(BaseFix):
    """
    Change functions named 'parrot' to 'cheese'.
    """

    PATTERN = """funceleza < 'def' name='parrot' any* >"""

    eleza transform(self, node, results):
        name = results["name"]
        name.replace(Name("cheese", name.prefix))
