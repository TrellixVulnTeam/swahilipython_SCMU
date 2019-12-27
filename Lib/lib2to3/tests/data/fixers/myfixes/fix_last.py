kutoka lib2to3.fixer_base agiza BaseFix

class FixLast(BaseFix):

    run_order = 10

    def match(self, node): return False
