kutoka lib2to3.fixer_base agiza BaseFix

class FixPreorder(BaseFix):
    order = "pre"

    def match(self, node): return False
