"""Fixer that changes raw_input(...) into input(...)."""
# Author: Andre Roberge

# Local agizas
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Name

class FixRawInput(fixer_base.BaseFix):

    BM_compatible = True
    PATTERN = """
              power< name='raw_input' trailer< '(' [any] ')' > any* >
              """

    def transform(self, node, results):
        name = results["name"]
        name.replace(Name("input", prefix=name.prefix))
