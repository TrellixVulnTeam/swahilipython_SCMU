"""Fix function attribute names (f.func_x -> f.__x__)."""
# Author: Collin Winter

# Local agizas
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Name


class FixFuncattrs(fixer_base.BaseFix):
    BM_compatible = True

    PATTERN = """
    power< any+ trailer< '.' attr=('func_closure' | 'func_doc' | 'func_globals'
                                  | 'func_name' | 'func_defaults' | 'func_code'
                                  | 'func_dict') > any* >
    """

    def transform(self, node, results):
        attr = results["attr"][0]
        attr.replace(Name(("__%s__" % attr.value[5:]),
                          prefix=attr.prefix))
