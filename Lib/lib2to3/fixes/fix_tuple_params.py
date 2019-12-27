"""Fixer for function definitions with tuple parameters.

eleza func(((a, b), c), d):
    ...

    ->

eleza func(x, d):
    ((a, b), c) = x
    ...

It will also support lambdas:

    lambda (x, y): x + y -> lambda t: t[0] + t[1]

    # The parens are a syntax error in Python 3
    lambda (x): x + y -> lambda x: x + y
"""
# Author: Collin Winter

# Local agizas
kutoka .. agiza pytree
kutoka ..pgen2 agiza token
kutoka .. agiza fixer_base
kutoka ..fixer_util agiza Assign, Name, Newline, Number, Subscript, syms

eleza is_docstring(stmt):
    rudisha isinstance(stmt, pytree.Node) and \
           stmt.children[0].type == token.STRING

kundi FixTupleParams(fixer_base.BaseFix):
    run_order = 4 #use a lower order since lambda is part of other
                  #patterns
    BM_compatible = True

    PATTERN = """
              funcdef< 'def' any parameters< '(' args=any ')' >
                       ['->' any] ':' suite=any+ >
              |
              lambda=
              lambdef< 'lambda' args=vfpdef< '(' inner=any ')' >
                       ':' body=any
              >
              """

    eleza transform(self, node, results):
        ikiwa "lambda" in results:
            rudisha self.transform_lambda(node, results)

        new_lines = []
        suite = results["suite"]
        args = results["args"]
        # This crap is so "eleza foo(...): x = 5; y = 7" is handled correctly.
        # TODO(cwinter): suite-cleanup
        ikiwa suite[0].children[1].type == token.INDENT:
            start = 2
            indent = suite[0].children[1].value
            end = Newline()
        else:
            start = 0
            indent = "; "
            end = pytree.Leaf(token.INDENT, "")

        # We need access to self for new_name(), and making this a method
        #  doesn't feel right. Closing over self and new_lines makes the
        #  code below cleaner.
        eleza handle_tuple(tuple_arg, add_prefix=False):
            n = Name(self.new_name())
            arg = tuple_arg.clone()
            arg.prefix = ""
            stmt = Assign(arg, n.clone())
            ikiwa add_prefix:
                n.prefix = " "
            tuple_arg.replace(n)
            new_lines.append(pytree.Node(syms.simple_stmt,
                                         [stmt, end.clone()]))

        ikiwa args.type == syms.tfpdef:
            handle_tuple(args)
        elikiwa args.type == syms.typedargslist:
            for i, arg in enumerate(args.children):
                ikiwa arg.type == syms.tfpdef:
                    # Without add_prefix, the emitted code is correct,
                    #  just ugly.
                    handle_tuple(arg, add_prefix=(i > 0))

        ikiwa not new_lines:
            return

        # This isn't strictly necessary, but it plays nicely with other fixers.
        # TODO(cwinter) get rid of this when children becomes a smart list
        for line in new_lines:
            line.parent = suite[0]

        # TODO(cwinter) suite-cleanup
        after = start
        ikiwa start == 0:
            new_lines[0].prefix = " "
        elikiwa is_docstring(suite[0].children[start]):
            new_lines[0].prefix = indent
            after = start + 1

        for line in new_lines:
            line.parent = suite[0]
        suite[0].children[after:after] = new_lines
        for i in range(after+1, after+len(new_lines)+1):
            suite[0].children[i].prefix = indent
        suite[0].changed()

    eleza transform_lambda(self, node, results):
        args = results["args"]
        body = results["body"]
        inner = simplify_args(results["inner"])

        # Replace lambda ((((x)))): x  with lambda x: x
        ikiwa inner.type == token.NAME:
            inner = inner.clone()
            inner.prefix = " "
            args.replace(inner)
            return

        params = find_params(args)
        to_index = map_to_index(params)
        tup_name = self.new_name(tuple_name(params))

        new_param = Name(tup_name, prefix=" ")
        args.replace(new_param.clone())
        for n in body.post_order():
            ikiwa n.type == token.NAME and n.value in to_index:
                subscripts = [c.clone() for c in to_index[n.value]]
                new = pytree.Node(syms.power,
                                  [new_param.clone()] + subscripts)
                new.prefix = n.prefix
                n.replace(new)


### Helper functions for transform_lambda()

eleza simplify_args(node):
    ikiwa node.type in (syms.vfplist, token.NAME):
        rudisha node
    elikiwa node.type == syms.vfpdef:
        # These look like vfpdef< '(' x ')' > where x is NAME
        # or another vfpeleza instance (leading to recursion).
        while node.type == syms.vfpdef:
            node = node.children[1]
        rudisha node
    raise RuntimeError("Received unexpected node %s" % node)

eleza find_params(node):
    ikiwa node.type == syms.vfpdef:
        rudisha find_params(node.children[1])
    elikiwa node.type == token.NAME:
        rudisha node.value
    rudisha [find_params(c) for c in node.children ikiwa c.type != token.COMMA]

eleza map_to_index(param_list, prefix=[], d=None):
    ikiwa d is None:
        d = {}
    for i, obj in enumerate(param_list):
        trailer = [Subscript(Number(str(i)))]
        ikiwa isinstance(obj, list):
            map_to_index(obj, trailer, d=d)
        else:
            d[obj] = prefix + trailer
    rudisha d

eleza tuple_name(param_list):
    l = []
    for obj in param_list:
        ikiwa isinstance(obj, list):
            l.append(tuple_name(obj))
        else:
            l.append(obj)
    rudisha "_".join(l)
