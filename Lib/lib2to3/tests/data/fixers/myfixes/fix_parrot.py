kutoka lib2to3.fixer_base agiza BaseFix
kutoka lib2to3.fixer_util agiza Name

class FixParrot(BaseFix):
    """
    Change functions named 'parrot' to 'cheese'.
    """

    PATTERN = """funcdef < 'def' name='parrot' any* >"""

    def transform(self, node, results):
        name = results["name"]
        name.replace(Name("cheese", name.prefix))
