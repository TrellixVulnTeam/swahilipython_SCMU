"""
    ast
    ~~~

    The `ast` module helps Python applications to process trees of the Python
    abstract syntax grammar.  The abstract syntax itself might change with
    each Python release; this module helps to find out programmatically what
    the current grammar looks like na allows modifications of it.

    An abstract syntax tree can be generated by pitaing `ast.PyCF_ONLY_AST` as
    a flag to the `compile()` builtin function ama by using the `parse()`
    function kutoka this module.  The result will be a tree of objects whose
    classes all inherit kutoka `ast.AST`.

    A modified abstract syntax tree can be compiled into a Python code object
    using the built-in `compile()` function.

    Additionally various helper functions are provided that make working with
    the trees simpler.  The main intention of the helper functions na this
    module kwenye general ni to provide an easy to use interface kila libraries
    that work tightly with the python syntax (template engines kila example).


    :copyright: Copyright 2008 by Armin Ronacher.
    :license: Python License.
"""
kutoka _ast agiza *


eleza parse(source, filename='<unknown>', mode='exec', *,
          type_comments=Uongo, feature_version=Tupu):
    """
    Parse the source into an AST node.
    Equivalent to compile(source, filename, mode, PyCF_ONLY_AST).
    Pass type_comments=Kweli to get back type comments where the syntax allows.
    """
    flags = PyCF_ONLY_AST
    ikiwa type_comments:
        flags |= PyCF_TYPE_COMMENTS
    ikiwa isinstance(feature_version, tuple):
        major, minor = feature_version  # Should be a 2-tuple.
        assert major == 3
        feature_version = minor
    elikiwa feature_version ni Tupu:
        feature_version = -1
    # Else it should be an int giving the minor version kila 3.x.
    rudisha compile(source, filename, mode, flags,
                   _feature_version=feature_version)


eleza literal_eval(node_or_string):
    """
    Safely evaluate an expression node ama a string containing a Python
    expression.  The string ama node provided may only consist of the following
    Python literal structures: strings, bytes, numbers, tuples, lists, dicts,
    sets, booleans, na Tupu.
    """
    ikiwa isinstance(node_or_string, str):
        node_or_string = parse(node_or_string, mode='eval')
    ikiwa isinstance(node_or_string, Expression):
        node_or_string = node_or_string.body
    eleza _convert_num(node):
        ikiwa isinstance(node, Constant):
            ikiwa type(node.value) kwenye (int, float, complex):
                rudisha node.value
        ashiria ValueError('malformed node ama string: ' + repr(node))
    eleza _convert_signed_num(node):
        ikiwa isinstance(node, UnaryOp) na isinstance(node.op, (UAdd, USub)):
            operand = _convert_num(node.operand)
            ikiwa isinstance(node.op, UAdd):
                rudisha + operand
            isipokua:
                rudisha - operand
        rudisha _convert_num(node)
    eleza _convert(node):
        ikiwa isinstance(node, Constant):
            rudisha node.value
        elikiwa isinstance(node, Tuple):
            rudisha tuple(map(_convert, node.elts))
        elikiwa isinstance(node, List):
            rudisha list(map(_convert, node.elts))
        elikiwa isinstance(node, Set):
            rudisha set(map(_convert, node.elts))
        elikiwa isinstance(node, Dict):
            rudisha dict(zip(map(_convert, node.keys),
                            map(_convert, node.values)))
        elikiwa isinstance(node, BinOp) na isinstance(node.op, (Add, Sub)):
            left = _convert_signed_num(node.left)
            right = _convert_num(node.right)
            ikiwa isinstance(left, (int, float)) na isinstance(right, complex):
                ikiwa isinstance(node.op, Add):
                    rudisha left + right
                isipokua:
                    rudisha left - right
        rudisha _convert_signed_num(node)
    rudisha _convert(node_or_string)


