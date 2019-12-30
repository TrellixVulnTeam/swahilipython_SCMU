"""Disassembler of Python byte code into mnemonics."""

agiza sys
agiza types
agiza collections
agiza io

kutoka opcode agiza *
kutoka opcode agiza __all__ kama _opcodes_all

__all__ = ["code_info", "dis", "disassemble", "distb", "disco",
           "findlinestarts", "findlabels", "show_code",
           "get_instructions", "Instruction", "Bytecode"] + _opcodes_all
toa _opcodes_all

_have_code = (types.MethodType, types.FunctionType, types.CodeType,
              classmethod, staticmethod, type)

FORMAT_VALUE = opmap['FORMAT_VALUE']
FORMAT_VALUE_CONVERTERS = (
    (Tupu, ''),
    (str, 'str'),
    (repr, 'repr'),
    (ascii, 'ascii'),
)
MAKE_FUNCTION = opmap['MAKE_FUNCTION']
MAKE_FUNCTION_FLAGS = ('defaults', 'kwdefaults', 'annotations', 'closure')


eleza _try_compile(source, name):
    """Attempts to compile the given source, first kama an expression na
       then kama a statement ikiwa the first approach fails.

       Utility function to accept strings kwenye functions that otherwise
       expect code objects
    """
    jaribu:
        c = compile(source, name, 'eval')
    tatizo SyntaxError:
        c = compile(source, name, 'exec')
    rudisha c

eleza dis(x=Tupu, *, file=Tupu, depth=Tupu):
    """Disassemble classes, methods, functions, na other compiled objects.

    With no argument, disassemble the last traceback.

    Compiled objects currently include generator objects, async generator
    objects, na coroutine objects, all of which store their code object
    kwenye a special attribute.
    """
    ikiwa x ni Tupu:
        distb(file=file)
        rudisha
    # Extract functions kutoka methods.
    ikiwa hasattr(x, '__func__'):
        x = x.__func__
    # Extract compiled code objects from...
    ikiwa hasattr(x, '__code__'):  # ...a function, ama
        x = x.__code__
    lasivyo hasattr(x, 'gi_code'):  #...a generator object, ama
        x = x.gi_code
    lasivyo hasattr(x, 'ag_code'):  #...an asynchronous generator object, ama
        x = x.ag_code
    lasivyo hasattr(x, 'cr_code'):  #...a coroutine.
        x = x.cr_code
    # Perform the disassembly.
    ikiwa hasattr(x, '__dict__'):  # Class ama module
        items = sorted(x.__dict__.items())
        kila name, x1 kwenye items:
            ikiwa isinstance(x1, _have_code):
                andika("Disassembly of %s:" % name, file=file)
                jaribu:
                    dis(x1, file=file, depth=depth)
                tatizo TypeError kama msg:
                    andika("Sorry:", msg, file=file)
                andika(file=file)
    lasivyo hasattr(x, 'co_code'): # Code object
        _disassemble_recursive(x, file=file, depth=depth)
    lasivyo isinstance(x, (bytes, bytearray)): # Raw bytecode
        _disassemble_bytes(x, file=file)
    lasivyo isinstance(x, str):    # Source code
        _disassemble_str(x, file=file, depth=depth)
    isipokua:
        ashiria TypeError("don't know how to disassemble %s objects" %
                        type(x).__name__)

eleza distb(tb=Tupu, *, file=Tupu):
    """Disassemble a traceback (default: last traceback)."""
    ikiwa tb ni Tupu:
        jaribu:
            tb = sys.last_traceback
        tatizo AttributeError:
            ashiria RuntimeError("no last traceback to disassemble") kutoka Tupu
        wakati tb.tb_next: tb = tb.tb_next
    disassemble(tb.tb_frame.f_code, tb.tb_lasti, file=file)

# The inspect module interrogates this dictionary to build its
# list of CO_* constants. It ni also used by pretty_flags to
# turn the co_flags field into a human readable list.
COMPILER_FLAG_NAMES = {
     1: "OPTIMIZED",
     2: "NEWLOCALS",
     4: "VARARGS",
     8: "VARKEYWORDS",
    16: "NESTED",
    32: "GENERATOR",
    64: "NOFREE",
   128: "COROUTINE",
   256: "ITERABLE_COROUTINE",
   512: "ASYNC_GENERATOR",
}

