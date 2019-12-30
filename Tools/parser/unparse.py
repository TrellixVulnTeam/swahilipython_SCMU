"Usage: unparse.py <path to source file>"
agiza sys
agiza ast
agiza tokenize
agiza io
agiza os

# Large float na imaginary literals get turned into infinities kwenye the AST.
# We unparse those infinities to INFSTR.
INFSTR = "1e" + repr(sys.float_info.max_10_exp + 1)

eleza interleave(inter, f, seq):
    """Call f on each item kwenye seq, calling inter() kwenye between.
    """
    seq = iter(seq)
    jaribu:
        f(next(seq))
    tatizo StopIteration:
        pita
    isipokua:
        kila x kwenye seq:
            inter()
            f(x)

kundi Unparser:
    """Methods kwenye this kundi recursively traverse an AST na
    output source code kila the abstract syntax; original formatting
    ni disregarded. """

    eleza __init__(self, tree, file = sys.stdout):
        """Unparser(tree, file=sys.stdout) -> Tupu.
         Print the source kila tree to file."""
        self.f = file
        self._indent = 0
        self.dispatch(tree)
        andika("", file=self.f)
        self.f.flush()

    eleza fill(self, text = ""):
        "Indent a piece of text, according to the current indentation level"
        self.f.write("\n"+"    "*self._indent + text)

    eleza write(self, text):
        "Append a piece of text to the current line."
        self.f.write(text)

    eleza enter(self):
        "Print ':', na increase the indentation."
        self.write(":")
        self._indent += 1

    eleza leave(self):
        "Decrease the indentation level."
        self._indent -= 1

    eleza dispatch(self, tree):
        "Dispatcher function, dispatching tree type T to method _T."
        ikiwa isinstance(tree, list):
            kila t kwenye tree:
                self.dispatch(t)
            rudisha
        meth = getattr(self, "_"+tree.__class__.__name__)
        meth(tree)


    ############### Unparsing methods ######################
    # There should be one method per concrete grammar type #
    # Constructors should be grouped by sum type. Ideally, #
    # this would follow the order kwenye the grammar, but      #
    # currently doesn't.                                   #
    ########################################################

    eleza _Module(self, tree):
        kila stmt kwenye tree.body:
            self.dispatch(stmt)

    # stmt
    eleza _Expr(self, tree):
        self.fill()
        self.dispatch(tree.value)

    eleza _NamedExpr(self, tree):
        self.write("(")
        self.dispatch(tree.target)
        self.write(" := ")
        self.dispatch(tree.value)
        self.write(")")

    eleza _Import(self, t):
        self.fill("agiza ")
        interleave(lambda: self.write(", "), self.dispatch, t.names)

    eleza _ImportFrom(self, t):
        self.fill("kutoka ")
        self.write("." * t.level)
        ikiwa t.module:
            self.write(t.module)
        self.write(" agiza ")
        interleave(lambda: self.write(", "), self.dispatch, t.names)

    eleza _Assign(self, t):
        self.fill()
        kila target kwenye t.targets:
            self.dispatch(target)
            self.write(" = ")
        self.dispatch(t.value)

    eleza _AugAssign(self, t):
        self.fill()
        self.dispatch(t.target)
        self.write(" "+self.binop[t.op.__class__.__name__]+"= ")
        self.dispatch(t.value)

    eleza _AnnAssign(self, t):
        self.fill()
        ikiwa sio t.simple na isinstance(t.target, ast.Name):
            self.write('(')
        self.dispatch(t.target)
        ikiwa sio t.simple na isinstance(t.target, ast.Name):
            self.write(')')
        self.write(": ")
        self.dispatch(t.annotation)
        ikiwa t.value:
            self.write(" = ")
            self.dispatch(t.value)

    eleza _Return(self, t):
        self.fill("return")
        ikiwa t.value:
            self.write(" ")
            self.dispatch(t.value)

    eleza _Pass(self, t):
        self.fill("pita")

    eleza _Break(self, t):
        self.fill("koma")

    eleza _Continue(self, t):
        self.fill("endelea")

    eleza _Delete(self, t):
        self.fill("toa ")
        interleave(lambda: self.write(", "), self.dispatch, t.targets)

    eleza _Assert(self, t):
        self.fill("assert ")
        self.dispatch(t.test)
        ikiwa t.msg:
            self.write(", ")
            self.dispatch(t.msg)

    eleza _Global(self, t):
        self.fill("global ")
        interleave(lambda: self.write(", "), self.write, t.names)

    eleza _Nonlocal(self, t):
        self.fill("nonlocal ")
        interleave(lambda: self.write(", "), self.write, t.names)

    eleza _Await(self, t):
        self.write("(")
        self.write("await")
        ikiwa t.value:
            self.write(" ")
            self.dispatch(t.value)
        self.write(")")

    eleza _Yield(self, t):
        self.write("(")
        self.write("yield")
        ikiwa t.value:
            self.write(" ")
            self.dispatch(t.value)
        self.write(")")

    eleza _YieldFrom(self, t):
        self.write("(")
        self.write("tuma from")
        ikiwa t.value:
            self.write(" ")
            self.dispatch(t.value)
        self.write(")")

    eleza _Raise(self, t):
        self.fill("raise")
        ikiwa sio t.exc:
            assert sio t.cause
            rudisha
        self.write(" ")
        self.dispatch(t.exc)
        ikiwa t.cause:
            self.write(" kutoka ")
            self.dispatch(t.cause)

    eleza _Try(self, t):
        self.fill("try")
        self.enter()
        self.dispatch(t.body)
        self.leave()
        kila ex kwenye t.handlers:
            self.dispatch(ex)
        ikiwa t.orisipokua:
            self.fill("else")
            self.enter()
            self.dispatch(t.orelse)
            self.leave()
        ikiwa t.finalbody:
            self.fill("finally")
            self.enter()
            self.dispatch(t.finalbody)
            self.leave()

    eleza _ExceptHandler(self, t):
        self.fill("except")
        ikiwa t.type:
            self.write(" ")
            self.dispatch(t.type)
        ikiwa t.name:
            self.write(" kama ")
            self.write(t.name)
        self.enter()
        self.dispatch(t.body)
        self.leave()

    eleza _ClassDef(self, t):
        self.write("\n")
        kila deco kwenye t.decorator_list:
            self.fill("@")
            self.dispatch(deco)
        self.fill("kundi "+t.name)
        self.write("(")
        comma = Uongo
        kila e kwenye t.bases:
            ikiwa comma: self.write(", ")
            isipokua: comma = Kweli
            self.dispatch(e)
        kila e kwenye t.keywords:
            ikiwa comma: self.write(", ")
            isipokua: comma = Kweli
            self.dispatch(e)
        self.write(")")

        self.enter()
        self.dispatch(t.body)
        self.leave()

    eleza _FunctionDef(self, t):
        self.__FunctionDef_helper(t, "def")

    eleza _AsyncFunctionDef(self, t):
        self.__FunctionDef_helper(t, "async def")

    eleza __FunctionDef_helper(self, t, fill_suffix):
        self.write("\n")
        kila deco kwenye t.decorator_list:
            self.fill("@")
            self.dispatch(deco)
        def_str = fill_suffix+" "+t.name + "("
        self.fill(def_str)
        self.dispatch(t.args)
        self.write(")")
        ikiwa t.returns:
            self.write(" -> ")
            self.dispatch(t.returns)
        self.enter()
        self.dispatch(t.body)
        self.leave()

    eleza _For(self, t):
        self.__For_helper("kila ", t)

    eleza _AsyncFor(self, t):
        self.__For_helper("async kila ", t)

    eleza __For_helper(self, fill, t):
        self.fill(fill)
        self.dispatch(t.target)
        self.write(" kwenye ")
        self.dispatch(t.iter)
        self.enter()
        self.dispatch(t.body)
        self.leave()
        ikiwa t.orisipokua:
            self.fill("else")
            self.enter()
            self.dispatch(t.orelse)
            self.leave()

    eleza _If(self, t):
        self.fill("ikiwa ")
        self.dispatch(t.test)
        self.enter()
        self.dispatch(t.body)
        self.leave()
        # collapse nested ifs into equivalent elifs.
        wakati (t.orelse na len(t.orelse) == 1 na
               isinstance(t.orelse[0], ast.If)):
            t = t.orelse[0]
            self.fill("lasivyo ")
            self.dispatch(t.test)
            self.enter()
            self.dispatch(t.body)
            self.leave()
        # final isipokua
        ikiwa t.orisipokua:
            self.fill("else")
            self.enter()
            self.dispatch(t.orelse)
            self.leave()

    eleza _While(self, t):
        self.fill("wakati ")
        self.dispatch(t.test)
        self.enter()
        self.dispatch(t.body)
        self.leave()
        ikiwa t.orisipokua:
            self.fill("else")
            self.enter()
            self.dispatch(t.orelse)
            self.leave()

    eleza _With(self, t):
        self.fill("ukijumuisha ")
        interleave(lambda: self.write(", "), self.dispatch, t.items)
        self.enter()
        self.dispatch(t.body)
        self.leave()

    eleza _AsyncWith(self, t):
        self.fill("async ukijumuisha ")
        interleave(lambda: self.write(", "), self.dispatch, t.items)
        self.enter()
        self.dispatch(t.body)
        self.leave()

    # expr
    eleza _JoinedStr(self, t):
        self.write("f")
        string = io.StringIO()
        self._fstring_JoinedStr(t, string.write)
        self.write(repr(string.getvalue()))

    eleza _FormattedValue(self, t):
        self.write("f")
        string = io.StringIO()
        self._fstring_FormattedValue(t, string.write)
        self.write(repr(string.getvalue()))

    eleza _fstring_JoinedStr(self, t, write):
        kila value kwenye t.values:
            meth = getattr(self, "_fstring_" + type(value).__name__)
            meth(value, write)

    eleza _fstring_Constant(self, t, write):
        assert isinstance(t.value, str)
        value = t.value.replace("{", "{{").replace("}", "}}")
        write(value)

    eleza _fstring_FormattedValue(self, t, write):
        write("{")
        expr = io.StringIO()
        Unparser(t.value, expr)
        expr = expr.getvalue().rstrip("\n")
        ikiwa expr.startswith("{"):
            write(" ")  # Separate pair of opening brackets kama "{ {"
        write(expr)
        ikiwa t.conversion != -1:
            conversion = chr(t.conversion)
            assert conversion kwenye "sra"
            write(f"!{conversion}")
        ikiwa t.format_spec:
            write(":")
            meth = getattr(self, "_fstring_" + type(t.format_spec).__name__)
            meth(t.format_spec, write)
        write("}")

    eleza _Name(self, t):
        self.write(t.id)

    eleza _write_constant(self, value):
        ikiwa isinstance(value, (float, complex)):
            # Substitute overflowing decimal literal kila AST infinities.
            self.write(repr(value).replace("inf", INFSTR))
        isipokua:
            self.write(repr(value))

    eleza _Constant(self, t):
        value = t.value
        ikiwa isinstance(value, tuple):
            self.write("(")
            ikiwa len(value) == 1:
                self._write_constant(value[0])
                self.write(",")
            isipokua:
                interleave(lambda: self.write(", "), self._write_constant, value)
            self.write(")")
        lasivyo value ni ...:
            self.write("...")
        isipokua:
            ikiwa t.kind == "u":
                self.write("u")
            self._write_constant(t.value)

    eleza _List(self, t):
        self.write("[")
        interleave(lambda: self.write(", "), self.dispatch, t.elts)
        self.write("]")

    eleza _ListComp(self, t):
        self.write("[")
        self.dispatch(t.elt)
        kila gen kwenye t.generators:
            self.dispatch(gen)
        self.write("]")

    eleza _GeneratorExp(self, t):
        self.write("(")
        self.dispatch(t.elt)
        kila gen kwenye t.generators:
            self.dispatch(gen)
        self.write(")")

    eleza _SetComp(self, t):
        self.write("{")
        self.dispatch(t.elt)
        kila gen kwenye t.generators:
            self.dispatch(gen)
        self.write("}")

    eleza _DictComp(self, t):
        self.write("{")
        self.dispatch(t.key)
        self.write(": ")
        self.dispatch(t.value)
        kila gen kwenye t.generators:
            self.dispatch(gen)
        self.write("}")

    eleza _comprehension(self, t):
        ikiwa t.is_async:
            self.write(" async kila ")
        isipokua:
            self.write(" kila ")
        self.dispatch(t.target)
        self.write(" kwenye ")
        self.dispatch(t.iter)
        kila if_clause kwenye t.ifs:
            self.write(" ikiwa ")
            self.dispatch(if_clause)

    eleza _IfExp(self, t):
        self.write("(")
        self.dispatch(t.body)
        self.write(" ikiwa ")
        self.dispatch(t.test)
        self.write(" isipokua ")
        self.dispatch(t.orelse)
        self.write(")")

    eleza _Set(self, t):
        assert(t.elts) # should be at least one element
        self.write("{")
        interleave(lambda: self.write(", "), self.dispatch, t.elts)
        self.write("}")

    eleza _Dict(self, t):
        self.write("{")
        eleza write_key_value_pair(k, v):
            self.dispatch(k)
            self.write(": ")
            self.dispatch(v)

        eleza write_item(item):
            k, v = item
            ikiwa k ni Tupu:
                # kila dictionary unpacking operator kwenye dicts {**{'y': 2}}
                # see PEP 448 kila details
                self.write("**")
                self.dispatch(v)
            isipokua:
                write_key_value_pair(k, v)
        interleave(lambda: self.write(", "), write_item, zip(t.keys, t.values))
        self.write("}")

    eleza _Tuple(self, t):
        self.write("(")
        ikiwa len(t.elts) == 1:
            elt = t.elts[0]
            self.dispatch(elt)
            self.write(",")
        isipokua:
            interleave(lambda: self.write(", "), self.dispatch, t.elts)
        self.write(")")

    unop = {"Invert":"~", "Not": "not", "UAdd":"+", "USub":"-"}
    eleza _UnaryOp(self, t):
        self.write("(")
        self.write(self.unop[t.op.__class__.__name__])
        self.write(" ")
        self.dispatch(t.operand)
        self.write(")")

    binop = { "Add":"+", "Sub":"-", "Mult":"*", "MatMult":"@", "Div":"/", "Mod":"%",
                    "LShift":"<<", "RShift":">>", "BitOr":"|", "BitXor":"^", "BitAnd":"&",
                    "FloorDiv":"//", "Pow": "**"}
    eleza _BinOp(self, t):
        self.write("(")
        self.dispatch(t.left)
        self.write(" " + self.binop[t.op.__class__.__name__] + " ")
        self.dispatch(t.right)
        self.write(")")

    cmpops = {"Eq":"==", "NotEq":"!=", "Lt":"<", "LtE":"<=", "Gt":">", "GtE":">=",
                        "Is":"is", "IsNot":"is not", "In":"in", "NotIn":"sio in"}
    eleza _Compare(self, t):
        self.write("(")
        self.dispatch(t.left)
        kila o, e kwenye zip(t.ops, t.comparators):
            self.write(" " + self.cmpops[o.__class__.__name__] + " ")
            self.dispatch(e)
        self.write(")")

    boolops = {ast.And: 'and', ast.Or: 'or'}
    eleza _BoolOp(self, t):
        self.write("(")
        s = " %s " % self.boolops[t.op.__class__]
        interleave(lambda: self.write(s), self.dispatch, t.values)
        self.write(")")

    eleza _Attribute(self,t):
        self.dispatch(t.value)
        # Special case: 3.__abs__() ni a syntax error, so ikiwa t.value
        # ni an integer literal then we need to either parenthesize
        # it ama add an extra space to get 3 .__abs__().
        ikiwa isinstance(t.value, ast.Constant) na isinstance(t.value.value, int):
            self.write(" ")
        self.write(".")
        self.write(t.attr)

    eleza _Call(self, t):
        self.dispatch(t.func)
        self.write("(")
        comma = Uongo
        kila e kwenye t.args:
            ikiwa comma: self.write(", ")
            isipokua: comma = Kweli
            self.dispatch(e)
        kila e kwenye t.keywords:
            ikiwa comma: self.write(", ")
            isipokua: comma = Kweli
            self.dispatch(e)
        self.write(")")

    eleza _Subscript(self, t):
        self.dispatch(t.value)
        self.write("[")
        self.dispatch(t.slice)
        self.write("]")

    eleza _Starred(self, t):
        self.write("*")
        self.dispatch(t.value)

    # slice
    eleza _Ellipsis(self, t):
        self.write("...")

    eleza _Index(self, t):
        self.dispatch(t.value)

    eleza _Slice(self, t):
        ikiwa t.lower:
            self.dispatch(t.lower)
        self.write(":")
        ikiwa t.upper:
            self.dispatch(t.upper)
        ikiwa t.step:
            self.write(":")
            self.dispatch(t.step)

    eleza _ExtSlice(self, t):
        interleave(lambda: self.write(', '), self.dispatch, t.dims)

    # argument
    eleza _arg(self, t):
        self.write(t.arg)
        ikiwa t.annotation:
            self.write(": ")
            self.dispatch(t.annotation)

    # others
    eleza _arguments(self, t):
        first = Kweli
        # normal arguments
        all_args = t.posonlyargs + t.args
        defaults = [Tupu] * (len(all_args) - len(t.defaults)) + t.defaults
        kila index, elements kwenye enumerate(zip(all_args, defaults), 1):
            a, d = elements
            ikiwa first:first = Uongo
            isipokua: self.write(", ")
            self.dispatch(a)
            ikiwa d:
                self.write("=")
                self.dispatch(d)
            ikiwa index == len(t.posonlyargs):
                self.write(", /")

        # varargs, ama bare '*' ikiwa no varargs but keyword-only arguments present
        ikiwa t.vararg ama t.kwonlyargs:
            ikiwa first:first = Uongo
            isipokua: self.write(", ")
            self.write("*")
            ikiwa t.vararg:
                self.write(t.vararg.arg)
                ikiwa t.vararg.annotation:
                    self.write(": ")
                    self.dispatch(t.vararg.annotation)

        # keyword-only arguments
        ikiwa t.kwonlyargs:
            kila a, d kwenye zip(t.kwonlyargs, t.kw_defaults):
                ikiwa first:first = Uongo
                isipokua: self.write(", ")
                self.dispatch(a),
                ikiwa d:
                    self.write("=")
                    self.dispatch(d)

        # kwargs
        ikiwa t.kwarg:
            ikiwa first:first = Uongo
            isipokua: self.write(", ")
            self.write("**"+t.kwarg.arg)
            ikiwa t.kwarg.annotation:
                self.write(": ")
                self.dispatch(t.kwarg.annotation)

    eleza _keyword(self, t):
        ikiwa t.arg ni Tupu:
            self.write("**")
        isipokua:
            self.write(t.arg)
            self.write("=")
        self.dispatch(t.value)

    eleza _Lambda(self, t):
        self.write("(")
        self.write("lambda ")
        self.dispatch(t.args)
        self.write(": ")
        self.dispatch(t.body)
        self.write(")")

    eleza _alias(self, t):
        self.write(t.name)
        ikiwa t.asname:
            self.write(" kama "+t.asname)

    eleza _withitem(self, t):
        self.dispatch(t.context_expr)
        ikiwa t.optional_vars:
            self.write(" kama ")
            self.dispatch(t.optional_vars)

