r"""Utilities to compile possibly incomplete Python source code.

This module provides two interfaces, broadly similar to the builtin
function compile(), which take program text, a filename na a 'mode'
and:

- Return code object ikiwa the command ni complete na valid
- Return Tupu ikiwa the command ni incomplete
- Raise SyntaxError, ValueError ama OverflowError ikiwa the command ni a
  syntax error (OverflowError na ValueError can be produced by
  malformed literals).

Approach:

First, check ikiwa the source consists entirely of blank lines na
comments; ikiwa so, replace it ukijumuisha 'pita', because the built-in
parser doesn't always do the right thing kila these.

Compile three times: kama is, ukijumuisha \n, na ukijumuisha \n\n appended.  If it
compiles kama is, it's complete.  If it compiles ukijumuisha one \n appended,
we expect more.  If it doesn't compile either way, we compare the
error we get when compiling ukijumuisha \n ama \n\n appended.  If the errors
are the same, the code ni broken.  But ikiwa the errors are different, we
expect more.  Not intuitive; sio even guaranteed to hold kwenye future
releases; but this matches the compiler's behavior kutoka Python 1.4
through 2.2, at least.

Caveat:

It ni possible (but sio likely) that the parser stops parsing ukijumuisha a
successful outcome before reaching the end of the source; kwenye this
case, trailing symbols may be ignored instead of causing an error.
For example, a backslash followed by two newlines may be followed by
arbitrary garbage.  This will be fixed once the API kila the parser is
better.

The two interfaces are:

compile_command(source, filename, symbol):

    Compiles a single command kwenye the manner described above.

CommandCompiler():

    Instances of this kundi have __call__ methods identical in
    signature to compile_command; the difference ni that ikiwa the
    instance compiles program text containing a __future__ statement,
    the instance 'remembers' na compiles all subsequent program texts
    ukijumuisha the statement kwenye force.

The module also provides another class:

Compile():

    Instances of this kundi act like the built-in function compile,
    but ukijumuisha 'memory' kwenye the sense described above.
"""

agiza __future__

_features = [getattr(__future__, fname)
             kila fname kwenye __future__.all_feature_names]

__all__ = ["compile_command", "Compile", "CommandCompiler"]

PyCF_DONT_IMPLY_DEDENT = 0x200          # Matches pythonrun.h

eleza _maybe_compile(compiler, source, filename, symbol):
    # Check kila source consisting of only blank lines na comments
    kila line kwenye source.split("\n"):
        line = line.strip()
        ikiwa line na line[0] != '#':
            koma               # Leave it alone
    isipokua:
        ikiwa symbol != "eval":
            source = "pita"     # Replace it ukijumuisha a 'pita' statement

    err = err1 = err2 = Tupu
    code = code1 = code2 = Tupu

    jaribu:
        code = compiler(source, filename, symbol)
    tatizo SyntaxError kama err:
        pita

    jaribu:
        code1 = compiler(source + "\n", filename, symbol)
    tatizo SyntaxError kama e:
        err1 = e

    jaribu:
        code2 = compiler(source + "\n\n", filename, symbol)
    tatizo SyntaxError kama e:
        err2 = e

    ikiwa code:
        rudisha code
    ikiwa sio code1 na repr(err1) == repr(err2):
        ashiria err1

eleza _compile(source, filename, symbol):
    rudisha compile(source, filename, symbol, PyCF_DONT_IMPLY_DEDENT)

eleza compile_command(source, filename="<input>", symbol="single"):
    r"""Compile a command na determine whether it ni incomplete.

    Arguments:

    source -- the source string; may contain \n characters
    filename -- optional filename kutoka which source was read; default
                "<input>"
    symbol -- optional grammar start symbol; "single" (default) ama "eval"

    Return value / exceptions ashiriad:

    - Return a code object ikiwa the command ni complete na valid
    - Return Tupu ikiwa the command ni incomplete
    - Raise SyntaxError, ValueError ama OverflowError ikiwa the command ni a
      syntax error (OverflowError na ValueError can be produced by
      malformed literals).
    """
    rudisha _maybe_compile(_compile, source, filename, symbol)

kundi Compile:
    """Instances of this kundi behave much like the built-in compile
    function, but ikiwa one ni used to compile text containing a future
    statement, it "remembers" na compiles all subsequent program texts
    ukijumuisha the statement kwenye force."""
    eleza __init__(self):
        self.flags = PyCF_DONT_IMPLY_DEDENT

    eleza __call__(self, source, filename, symbol):
        codeob = compile(source, filename, symbol, self.flags, 1)
        kila feature kwenye _features:
            ikiwa codeob.co_flags & feature.compiler_flag:
                self.flags |= feature.compiler_flag
        rudisha codeob

kundi CommandCompiler:
    """Instances of this kundi have __call__ methods identical in
    signature to compile_command; the difference ni that ikiwa the
    instance compiles program text containing a __future__ statement,
    the instance 'remembers' na compiles all subsequent program texts
    ukijumuisha the statement kwenye force."""

    eleza __init__(self,):
        self.compiler = Compile()

    eleza __call__(self, source, filename="<input>", symbol="single"):
        r"""Compile a command na determine whether it ni incomplete.

        Arguments:

        source -- the source string; may contain \n characters
        filename -- optional filename kutoka which source was read;
                    default "<input>"
        symbol -- optional grammar start symbol; "single" (default) ama
                  "eval"

        Return value / exceptions ashiriad:

        - Return a code object ikiwa the command ni complete na valid
        - Return Tupu ikiwa the command ni incomplete
        - Raise SyntaxError, ValueError ama OverflowError ikiwa the command ni a
          syntax error (OverflowError na ValueError can be produced by
          malformed literals).
        """
        rudisha _maybe_compile(self.compiler, source, filename, symbol)