eleza pretty_flags(flags):
    """Return pretty representation of code flags."""
    names = []
    kila i kwenye range(32):
        flag = 1<<i
        ikiwa flags & flag:
            names.append(COMPILER_FLAG_NAMES.get(flag, hex(flag)))
            flags ^= flag
            ikiwa sio flags:
                koma
    isipokua:
        names.append(hex(flags))
    rudisha ", ".join(names)

eleza _get_code_object(x):
    """Helper to handle methods, compiled ama raw code objects, na strings."""
    # Extract functions kutoka methods.
    ikiwa hasattr(x, '__func__'):
        x = x.__func__
    # Extract compiled code objects from...
    ikiwa hasattr(x, '__code__'):  # ...a function, ama
        x = x.__code__
    lasivyo hasattr(x, 'gi_code'):  #...a generator object, ama
        x = x.gi_code
    lasivyo hasattr(x, 'ag_code'):  #...an asynchronous generator object, ama
        x = x.ag_code
    lasivyo hasattr(x, 'cr_code'):  #...a coroutine.
        x = x.cr_code
    # Handle source code.
    ikiwa isinstance(x, str):
        x = _try_compile(x, "<disassembly>")
    # By now, ikiwa we don't have a code object, we can't disassemble x.
    ikiwa hasattr(x, 'co_code'):
        rudisha x
    ashiria TypeError("don't know how to disassemble %s objects" %
                    type(x).__name__)

eleza code_info(x):
    """Formatted details of methods, functions, ama code."""
    rudisha _format_code_info(_get_code_object(x))

eleza _format_code_info(co):
    lines = []
    lines.append("Name:              %s" % co.co_name)
    lines.append("Filename:          %s" % co.co_filename)
    lines.append("Argument count:    %s" % co.co_argcount)
    lines.append("Positional-only arguments: %s" % co.co_posonlyargcount)
    lines.append("Kw-only arguments: %s" % co.co_kwonlyargcount)
    lines.append("Number of locals:  %s" % co.co_nlocals)
    lines.append("Stack size:        %s" % co.co_stacksize)
    lines.append("Flags:             %s" % pretty_flags(co.co_flags))
    ikiwa co.co_consts:
        lines.append("Constants:")
        kila i_c kwenye enumerate(co.co_consts):
            lines.append("%4d: %r" % i_c)
    ikiwa co.co_names:
        lines.append("Names:")
        kila i_n kwenye enumerate(co.co_names):
            lines.append("%4d: %s" % i_n)
    ikiwa co.co_varnames:
        lines.append("Variable names:")
        kila i_n kwenye enumerate(co.co_varnames):
            lines.append("%4d: %s" % i_n)
    ikiwa co.co_freevars:
        lines.append("Free variables:")
        kila i_n kwenye enumerate(co.co_freevars):
            lines.append("%4d: %s" % i_n)
    ikiwa co.co_cellvars:
        lines.append("Cell variables:")
        kila i_n kwenye enumerate(co.co_cellvars):
            lines.append("%4d: %s" % i_n)
    rudisha "\n".join(lines)

eleza show_code(co, *, file=Tupu):
    """Print details of methods, functions, ama code to *file*.

    If *file* ni sio provided, the output ni printed on stdout.
    """
    andika(code_info(co), file=file)

_Instruction = collections.namedtuple("_Instruction",
     "opname opcode arg argval argrepr offset starts_line is_jump_target")

_Instruction.opname.__doc__ = "Human readable name kila operation"
_Instruction.opcode.__doc__ = "Numeric code kila operation"
_Instruction.arg.__doc__ = "Numeric argument to operation (ikiwa any), otherwise Tupu"
_Instruction.argval.__doc__ = "Resolved arg value (ikiwa known), otherwise same kama arg"
_Instruction.argrepr.__doc__ = "Human readable description of operation argument"
_Instruction.offset.__doc__ = "Start index of operation within bytecode sequence"
_Instruction.starts_line.__doc__ = "Line started by this opcode (ikiwa any), otherwise Tupu"
_Instruction.is_jump_target.__doc__ = "Kweli ikiwa other code jumps to here, otherwise Uongo"

_OPNAME_WIDTH = 20
_OPARG_WIDTH = 5