eleza dump(node, annotate_fields=Kweli, include_attributes=Uongo):
    """
    Return a formatted dump of the tree kwenye node.  This ni mainly useful for
    debugging purposes.  If annotate_fields ni true (by default),
    the rudishaed string will show the names na the values kila fields.
    If annotate_fields ni false, the result string will be more compact by
    omitting unambiguous field names.  Attributes such kama line
    numbers na column offsets are sio dumped by default.  If this ni wanted,
    include_attributes can be set to true.
    """
    eleza _format(node):
        ikiwa isinstance(node, AST):
            args = []
            keywords = annotate_fields
            kila field kwenye node._fields:
                jaribu:
                    value = getattr(node, field)
                tatizo AttributeError:
                    keywords = Kweli
                isipokua:
                    ikiwa keywords:
                        args.append('%s=%s' % (field, _format(value)))
                    isipokua:
                        args.append(_format(value))
            ikiwa include_attributes na node._attributes:
                kila a kwenye node._attributes:
                    jaribu:
                        args.append('%s=%s' % (a, _format(getattr(node, a))))
                    tatizo AttributeError:
                        pita
            rudisha '%s(%s)' % (node.__class__.__name__, ', '.join(args))
        elikiwa isinstance(node, list):
            rudisha '[%s]' % ', '.join(_format(x) kila x kwenye node)
        rudisha repr(node)
    ikiwa sio isinstance(node, AST):
        ashiria TypeError('expected AST, got %r' % node.__class__.__name__)
    rudisha _format(node)


eleza copy_location(new_node, old_node):
    """
    Copy source location (`lineno`, `col_offset`, `end_lineno`, na `end_col_offset`
    attributes) kutoka *old_node* to *new_node* ikiwa possible, na rudisha *new_node*.
    """
    kila attr kwenye 'lineno', 'col_offset', 'end_lineno', 'end_col_offset':
        ikiwa attr kwenye old_node._attributes na attr kwenye new_node._attributes \
           na hasattr(old_node, attr):
            setattr(new_node, attr, getattr(old_node, attr))
    rudisha new_node


eleza fix_missing_locations(node):
    """
    When you compile a node tree with compile(), the compiler expects lineno and
    col_offset attributes kila every node that supports them.  This ni rather
    tedious to fill kwenye kila generated nodes, so this helper adds these attributes
    recursively where sio already set, by setting them to the values of the
    parent node.  It works recursively starting at *node*.
    """
    eleza _fix(node, lineno, col_offset, end_lineno, end_col_offset):
        ikiwa 'lineno' kwenye node._attributes:
            ikiwa sio hasattr(node, 'lineno'):
                node.lineno = lineno
            isipokua:
                lineno = node.lineno
        ikiwa 'end_lineno' kwenye node._attributes:
            ikiwa sio hasattr(node, 'end_lineno'):
                node.end_lineno = end_lineno
            isipokua:
                end_lineno = node.end_lineno
        ikiwa 'col_offset' kwenye node._attributes:
            ikiwa sio hasattr(node, 'col_offset'):
                node.col_offset = col_offset
            isipokua:
                col_offset = node.col_offset
        ikiwa 'end_col_offset' kwenye node._attributes:
            ikiwa sio hasattr(node, 'end_col_offset'):
                node.end_col_offset = end_col_offset
            isipokua:
                end_col_offset = node.end_col_offset
        kila child kwenye iter_child_nodes(node):
            _fix(child, lineno, col_offset, end_lineno, end_col_offset)
    _fix(node, 1, 0, 1, 0)
    rudisha node


eleza increment_lineno(node, n=1):
    """
    Increment the line number na end line number of each node kwenye the tree
    starting at *node* by *n*. This ni useful to "move code" to a different
    location kwenye a file.
    """
    kila child kwenye walk(node):
        ikiwa 'lineno' kwenye child._attributes:
            child.lineno = getattr(child, 'lineno', 0) + n
        ikiwa 'end_lineno' kwenye child._attributes:
            child.end_lineno = getattr(child, 'end_lineno', 0) + n
    rudisha node


eleza iter_fields(node):
    """
    Yield a tuple of ``(fieldname, value)`` kila each field kwenye ``node._fields``
    that ni present on *node*.
    """
    kila field kwenye node._fields:
        jaribu:
            tuma field, getattr(node, field)
        tatizo AttributeError:
            pita


eleza iter_child_nodes(node):
    """
    Yield all direct child nodes of *node*, that is, all fields that are nodes
    na all items of fields that are lists of nodes.
    """
    kila name, field kwenye iter_fields(node):
        ikiwa isinstance(field, AST):
            tuma field
        elikiwa isinstance(field, list):
            kila item kwenye field:
                ikiwa isinstance(item, AST):
                    tuma item


