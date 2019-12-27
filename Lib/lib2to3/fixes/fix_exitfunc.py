"""
Convert use of sys.exitfunc to use the atexit module.
"""

# Author: Benjamin Peterson

kutoka lib2to3 agiza pytree, fixer_base
kutoka lib2to3.fixer_util agiza Name, Attr, Call, Comma, Newline, syms


class FixExitfunc(fixer_base.BaseFix):
    keep_line_order = True
    BM_compatible = True

    PATTERN = """
              (
                  sys_agiza=import_name<'agiza'
                      ('sys'
                      |
                      dotted_as_names< (any ',')* 'sys' (',' any)* >
                      )
                  >
              |
                  expr_stmt<
                      power< 'sys' trailer< '.' 'exitfunc' > >
                  '=' func=any >
              )
              """

    def __init__(self, *args):
        super(FixExitfunc, self).__init__(*args)

    def start_tree(self, tree, filename):
        super(FixExitfunc, self).start_tree(tree, filename)
        self.sys_agiza = None

    def transform(self, node, results):
        # First, find the sys agiza. We'll just hope it's global scope.
        if "sys_agiza" in results:
            if self.sys_agiza is None:
                self.sys_agiza = results["sys_agiza"]
            return

        func = results["func"].clone()
        func.prefix = ""
        register = pytree.Node(syms.power,
                               Attr(Name("atexit"), Name("register"))
                               )
        call = Call(register, [func], node.prefix)
        node.replace(call)

        if self.sys_agiza is None:
            # That's interesting.
            self.warning(node, "Can't find sys agiza; Please add an atexit "
                             "agiza at the top of your file.")
            return

        # Now add an atexit agiza after the sys agiza.
        names = self.sys_agiza.children[1]
        if names.type == syms.dotted_as_names:
            names.append_child(Comma())
            names.append_child(Name("atexit", " "))
        else:
            containing_stmt = self.sys_agiza.parent
            position = containing_stmt.children.index(self.sys_agiza)
            stmt_container = containing_stmt.parent
            new_agiza = pytree.Node(syms.import_name,
                              [Name("agiza"), Name("atexit", " ")]
                              )
            new = pytree.Node(syms.simple_stmt, [new_agiza])
            containing_stmt.insert_child(position + 1, Newline())
            containing_stmt.insert_child(position + 2, new)