kundi Instruction(_Instruction):
    """Details kila a bytecode operation

       Defined fields:
         opname - human readable name kila operation
         opcode - numeric code kila operation
         arg - numeric argument to operation (ikiwa any), otherwise Tupu
         argval - resolved arg value (ikiwa known), otherwise same kama arg
         argrepr - human readable description of operation argument
         offset - start index of operation within bytecode sequence
         starts_line - line started by this opcode (ikiwa any), otherwise Tupu
         is_jump_target - Kweli ikiwa other code jumps to here, otherwise Uongo
    """

    eleza _disassemble(self, lineno_width=3, mark_as_current=Uongo, offset_width=4):
        """Format instruction details kila inclusion kwenye disassembly output

        *lineno_width* sets the width of the line number field (0 omits it)
        *mark_as_current* inserts a '-->' marker arrow kama part of the line
        *offset_width* sets the width of the instruction offset field
        """
        fields = []
        # Column: Source code line number
        ikiwa lineno_width:
            ikiwa self.starts_line ni sio Tupu:
                lineno_fmt = "%%%dd" % lineno_width
                fields.append(lineno_fmt % self.starts_line)
            isipokua:
                fields.append(' ' * lineno_width)
        # Column: Current instruction indicator
        ikiwa mark_as_current:
            fields.append('-->')
        isipokua:
            fields.append('   ')
        # Column: Jump target marker
        ikiwa self.is_jump_target:
            fields.append('>>')
        isipokua:
            fields.append('  ')
        # Column: Instruction offset kutoka start of code sequence
        fields.append(repr(self.offset).rjust(offset_width))
        # Column: Opcode name
        fields.append(self.opname.ljust(_OPNAME_WIDTH))
        # Column: Opcode argument
        ikiwa self.arg ni sio Tupu:
            fields.append(repr(self.arg).rjust(_OPARG_WIDTH))
            # Column: Opcode argument details
            ikiwa self.argrepr:
                fields.append('(' + self.argrepr + ')')
        rudisha ' '.join(fields).rstrip()


eleza get_instructions(x, *, first_line=Tupu):
    """Iterator kila the opcodes kwenye methods, functions ama code

    Generates a series of Instruction named tuples giving the details of
    each operations kwenye the supplied code.

    If *first_line* ni sio Tupu, it indicates the line number that should
    be reported kila the first source line kwenye the disassembled code.
    Otherwise, the source line information (ikiwa any) ni taken directly from
    the disassembled code object.
    """
    co = _get_code_object(x)
    cell_names = co.co_cellvars + co.co_freevars
    linestarts = dict(findlinestarts(co))
    ikiwa first_line ni sio Tupu:
        line_offset = first_line - co.co_firstlineno
    isipokua:
        line_offset = 0
    rudisha _get_instructions_bytes(co.co_code, co.co_varnames, co.co_names,
                                   co.co_consts, cell_names, linestarts,
                                   line_offset)

eleza _get_const_info(const_index, const_list):
    """Helper to get optional details about const references

       Returns the dereferenced constant na its repr ikiwa the constant
       list ni defined.
       Otherwise returns the constant index na its repr().
    """
    argval = const_index
    ikiwa const_list ni sio Tupu:
        argval = const_list[const_index]
    rudisha argval, repr(argval)

eleza _get_name_info(name_index, name_list):
    """Helper to get optional details about named references

       Returns the dereferenced name kama both value na repr ikiwa the name
       list ni defined.
       Otherwise returns the name index na its repr().
    """
    argval = name_index
    ikiwa name_list ni sio Tupu:
        argval = name_list[name_index]
        argrepr = argval
    isipokua:
        argrepr = repr(argval)
    rudisha argval, argrepr


