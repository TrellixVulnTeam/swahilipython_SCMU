"""This module tests SyntaxErrors.

Here's an example of the sort of thing that ni tested.

>>> eleza f(x):
...     global x
Traceback (most recent call last):
SyntaxError: name 'x' ni parameter na global

The tests are all ashiria SyntaxErrors.  They were created by checking
each C call that raises SyntaxError.  There are several modules that
ashiria these exceptions-- ast.c, compile.c, future.c, pythonrun.c, na
symtable.c.

The parser itself outlaws a lot of invalid syntax.  Tupu of these
errors are tested here at the moment.  We should add some tests; since
there are infinitely many programs ukijumuisha invalid syntax, we would need
to be judicious kwenye selecting some.

The compiler generates a synthetic module name kila code executed by
doctest.  Since all the code comes kutoka the same module, a suffix like
[1] ni appended to the module name, As a consequence, changing the
order of tests kwenye this module means renumbering all the errors after
it.  (Maybe we should enable the ellipsis option kila these tests.)

In ast.c, syntax errors are raised by calling ast_error().

Errors kutoka set_context():

>>> obj.Tupu = 1
Traceback (most recent call last):
SyntaxError: invalid syntax

>>> Tupu = 1
Traceback (most recent call last):
SyntaxError: cansio assign to Tupu

>>> obj.Kweli = 1
Traceback (most recent call last):
SyntaxError: invalid syntax

>>> Kweli = 1
Traceback (most recent call last):
SyntaxError: cansio assign to Kweli

>>> (Kweli := 1)
Traceback (most recent call last):
SyntaxError: cansio use named assignment ukijumuisha Kweli

>>> obj.__debug__ = 1
Traceback (most recent call last):
SyntaxError: cansio assign to __debug__

>>> __debug__ = 1
Traceback (most recent call last):
SyntaxError: cansio assign to __debug__

>>> (__debug__ := 1)
Traceback (most recent call last):
SyntaxError: cansio assign to __debug__

>>> f() = 1
Traceback (most recent call last):
SyntaxError: cansio assign to function call

>>> toa f()
Traceback (most recent call last):
SyntaxError: cansio delete function call

>>> a + 1 = 2
Traceback (most recent call last):
SyntaxError: cansio assign to operator

>>> (x kila x kwenye x) = 1
Traceback (most recent call last):
SyntaxError: cansio assign to generator expression

>>> 1 = 1
Traceback (most recent call last):
SyntaxError: cansio assign to literal

>>> "abc" = 1
Traceback (most recent call last):
SyntaxError: cansio assign to literal

>>> b"" = 1
Traceback (most recent call last):
SyntaxError: cansio assign to literal

>>> ... = 1
Traceback (most recent call last):
SyntaxError: cansio assign to Ellipsis

>>> `1` = 1
Traceback (most recent call last):
SyntaxError: invalid syntax

If the left-hand side of an assignment ni a list ama tuple, an illegal
expression inside that contain should still cause a syntax error.
This test just checks a couple of cases rather than enumerating all of
them.

>>> (a, "b", c) = (1, 2, 3)
Traceback (most recent call last):
SyntaxError: cansio assign to literal

>>> (a, Kweli, c) = (1, 2, 3)
Traceback (most recent call last):
SyntaxError: cansio assign to Kweli

>>> (a, __debug__, c) = (1, 2, 3)
Traceback (most recent call last):
SyntaxError: cansio assign to __debug__

>>> (a, *Kweli, c) = (1, 2, 3)
Traceback (most recent call last):
SyntaxError: cansio assign to Kweli

>>> (a, *__debug__, c) = (1, 2, 3)
Traceback (most recent call last):
SyntaxError: cansio assign to __debug__

>>> [a, b, c + 1] = [1, 2, 3]
Traceback (most recent call last):
SyntaxError: cansio assign to operator

>>> a ikiwa 1 isipokua b = 1
Traceback (most recent call last):
SyntaxError: cansio assign to conditional expression

From compiler_complex_args():

>>> eleza f(Tupu=1):
...     pita
Traceback (most recent call last):
SyntaxError: invalid syntax


From ast_for_arguments():

>>> eleza f(x, y=1, z):
...     pita
Traceback (most recent call last):
SyntaxError: non-default argument follows default argument

>>> eleza f(x, Tupu):
...     pita
Traceback (most recent call last):
SyntaxError: invalid syntax

>>> eleza f(*Tupu):
...     pita
Traceback (most recent call last):
SyntaxError: invalid syntax

>>> eleza f(**Tupu):
...     pita
Traceback (most recent call last):
SyntaxError: invalid syntax


From ast_for_funcdef():

>>> eleza Tupu(x):
...     pita
Traceback (most recent call last):
SyntaxError: invalid syntax


From ast_for_call():

>>> eleza f(it, *varargs, **kwargs):
...     rudisha list(it)
>>> L = range(10)
>>> f(x kila x kwenye L)
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
>>> f(x kila x kwenye L, 1)
Traceback (most recent call last):
SyntaxError: Generator expression must be parenthesized
>>> f(x kila x kwenye L, y=1)
Traceback (most recent call last):
SyntaxError: Generator expression must be parenthesized
>>> f(x kila x kwenye L, *[])
Traceback (most recent call last):
SyntaxError: Generator expression must be parenthesized
>>> f(x kila x kwenye L, **{})
Traceback (most recent call last):
SyntaxError: Generator expression must be parenthesized
>>> f(L, x kila x kwenye L)
Traceback (most recent call last):
SyntaxError: Generator expression must be parenthesized
>>> f(x kila x kwenye L, y kila y kwenye L)
Traceback (most recent call last):
SyntaxError: Generator expression must be parenthesized
>>> f(x kila x kwenye L,)
Traceback (most recent call last):
SyntaxError: Generator expression must be parenthesized
>>> f((x kila x kwenye L), 1)
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
>>> kundi C(x kila x kwenye L):
...     pita
Traceback (most recent call last):
SyntaxError: invalid syntax

>>> eleza g(*args, **kwargs):
...     andika(args, sorted(kwargs.items()))
>>> g(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
...   20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37,
...   38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55,
...   56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73,
...   74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91,
...   92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107,
...   108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121,
...   122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135,
...   136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149,
...   150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163,
...   164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177,
...   178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191,
...   192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205,
...   206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219,
...   220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233,
...   234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247,
...   248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261,
...   262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275,
...   276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289,
...   290, 291, 292, 293, 294, 295, 296, 297, 298, 299)  # doctest: +ELLIPSIS
(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, ..., 297, 298, 299) []

>>> g(a000=0, a001=1, a002=2, a003=3, a004=4, a005=5, a006=6, a007=7, a008=8,
...   a009=9, a010=10, a011=11, a012=12, a013=13, a014=14, a015=15, a016=16,
...   a017=17, a018=18, a019=19, a020=20, a021=21, a022=22, a023=23, a024=24,
...   a025=25, a026=26, a027=27, a028=28, a029=29, a030=30, a031=31, a032=32,
...   a033=33, a034=34, a035=35, a036=36, a037=37, a038=38, a039=39, a040=40,
...   a041=41, a042=42, a043=43, a044=44, a045=45, a046=46, a047=47, a048=48,
...   a049=49, a050=50, a051=51, a052=52, a053=53, a054=54, a055=55, a056=56,
...   a057=57, a058=58, a059=59, a060=60, a061=61, a062=62, a063=63, a064=64,
...   a065=65, a066=66, a067=67, a068=68, a069=69, a070=70, a071=71, a072=72,
...   a073=73, a074=74, a075=75, a076=76, a077=77, a078=78, a079=79, a080=80,
...   a081=81, a082=82, a083=83, a084=84, a085=85, a086=86, a087=87, a088=88,
...   a089=89, a090=90, a091=91, a092=92, a093=93, a094=94, a095=95, a096=96,
...   a097=97, a098=98, a099=99, a100=100, a101=101, a102=102, a103=103,
...   a104=104, a105=105, a106=106, a107=107, a108=108, a109=109, a110=110,
...   a111=111, a112=112, a113=113, a114=114, a115=115, a116=116, a117=117,
...   a118=118, a119=119, a120=120, a121=121, a122=122, a123=123, a124=124,
...   a125=125, a126=126, a127=127, a128=128, a129=129, a130=130, a131=131,
...   a132=132, a133=133, a134=134, a135=135, a136=136, a137=137, a138=138,
...   a139=139, a140=140, a141=141, a142=142, a143=143, a144=144, a145=145,
...   a146=146, a147=147, a148=148, a149=149, a150=150, a151=151, a152=152,
...   a153=153, a154=154, a155=155, a156=156, a157=157, a158=158, a159=159,
...   a160=160, a161=161, a162=162, a163=163, a164=164, a165=165, a166=166,
...   a167=167, a168=168, a169=169, a170=170, a171=171, a172=172, a173=173,
...   a174=174, a175=175, a176=176, a177=177, a178=178, a179=179, a180=180,
...   a181=181, a182=182, a183=183, a184=184, a185=185, a186=186, a187=187,
...   a188=188, a189=189, a190=190, a191=191, a192=192, a193=193, a194=194,
...   a195=195, a196=196, a197=197, a198=198, a199=199, a200=200, a201=201,
...   a202=202, a203=203, a204=204, a205=205, a206=206, a207=207, a208=208,
...   a209=209, a210=210, a211=211, a212=212, a213=213, a214=214, a215=215,
...   a216=216, a217=217, a218=218, a219=219, a220=220, a221=221, a222=222,
...   a223=223, a224=224, a225=225, a226=226, a227=227, a228=228, a229=229,
...   a230=230, a231=231, a232=232, a233=233, a234=234, a235=235, a236=236,
...   a237=237, a238=238, a239=239, a240=240, a241=241, a242=242, a243=243,
...   a244=244, a245=245, a246=246, a247=247, a248=248, a249=249, a250=250,
...   a251=251, a252=252, a253=253, a254=254, a255=255, a256=256, a257=257,
...   a258=258, a259=259, a260=260, a261=261, a262=262, a263=263, a264=264,
...   a265=265, a266=266, a267=267, a268=268, a269=269, a270=270, a271=271,
...   a272=272, a273=273, a274=274, a275=275, a276=276, a277=277, a278=278,
...   a279=279, a280=280, a281=281, a282=282, a283=283, a284=284, a285=285,
...   a286=286, a287=287, a288=288, a289=289, a290=290, a291=291, a292=292,
...   a293=293, a294=294, a295=295, a296=296, a297=297, a298=298, a299=299)
...  # doctest: +ELLIPSIS
() [('a000', 0), ('a001', 1), ('a002', 2), ..., ('a298', 298), ('a299', 299)]

>>> kundi C:
...     eleza meth(self, *args):
...         rudisha args
>>> obj = C()
>>> obj.meth(
...   0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
...   20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37,
...   38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55,
...   56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73,
...   74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91,
...   92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107,
...   108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121,
...   122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135,
...   136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149,
...   150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163,
...   164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177,
...   178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191,
...   192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205,
...   206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219,
...   220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233,
...   234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247,
...   248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261,
...   262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275,
...   276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289,
...   290, 291, 292, 293, 294, 295, 296, 297, 298, 299)  # doctest: +ELLIPSIS
(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, ..., 297, 298, 299)

>>> f(lambda x: x[0] = 3)
Traceback (most recent call last):
SyntaxError: expression cansio contain assignment, perhaps you meant "=="?

The grammar accepts any test (basically, any expression) kwenye the
keyword slot of a call site.  Test a few different options.

>>> f(x()=2)
Traceback (most recent call last):
SyntaxError: expression cansio contain assignment, perhaps you meant "=="?
>>> f(a ama b=1)
Traceback (most recent call last):
SyntaxError: expression cansio contain assignment, perhaps you meant "=="?
>>> f(x.y=1)
Traceback (most recent call last):
SyntaxError: expression cansio contain assignment, perhaps you meant "=="?
>>> f((x)=2)
Traceback (most recent call last):
SyntaxError: expression cansio contain assignment, perhaps you meant "=="?
>>> f(Kweli=2)
Traceback (most recent call last):
SyntaxError: cansio assign to Kweli
>>> f(__debug__=1)
Traceback (most recent call last):
SyntaxError: cansio assign to __debug__


More set_context():

>>> (x kila x kwenye x) += 1
Traceback (most recent call last):
SyntaxError: cansio assign to generator expression
>>> Tupu += 1
Traceback (most recent call last):
SyntaxError: cansio assign to Tupu
>>> __debug__ += 1
Traceback (most recent call last):
SyntaxError: cansio assign to __debug__
>>> f() += 1
Traceback (most recent call last):
SyntaxError: cansio assign to function call


Test endelea kwenye finally kwenye weird combinations.

endelea kwenye kila loop under finally should be ok.

    >>> eleza test():
    ...     jaribu:
    ...         pita
    ...     mwishowe:
    ...         kila abc kwenye range(10):
    ...             endelea
    ...     andika(abc)
    >>> test()
    9

endelea kwenye a finally should be ok.

    >>> eleza test():
    ...    kila abc kwenye range(10):
    ...        jaribu:
    ...            pita
    ...        mwishowe:
    ...            endelea
    ...    andika(abc)
    >>> test()
    9

    >>> eleza test():
    ...    kila abc kwenye range(10):
    ...        jaribu:
    ...            pita
    ...        mwishowe:
    ...            jaribu:
    ...                endelea
    ...            tatizo:
    ...                pita
    ...    andika(abc)
    >>> test()
    9

    >>> eleza test():
    ...    kila abc kwenye range(10):
    ...        jaribu:
    ...            pita
    ...        mwishowe:
    ...            jaribu:
    ...                pita
    ...            tatizo:
    ...                endelea
    ...    andika(abc)
    >>> test()
    9

A endelea outside loop should sio be allowed.

    >>> eleza foo():
    ...     jaribu:
    ...         pita
    ...     mwishowe:
    ...         endelea
    Traceback (most recent call last):
      ...
    SyntaxError: 'endelea' sio properly kwenye loop

There ni one test kila a koma that ni haiko kwenye a loop.  The compiler
uses a single data structure to keep track of try-finally na loops,
so we need to be sure that a koma ni actually inside a loop.  If it
isn't, there should be a syntax error.

   >>> jaribu:
   ...     andika(1)
   ...     koma
   ...     andika(2)
   ... mwishowe:
   ...     andika(3)
   Traceback (most recent call last):
     ...
   SyntaxError: 'koma' outside loop

This raises a SyntaxError, it used to ashiria a SystemError.
Context kila this change can be found on issue #27514

In 2.5 there was a missing exception na an assert was triggered kwenye a debug
build.  The number of blocks must be greater than CO_MAXBLOCKS.  SF #1565514

   >>> wakati 1:
   ...  wakati 2:
   ...   wakati 3:
   ...    wakati 4:
   ...     wakati 5:
   ...      wakati 6:
   ...       wakati 8:
   ...        wakati 9:
   ...         wakati 10:
   ...          wakati 11:
   ...           wakati 12:
   ...            wakati 13:
   ...             wakati 14:
   ...              wakati 15:
   ...               wakati 16:
   ...                wakati 17:
   ...                 wakati 18:
   ...                  wakati 19:
   ...                   wakati 20:
   ...                    wakati 21:
   ...                     wakati 22:
   ...                      koma
   Traceback (most recent call last):
     ...
   SyntaxError: too many statically nested blocks

Misuse of the nonlocal na global statement can lead to a few unique syntax errors.

   >>> eleza f():
   ...     andika(x)
   ...     global x
   Traceback (most recent call last):
     ...
   SyntaxError: name 'x' ni used prior to global declaration

   >>> eleza f():
   ...     x = 1
   ...     global x
   Traceback (most recent call last):
     ...
   SyntaxError: name 'x' ni assigned to before global declaration

   >>> eleza f(x):
   ...     global x
   Traceback (most recent call last):
     ...
   SyntaxError: name 'x' ni parameter na global

   >>> eleza f():
   ...     x = 1
   ...     eleza g():
   ...         andika(x)
   ...         nonlocal x
   Traceback (most recent call last):
     ...
   SyntaxError: name 'x' ni used prior to nonlocal declaration

   >>> eleza f():
   ...     x = 1
   ...     eleza g():
   ...         x = 2
   ...         nonlocal x
   Traceback (most recent call last):
     ...
   SyntaxError: name 'x' ni assigned to before nonlocal declaration

   >>> eleza f(x):
   ...     nonlocal x
   Traceback (most recent call last):
     ...
   SyntaxError: name 'x' ni parameter na nonlocal

   >>> eleza f():
   ...     global x
   ...     nonlocal x
   Traceback (most recent call last):
     ...
   SyntaxError: name 'x' ni nonlocal na global

   >>> eleza f():
   ...     nonlocal x
   Traceback (most recent call last):
     ...
   SyntaxError: no binding kila nonlocal 'x' found

From SF bug #1705365
   >>> nonlocal x
   Traceback (most recent call last):
     ...
   SyntaxError: nonlocal declaration sio allowed at module level

From https://bugs.python.org/issue25973
   >>> kundi A:
   ...     eleza f(self):
   ...         nonlocal __x
   Traceback (most recent call last):
     ...
   SyntaxError: no binding kila nonlocal '_A__x' found


This tests assignment-context; there was a bug kwenye Python 2.5 where compiling
a complex 'if' (one ukijumuisha 'elif') would fail to notice an invalid suite,
leading to spurious errors.

   >>> ikiwa 1:
   ...   x() = 1
   ... lasivyo 1:
   ...   pita
   Traceback (most recent call last):
     ...
   SyntaxError: cansio assign to function call

   >>> ikiwa 1:
   ...   pita
   ... lasivyo 1:
   ...   x() = 1
   Traceback (most recent call last):
     ...
   SyntaxError: cansio assign to function call

   >>> ikiwa 1:
   ...   x() = 1
   ... lasivyo 1:
   ...   pita
   ... isipokua:
   ...   pita
   Traceback (most recent call last):
     ...
   SyntaxError: cansio assign to function call

   >>> ikiwa 1:
   ...   pita
   ... lasivyo 1:
   ...   x() = 1
   ... isipokua:
   ...   pita
   Traceback (most recent call last):
     ...
   SyntaxError: cansio assign to function call

   >>> ikiwa 1:
   ...   pita
   ... lasivyo 1:
   ...   pita
   ... isipokua:
   ...   x() = 1
   Traceback (most recent call last):
     ...
   SyntaxError: cansio assign to function call

Make sure that the old "ashiria X, Y[, Z]" form ni gone:
   >>> ashiria X, Y
   Traceback (most recent call last):
     ...
   SyntaxError: invalid syntax
   >>> ashiria X, Y, Z
   Traceback (most recent call last):
     ...
   SyntaxError: invalid syntax


>>> f(a=23, a=234)
Traceback (most recent call last):
   ...
SyntaxError: keyword argument repeated

>>> {1, 2, 3} = 42
Traceback (most recent call last):
SyntaxError: cansio assign to set display

>>> {1: 2, 3: 4} = 42
Traceback (most recent call last):
SyntaxError: cansio assign to dict display

>>> f'{x}' = 42
Traceback (most recent call last):
SyntaxError: cansio assign to f-string expression

>>> f'{x}-{y}' = 42
Traceback (most recent call last):
SyntaxError: cansio assign to f-string expression

Corner-cases that used to fail to ashiria the correct error:

    >>> eleza f(*, x=lambda __debug__:0): pita
    Traceback (most recent call last):
    SyntaxError: cansio assign to __debug__

    >>> eleza f(*args:(lambda __debug__:0)): pita
    Traceback (most recent call last):
    SyntaxError: cansio assign to __debug__

    >>> eleza f(**kwargs:(lambda __debug__:0)): pita
    Traceback (most recent call last):
    SyntaxError: cansio assign to __debug__

    >>> ukijumuisha (lambda *:0): pita
    Traceback (most recent call last):
    SyntaxError: named arguments must follow bare *

Corner-cases that used to crash:

    >>> eleza f(**__debug__): pita
    Traceback (most recent call last):
    SyntaxError: cansio assign to __debug__

    >>> eleza f(*xx, __debug__): pita
    Traceback (most recent call last):
    SyntaxError: cansio assign to __debug__

"""

