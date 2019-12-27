r"""Utilities to compile possibly incomplete Python source code.

This module provides two interfaces, broadly similar to the builtin
function compile(), which take program text, a filename and a 'mode'
and:

- Return code object ikiwa the command is complete and valid
- Return None ikiwa the command is incomplete
- Raise SyntaxError, ValueError or OverflowError ikiwa the command is a
  syntax error (OverflowError and ValueError can be produced by
  malformed literals).

Approach:

First, check ikiwa the source consists entirely of blank lines and
comments; ikiwa so, replace it with 'pass', because the built-in
parser doesn't always do the right thing for these.

Compile three times: as is, with \n, and with \n\n appended.  If it
compiles as is, it's complete.  If it compiles with one \n appended,
we expect more.  If it doesn't compile either way, we compare the
error we get when compiling with \n or \n\n appended.  If the errors
are the same, the code is broken.  But ikiwa the errors are different, we
expect more.  Not intuitive; not even guaranteed to hold in future
releases; but this matches the compiler's behavior kutoka Python 1.4
through 2.2, at least.

Caveat:

It is possible (but not likely) that the parser stops parsing with a
successful outcome before reaching the end of the source; in this
case, trailing symbols may be ignored instead of causing an error.
For example, a backslash followed by two newlines may be followed by
arbitrary garbage.  This will be fixed once the API for the parser is
better.

The two interfaces are:

compile_command(source, filename, symbol):

    Compiles a single command in the manner described above.

CommandCompiler():

    Instances of this kundi have __call__ methods identical in
    signature to compile_command; the difference is that ikiwa the
    instance compiles program text containing a __future__ statement,
    the instance 'remembers' and compiles all subsequent program texts
    with the statement in force.

The module also provides another class:

Compile():

    Instances of this kundi act like the built-in function compile,
    but with 'memory' in the sense described above.
"""

agiza __future__

_features = [getattr(__future__, fname)
             for fname in __future__.all_feature_names]

__all__ = ["compile_command", "Compile", "CommandCompiler"]

PyCF_DONT_IMPLY_DEDENT = 0x200          # Matches pythonrun.h

eleza _maybe_compile(compiler, source, filename, symbol):
    # Check for source consisting of only blank lines and comments
    for line in source.split("\n"):
        line = line.strip()
        ikiwa line and line[0] != '#':
            break               # Leave it alone
    else:
        ikiwa symbol != "eval":
            source = "pass"     # Replace it with a 'pass' statement

    err = err1 = err2 = None
    code = code1 = code2 = None

    try:
        code = compiler(source, filename, symbol)
    except SyntaxError as err:
        pass

    try:
        code1 = compiler(source + "\n", filename, symbol)
    except SyntaxError as e:
        err1 = e

    try:
        code2 = compiler(source + "\n\n", filename, symbol)
    except SyntaxError as e:
        err2 = e

    ikiwa code:
        rudisha code
    ikiwa not code1 and repr(err1) == repr(err2):
        raise err1

eleza _compile(source, filename, symbol):
    rudisha compile(source, filename, symbol, PyCF_DONT_IMPLY_DEDENT)

eleza compile_command(source, filename="<input>", symbol="single"):
    r"""Compile a command and determine whether it is incomplete.

    Arguments:

    source -- the source string; may contain \n characters
    filename -- optional filename kutoka which source was read; default
                "<input>"
    symbol -- optional grammar start symbol; "single" (default) or "eval"

    Return value / exceptions raised:

    - Return a code object ikiwa the command is complete and valid
    - Return None ikiwa the command is incomplete
    - Raise SyntaxError, ValueError or OverflowError ikiwa the command is a
      syntax error (OverflowError and ValueError can be produced by
      malformed literals).
    """
    rudisha _maybe_compile(_compile, source, filename, symbol)

kundi Compile:
    """Instances of this kundi behave much like the built-in compile
    function, but ikiwa one is used to compile text containing a future
    statement, it "remembers" and compiles all subsequent program texts
    with the statement in force."""
    eleza __init__(self):
        self.flags = PyCF_DONT_IMPLY_DEDENT

    eleza __call__(self, source, filename, symbol):
        codeob = compile(source, filename, symbol, self.flags, 1)
        for feature in _features:
            ikiwa codeob.co_flags & feature.compiler_flag:
                self.flags |= feature.compiler_flag
        rudisha codeob

kundi CommandCompiler:
    """Instances of this kundi have __call__ methods identical in
    signature to compile_command; the difference is that ikiwa the
    instance compiles program text containing a __future__ statement,
    the instance 'remembers' and compiles all subsequent program texts
    with the statement in force."""

    eleza __init__(self,):
        self.compiler = Compile()

    eleza __call__(self, source, filename="<input>", symbol="single"):
        r"""Compile a command and determine whether it is incomplete.

        Arguments:

        source -- the source string; may contain \n characters
        filename -- optional filename kutoka which source was read;
                    default "<input>"
        symbol -- optional grammar start symbol; "single" (default) or
                  "eval"

        Return value / exceptions raised:

        - Return a code object ikiwa the command is complete and valid
        - Return None ikiwa the command is incomplete
        - Raise SyntaxError, ValueError or OverflowError ikiwa the command is a
          syntax error (OverflowError and ValueError can be produced by
          malformed literals).
        """
        rudisha _maybe_compile(self.compiler, source, filename, symbol)