eleza get_docstring(node, clean=Kweli):
    """
    Return the docstring kila the given node ama Tupu ikiwa no docstring can
    be found.  If the node provided does sio have docstrings a TypeError
    will be ashiriad.

    If *clean* ni `Kweli`, all tabs are expanded to spaces na any whitespace
    that can be uniformly removed kutoka the second line onwards ni removed.
    """
    ikiwa sio isinstance(node, (AsyncFunctionDef, FunctionDef, ClassDef, Module)):
        ashiria TypeError("%r can't have docstrings" % node.__class__.__name__)
    ikiwa not(node.body na isinstance(node.body[0], Expr)):
        rudisha Tupu
    node = node.body[0].value
    ikiwa isinstance(node, Str):
        text = node.s
    elikiwa isinstance(node, Constant) na isinstance(node.value, str):
        text = node.value
    isipokua:
        rudisha Tupu
    ikiwa clean:
        agiza inspect
        text = inspect.cleandoc(text)
    rudisha text


eleza _splitlines_no_ff(source):
    """Split a string into lines ignoring form feed na other chars.

    This mimics how the Python parser splits source code.
    """
    idx = 0
    lines = []
    next_line = ''
    wakati idx < len(source):
        c = source[idx]
        next_line += c
        idx += 1
        # Keep \r\n together
        ikiwa c == '\r' na idx < len(source) na source[idx] == '\n':
            next_line += '\n'
            idx += 1
        ikiwa c kwenye '\r\n':
            lines.append(next_line)
            next_line = ''

    ikiwa next_line:
        lines.append(next_line)
    rudisha lines


eleza _pad_whitespace(source):
    """Replace all chars tatizo '\f\t' kwenye a line with spaces."""
    result = ''
    kila c kwenye source:
        ikiwa c kwenye '\f\t':
            result += c
        isipokua:
            result += ' '
    rudisha result


eleza get_source_segment(source, node, *, padded=Uongo):
    """Get source code segment of the *source* that generated *node*.

    If some location information (`lineno`, `end_lineno`, `col_offset`,
    ama `end_col_offset`) ni missing, rudisha Tupu.

    If *padded* ni `Kweli`, the first line of a multi-line statement will
    be padded with spaces to match its original position.
    """
    jaribu:
        lineno = node.lineno - 1
        end_lineno = node.end_lineno - 1
        col_offset = node.col_offset
        end_col_offset = node.end_col_offset
    tatizo AttributeError:
        rudisha Tupu

    lines = _splitlines_no_ff(source)
    ikiwa end_lineno == lineno:
        rudisha lines[lineno].encode()[col_offset:end_col_offset].decode()

    ikiwa padded:
        padding = _pad_whitespace(lines[lineno].encode()[:col_offset].decode())
    isipokua:
        padding = ''

    first = padding + lines[lineno].encode()[col_offset:].decode()
    last = lines[end_lineno].encode()[:end_col_offset].decode()
    lines = lines[lineno+1:end_lineno]

    lines.insert(0, first)
    lines.append(last)
    rudisha ''.join(lines)


eleza walk(node):
    """
    Recursively tuma all descendant nodes kwenye the tree starting at *node*
    (including *node* itself), kwenye no specified order.  This ni useful ikiwa you
    only want to modify nodes kwenye place na don't care about the context.
    """
    kutoka collections agiza deque
    todo = deque([node])
    wakati todo:
        node = todo.popleft()
        todo.extend(iter_child_nodes(node))
        tuma node


kundi NodeVisitor(object):
    """
    A node visitor base kundi that walks the abstract syntax tree na calls a
    visitor function kila every node found.  This function may rudisha a value
    which ni forwarded by the `visit` method.

    This kundi ni meant to be subclassed, with the subkundi adding visitor
    methods.

    Per default the visitor functions kila the nodes are ``'visit_'`` +
    kundi name of the node.  So a `TryFinally` node visit function would
    be `visit_TryFinally`.  This behavior can be changed by overriding
    the `visit` method.  If no visitor function exists kila a node
    (rudisha value `Tupu`) the `generic_visit` visitor ni used instead.

    Don't use the `NodeVisitor` ikiwa you want to apply changes to nodes during
    traversing.  For this a special visitor exists (`NodeTransformer`) that
    allows modifications.
    """

    eleza visit(self, node):
        """Visit a node."""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        rudisha visitor(node)

    eleza generic_visit(self, node):
        """Called ikiwa no explicit visitor function exists kila a node."""
        kila field, value kwenye iter_fields(node):
            ikiwa isinstance(value, list):
                kila item kwenye value:
                    ikiwa isinstance(item, AST):
                        self.visit(item)
            elikiwa isinstance(value, AST):
                self.visit(value)

    eleza visit_Constant(self, node):
        value = node.value
        type_name = _const_node_type_names.get(type(value))
        ikiwa type_name ni Tupu:
            kila cls, name kwenye _const_node_type_names.items():
                ikiwa isinstance(value, cls):
                    type_name = name
                    koma
        ikiwa type_name ni sio Tupu:
            method = 'visit_' + type_name
            jaribu:
                visitor = getattr(self, method)
            tatizo AttributeError:
                pita
            isipokua:
                agiza warnings
                warnings.warn(f"{method} ni deprecated; add visit_Constant",
                              PendingDeprecationWarning, 2)
                rudisha visitor(node)
        rudisha self.generic_visit(node)