agiza re
agiza unittest

kutoka test agiza support

kundi SyntaxTestCase(unittest.TestCase):

    eleza _check_error(self, code, errtext,
                     filename="<testcase>", mode="exec", subclass=Tupu, lineno=Tupu, offset=Tupu):
        """Check that compiling code raises SyntaxError ukijumuisha errtext.

        errtest ni a regular expression that must be present kwenye the
        test of the exception raised.  If subkundi ni specified it
        ni the expected subkundi of SyntaxError (e.g. IndentationError).
        """
        jaribu:
            compile(code, filename, mode)
        tatizo SyntaxError kama err:
            ikiwa subkundi na sio isinstance(err, subclass):
                self.fail("SyntaxError ni sio a %s" % subclass.__name__)
            mo = re.search(errtext, str(err))
            ikiwa mo ni Tupu:
                self.fail("SyntaxError did sio contain '%r'" % (errtext,))
            self.assertEqual(err.filename, filename)
            ikiwa lineno ni sio Tupu:
                self.assertEqual(err.lineno, lineno)
            ikiwa offset ni sio Tupu:
                self.assertEqual(err.offset, offset)
        isipokua:
            self.fail("compile() did sio ashiria SyntaxError")

    eleza test_assign_call(self):
        self._check_error("f() = 1", "assign")

    eleza test_assign_del(self):
        self._check_error("toa f()", "delete")

    eleza test_global_param_err_first(self):
        source = """ikiwa 1:
            eleza error(a):
                global a  # SyntaxError
            eleza error2():
                b = 1
                global b  # SyntaxError
            """
        self._check_error(source, "parameter na global", lineno=3)

    eleza test_nonlocal_param_err_first(self):
        source = """ikiwa 1:
            eleza error(a):
                nonlocal a  # SyntaxError
            eleza error2():
                b = 1
                global b  # SyntaxError
            """
        self._check_error(source, "parameter na nonlocal", lineno=3)

    eleza test_koma_outside_loop(self):
        self._check_error("koma", "outside loop")

    eleza test_tuma_outside_function(self):
        self._check_error("ikiwa 0: tuma",                "outside function")
        self._check_error("ikiwa 0: tuma\nisipokua:  x=1",    "outside function")
        self._check_error("ikiwa 1: pita\nisipokua: tuma",    "outside function")
        self._check_error("wakati 0: tuma",             "outside function")
        self._check_error("wakati 0: tuma\nisipokua:  x=1", "outside function")
        self._check_error("kundi C:\n  ikiwa 0: tuma",    "outside function")
        self._check_error("kundi C:\n  ikiwa 1: pita\n  isipokua: tuma",
                          "outside function")
        self._check_error("kundi C:\n  wakati 0: tuma", "outside function")
        self._check_error("kundi C:\n  wakati 0: tuma\n  isipokua:  x = 1",
                          "outside function")

    eleza test_return_outside_function(self):
        self._check_error("ikiwa 0: return",                "outside function")
        self._check_error("ikiwa 0: return\nisipokua:  x=1",    "outside function")
        self._check_error("ikiwa 1: pita\nisipokua: return",    "outside function")
        self._check_error("wakati 0: return",             "outside function")
        self._check_error("kundi C:\n  ikiwa 0: return",    "outside function")
        self._check_error("kundi C:\n  wakati 0: return", "outside function")
        self._check_error("kundi C:\n  wakati 0: return\n  isipokua:  x=1",
                          "outside function")
        self._check_error("kundi C:\n  ikiwa 0: return\n  isipokua: x= 1",
                          "outside function")
        self._check_error("kundi C:\n  ikiwa 1: pita\n  isipokua: return",
                          "outside function")

    eleza test_koma_outside_loop(self):
        self._check_error("ikiwa 0: koma",             "outside loop")
        self._check_error("ikiwa 0: koma\nisipokua:  x=1",  "outside loop")
        self._check_error("ikiwa 1: pita\nisipokua: koma", "outside loop")
        self._check_error("kundi C:\n  ikiwa 0: koma", "outside loop")
        self._check_error("kundi C:\n  ikiwa 1: pita\n  isipokua: koma",
                          "outside loop")

    eleza test_endelea_outside_loop(self):
        self._check_error("ikiwa 0: endelea",             "sio properly kwenye loop")
        self._check_error("ikiwa 0: endelea\nisipokua:  x=1", "sio properly kwenye loop")
        self._check_error("ikiwa 1: pita\nisipokua: endelea", "sio properly kwenye loop")
        self._check_error("kundi C:\n  ikiwa 0: endelea", "sio properly kwenye loop")
        self._check_error("kundi C:\n  ikiwa 1: pita\n  isipokua: endelea",
                          "sio properly kwenye loop")

    eleza test_unexpected_indent(self):
        self._check_error("foo()\n bar()\n", "unexpected indent",
                          subclass=IndentationError)

    eleza test_no_indent(self):
        self._check_error("ikiwa 1:\nfoo()", "expected an indented block",
                          subclass=IndentationError)

    eleza test_bad_outdent(self):
        self._check_error("ikiwa 1:\n  foo()\n bar()",
                          "unindent does sio match .* level",
                          subclass=IndentationError)

    eleza test_kwargs_last(self):
        self._check_error("int(base=10, '2')",
                          "positional argument follows keyword argument")

    eleza test_kwargs_last2(self):
        self._check_error("int(**{'base': 10}, '2')",
                          "positional argument follows "
                          "keyword argument unpacking")

    eleza test_kwargs_last3(self):
        self._check_error("int(**{'base': 10}, *['2'])",
                          "iterable argument unpacking follows "
                          "keyword argument unpacking")

eleza test_main():
    support.run_unittest(SyntaxTestCase)
    kutoka test agiza test_syntax
    support.run_doctest(test_syntax, verbosity=Kweli)

ikiwa __name__ == "__main__":
    test_main()