eleza roundtrip(filename, output=sys.stdout):
    ukijumuisha open(filename, "rb") kama pyfile:
        encoding = tokenize.detect_encoding(pyfile.readline)[0]
    ukijumuisha open(filename, "r", encoding=encoding) kama pyfile:
        source = pyfile.read()
    tree = compile(source, filename, "exec", ast.PyCF_ONLY_AST)
    Unparser(tree, output)



eleza testdir(a):
    jaribu:
        names = [n kila n kwenye os.listdir(a) ikiwa n.endswith('.py')]
    tatizo OSError:
        andika("Directory sio readable: %s" % a, file=sys.stderr)
    isipokua:
        kila n kwenye names:
            fullname = os.path.join(a, n)
            ikiwa os.path.isfile(fullname):
                output = io.StringIO()
                andika('Testing %s' % fullname)
                jaribu:
                    roundtrip(fullname, output)
                tatizo Exception kama e:
                    andika('  Failed to compile, exception ni %s' % repr(e))
            lasivyo os.path.isdir(fullname):
                testdir(fullname)

eleza main(args):
    ikiwa args[0] == '--testdir':
        kila a kwenye args[1:]:
            testdir(a)
    isipokua:
        kila a kwenye args:
            roundtrip(a)

ikiwa __name__=='__main__':
    main(sys.argv[1:])