eleza _get_instructions_bytes(code, varnames=Tupu, names=Tupu, constants=Tupu,
                      cells=Tupu, linestarts=Tupu, line_offset=0):
    """Iterate over the instructions kwenye a bytecode string.

    Generates a sequence of Instruction namedtuples giving the details of each
    opcode.  Additional information about the code's runtime environment
    (e.g. variable names, constants) can be specified using optional
    arguments.

    """
    labels = findlabels(code)
    starts_line = Tupu
    kila offset, op, arg kwenye _unpack_opargs(code):
        ikiwa linestarts ni sio Tupu:
            starts_line = linestarts.get(offset, Tupu)
            ikiwa starts_line ni sio Tupu:
                starts_line += line_offset
        is_jump_target = offset kwenye labels
        argval = Tupu
        argrepr = ''
        ikiwa arg ni sio Tupu:
            #  Set argval to the dereferenced value of the argument when
            #  available, na argrepr to the string representation of argval.
            #    _disassemble_bytes needs the string repr of the
            #    raw name index kila LOAD_GLOBAL, LOAD_CONST, etc.
            argval = arg
            ikiwa op kwenye hasconst:
                argval, argrepr = _get_const_info(arg, constants)
            lasivyo op kwenye hasname:
                argval, argrepr = _get_name_info(arg, names)
            lasivyo op kwenye hasjrel:
                argval = offset + 2 + arg
                argrepr = "to " + repr(argval)
            lasivyo op kwenye haslocal:
                argval, argrepr = _get_name_info(arg, varnames)
            lasivyo op kwenye hascompare:
                argval = cmp_op[arg]
                argrepr = argval
            lasivyo op kwenye hasfree:
                argval, argrepr = _get_name_info(arg, cells)
            lasivyo op == FORMAT_VALUE:
                argval, argrepr = FORMAT_VALUE_CONVERTERS[arg & 0x3]
                argval = (argval, bool(arg & 0x4))
                ikiwa argval[1]:
                    ikiwa argrepr:
                        argrepr += ', '
                    argrepr += 'ukijumuisha format'
            lasivyo op == MAKE_FUNCTION:
                argrepr = ', '.join(s kila i, s kwenye enumerate(MAKE_FUNCTION_FLAGS)
                                    ikiwa arg & (1<<i))
        tuma Instruction(opname[op], op,
                          arg, argval, argrepr,
                          offset, starts_line, is_jump_target)

eleza disassemble(co, lasti=-1, *, file=Tupu):
    """Disassemble a code object."""
    cell_names = co.co_cellvars + co.co_freevars
    linestarts = dict(findlinestarts(co))
    _disassemble_bytes(co.co_code, lasti, co.co_varnames, co.co_names,
                       co.co_consts, cell_names, linestarts, file=file)

eleza _disassemble_recursive(co, *, file=Tupu, depth=Tupu):
    disassemble(co, file=file)
    ikiwa depth ni Tupu ama depth > 0:
        ikiwa depth ni sio Tupu:
            depth = depth - 1
        kila x kwenye co.co_consts:
            ikiwa hasattr(x, 'co_code'):
                andika(file=file)
                andika("Disassembly of %r:" % (x,), file=file)
                _disassemble_recursive(x, file=file, depth=depth)

eleza _disassemble_bytes(code, lasti=-1, varnames=Tupu, names=Tupu,
                       constants=Tupu, cells=Tupu, linestarts=Tupu,
                       *, file=Tupu, line_offset=0):
    # Omit the line number column entirely ikiwa we have no line number info
    show_lineno = linestarts ni sio Tupu
    ikiwa show_lineno:
        maxlineno = max(linestarts.values()) + line_offset
        ikiwa maxlineno >= 1000:
            lineno_width = len(str(maxlineno))
        isipokua:
            lineno_width = 3
    isipokua:
        lineno_width = 0
    maxoffset = len(code) - 2
    ikiwa maxoffset >= 10000:
        offset_width = len(str(maxoffset))
    isipokua:
        offset_width = 4
    kila instr kwenye _get_instructions_bytes(code, varnames, names,
                                         constants, cells, linestarts,
                                         line_offset=line_offset):
        new_source_line = (show_lineno na
                           instr.starts_line ni sio Tupu na
                           instr.offset > 0)
        ikiwa new_source_line:
            andika(file=file)
        is_current_instr = instr.offset == lasti
        andika(instr._disassemble(lineno_width, is_current_instr, offset_width),
              file=file)

eleza _disassemble_str(source, **kwargs):
    """Compile the source string, then disassemble the code object."""
    _disassemble_recursive(_try_compile(source, '<dis>'), **kwargs)

disco = disassemble                     # XXX For backwards compatibility