kundi NodeTransformer(NodeVisitor):
    """
    A :class:`NodeVisitor` subkundi that walks the abstract syntax tree and
    allows modification of nodes.

    The `NodeTransformer` will walk the AST na use the rudisha value of the
    visitor methods to replace ama remove the old node.  If the rudisha value of
    the visitor method ni ``Tupu``, the node will be removed kutoka its location,
    otherwise it ni replaced with the rudisha value.  The rudisha value may be the
    original node kwenye which case no replacement takes place.

    Here ni an example transformer that rewrites all occurrences of name lookups
    (``foo``) to ``data['foo']``::

       kundi RewriteName(NodeTransformer):

           eleza visit_Name(self, node):
               rudisha copy_location(Subscript(
                   value=Name(id='data', ctx=Load()),
                   slice=Index(value=Str(s=node.id)),
                   ctx=node.ctx
               ), node)

    Keep kwenye mind that ikiwa the node you're operating on has child nodes you must
    either transform the child nodes yourself ama call the :meth:`generic_visit`
    method kila the node first.

    For nodes that were part of a collection of statements (that applies to all
    statement nodes), the visitor may also rudisha a list of nodes rather than
    just a single node.

    Usually you use the transformer like this::

       node = YourTransformer().visit(node)
    """

    eleza generic_visit(self, node):
        kila field, old_value kwenye iter_fields(node):
            ikiwa isinstance(old_value, list):
                new_values = []
                kila value kwenye old_value:
                    ikiwa isinstance(value, AST):
                        value = self.visit(value)
                        ikiwa value ni Tupu:
                            endelea
                        elikiwa sio isinstance(value, AST):
                            new_values.extend(value)
                            endelea
                    new_values.append(value)
                old_value[:] = new_values
            elikiwa isinstance(old_value, AST):
                new_node = self.visit(old_value)
                ikiwa new_node ni Tupu:
                    delattr(node, field)
                isipokua:
                    setattr(node, field, new_node)
        rudisha node


# The following code ni kila backward compatibility.
# It will be removed kwenye future.

eleza _getter(self):
    rudisha self.value

eleza _setter(self, value):
    self.value = value

Constant.n = property(_getter, _setter)
Constant.s = property(_getter, _setter)

kundi _ABC(type):

    eleza __instancecheck__(cls, inst):
        ikiwa sio isinstance(inst, Constant):
            rudisha Uongo
        ikiwa cls kwenye _const_types:
            jaribu:
                value = inst.value
            tatizo AttributeError:
                rudisha Uongo
            isipokua:
                rudisha (
                    isinstance(value, _const_types[cls]) and
                    sio isinstance(value, _const_types_not.get(cls, ()))
                )
        rudisha type.__instancecheck__(cls, inst)

eleza _new(cls, *args, **kwargs):
    ikiwa cls kwenye _const_types:
        rudisha Constant(*args, **kwargs)
    rudisha Constant.__new__(cls, *args, **kwargs)

kundi Num(Constant, metaclass=_ABC):
    _fields = ('n',)
    __new__ = _new

kundi Str(Constant, metaclass=_ABC):
    _fields = ('s',)
    __new__ = _new

kundi Bytes(Constant, metaclass=_ABC):
    _fields = ('s',)
    __new__ = _new

kundi NameConstant(Constant, metaclass=_ABC):
    __new__ = _new

kundi Ellipsis(Constant, metaclass=_ABC):
    _fields = ()

    eleza __new__(cls, *args, **kwargs):
        ikiwa cls ni Ellipsis:
            rudisha Constant(..., *args, **kwargs)
        rudisha Constant.__new__(cls, *args, **kwargs)

_const_types = {
    Num: (int, float, complex),
    Str: (str,),
    Bytes: (bytes,),
    NameConstant: (type(Tupu), bool),
    Ellipsis: (type(...),),
}
_const_types_not = {
    Num: (bool,),
}
_const_node_type_names = {
    bool: 'NameConstant',  # should be before int
    type(Tupu): 'NameConstant',
    int: 'Num',
    float: 'Num',
    complex: 'Num',
    str: 'Str',
    bytes: 'Bytes',
    type(...): 'Ellipsis',
}