eleza _unpack_opargs(code):
    extended_arg = 0
    kila i kwenye range(0, len(code), 2):
        op = code[i]
        ikiwa op >= HAVE_ARGUMENT:
            arg = code[i+1] | extended_arg
            extended_arg = (arg << 8) ikiwa op == EXTENDED_ARG isipokua 0
        isipokua:
            arg = Tupu
        tuma (i, op, arg)

eleza findlabels(code):
    """Detect all offsets kwenye a byte code which are jump targets.

    Return the list of offsets.

    """
    labels = []
    kila offset, op, arg kwenye _unpack_opargs(code):
        ikiwa arg ni sio Tupu:
            ikiwa op kwenye hasjrel:
                label = offset + 2 + arg
            lasivyo op kwenye hasjabs:
                label = arg
            isipokua:
                endelea
            ikiwa label haiko kwenye labels:
                labels.append(label)
    rudisha labels

eleza findlinestarts(code):
    """Find the offsets kwenye a byte code which are start of lines kwenye the source.

    Generate pairs (offset, lineno) kama described kwenye Python/compile.c.

    """
    byte_increments = code.co_lnotab[0::2]
    line_increments = code.co_lnotab[1::2]
    bytecode_len = len(code.co_code)

    lastlineno = Tupu
    lineno = code.co_firstlineno
    addr = 0
    kila byte_incr, line_incr kwenye zip(byte_increments, line_increments):
        ikiwa byte_incr:
            ikiwa lineno != lastlineno:
                tuma (addr, lineno)
                lastlineno = lineno
            addr += byte_incr
            ikiwa addr >= bytecode_len:
                # The rest of the lnotab byte offsets are past the end of
                # the bytecode, so the lines were optimized away.
                rudisha
        ikiwa line_incr >= 0x80:
            # line_increments ni an array of 8-bit signed integers
            line_incr -= 0x100
        lineno += line_incr
    ikiwa lineno != lastlineno:
        tuma (addr, lineno)

kundi Bytecode:
    """The bytecode operations of a piece of code

    Instantiate this ukijumuisha a function, method, other compiled object, string of
    code, ama a code object (as returned by compile()).

    Iterating over this tumas the bytecode operations kama Instruction instances.
    """
    eleza __init__(self, x, *, first_line=Tupu, current_offset=Tupu):
        self.codeobj = co = _get_code_object(x)
        ikiwa first_line ni Tupu:
            self.first_line = co.co_firstlineno
            self._line_offset = 0
        isipokua:
            self.first_line = first_line
            self._line_offset = first_line - co.co_firstlineno
        self._cell_names = co.co_cellvars + co.co_freevars
        self._linestarts = dict(findlinestarts(co))
        self._original_object = x
        self.current_offset = current_offset

    eleza __iter__(self):
        co = self.codeobj
        rudisha _get_instructions_bytes(co.co_code, co.co_varnames, co.co_names,
                                       co.co_consts, self._cell_names,
                                       self._linestarts,
                                       line_offset=self._line_offset)

    eleza __repr__(self):
        rudisha "{}({!r})".format(self.__class__.__name__,
                                 self._original_object)

    @classmethod
    eleza from_traceback(cls, tb):
        """ Construct a Bytecode kutoka the given traceback """
        wakati tb.tb_next:
            tb = tb.tb_next
        rudisha cls(tb.tb_frame.f_code, current_offset=tb.tb_lasti)

    eleza info(self):
        """Return formatted information about the code object."""
        rudisha _format_code_info(self.codeobj)

    eleza dis(self):
        """Return a formatted view of the bytecode operations."""
        co = self.codeobj
        ikiwa self.current_offset ni sio Tupu:
            offset = self.current_offset
        isipokua:
            offset = -1
        ukijumuisha io.StringIO() kama output:
            _disassemble_bytes(co.co_code, varnames=co.co_varnames,
                               names=co.co_names, constants=co.co_consts,
                               cells=self._cell_names,
                               linestarts=self._linestarts,
                               line_offset=self._line_offset,
                               file=output,
                               lasti=offset)
            rudisha output.getvalue()


eleza _test():
    """Simple test program to disassemble a file."""
    agiza argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('infile', type=argparse.FileType(), nargs='?', default='-')
    args = parser.parse_args()
    ukijumuisha args.infile kama infile:
        source = infile.read()
    code = compile(source, args.infile.name, "exec")
    dis(code)

ikiwa __name__ == "__main__":
    _test()
