# A test suite kila pdb; sio very comprehensive at the moment.

agiza doctest
agiza os
agiza pdb
agiza sys
agiza types
agiza unittest
agiza subprocess
agiza textwrap

kutoka contextlib agiza ExitStack
kutoka io agiza StringIO
kutoka test agiza support
# This little helper kundi ni essential kila testing pdb under doctest.
kutoka test.test_doctest agiza _FakeInput
kutoka unittest.mock agiza patch


kundi PdbTestInput(object):
    """Context manager that makes testing Pdb kwenye doctests easier."""

    eleza __init__(self, input):
        self.input = input

    eleza __enter__(self):
        self.real_stdin = sys.stdin
        sys.stdin = _FakeInput(self.input)
        self.orig_trace = sys.gettrace() ikiwa hasattr(sys, 'gettrace') isipokua Tupu

    eleza __exit__(self, *exc):
        sys.stdin = self.real_stdin
        ikiwa self.orig_trace:
            sys.settrace(self.orig_trace)


eleza test_pdb_displayhook():
    """This tests the custom displayhook kila pdb.

    >>> eleza test_function(foo, bar):
    ...     agiza pdb; pdb.Pdb(nosigint=Kweli, readrc=Uongo).set_trace()
    ...     pass

    >>> ukijumuisha PdbTestInput([
    ...     'foo',
    ...     'bar',
    ...     'kila i kwenye range(5): andika(i)',
    ...     'endelea',
    ... ]):
    ...     test_function(1, Tupu)
    > <doctest test.test_pdb.test_pdb_displayhook[0]>(3)test_function()
    -> pass
    (Pdb) foo
    1
    (Pdb) bar
    (Pdb) kila i kwenye range(5): andika(i)
    0
    1
    2
    3
    4
    (Pdb) endelea
    """


eleza test_pdb_basic_commands():
    """Test the basic commands of pdb.

    >>> eleza test_function_2(foo, bar='default'):
    ...     andika(foo)
    ...     kila i kwenye range(5):
    ...         andika(i)
    ...     andika(bar)
    ...     kila i kwenye range(10):
    ...         never_executed
    ...     andika('after for')
    ...     andika('...')
    ...     rudisha foo.upper()

    >>> eleza test_function3(arg=Tupu, *, kwonly=Tupu):
    ...     pass

    >>> eleza test_function4(a, b, c, /):
    ...     pass

    >>> eleza test_function():
    ...     agiza pdb; pdb.Pdb(nosigint=Kweli, readrc=Uongo).set_trace()
    ...     ret = test_function_2('baz')
    ...     test_function3(kwonly=Kweli)
    ...     test_function4(1, 2, 3)
    ...     andika(ret)

    >>> ukijumuisha PdbTestInput([  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    ...     'step',       # entering the function call
    ...     'args',       # display function args
    ...     'list',       # list function source
    ...     'bt',         # display backtrace
    ...     'up',         # step up to test_function()
    ...     'down',       # step down to test_function_2() again
    ...     'next',       # stepping to andika(foo)
    ...     'next',       # stepping to the kila loop
    ...     'step',       # stepping into the kila loop
    ...     'until',      # continuing until out of the kila loop
    ...     'next',       # executing the andika(bar)
    ...     'jump 8',     # jump over second kila loop
    ...     'return',     # rudisha out of function
    ...     'retval',     # display rudisha value
    ...     'next',       # step to test_function3()
    ...     'step',       # stepping into test_function3()
    ...     'args',       # display function args
    ...     'return',     # rudisha out of function
    ...     'next',       # step to test_function4()
    ...     'step',       # stepping to test_function4()
    ...     'args',       # display function args
    ...     'endelea',
    ... ]):
    ...    test_function()
    > <doctest test.test_pdb.test_pdb_basic_commands[3]>(3)test_function()
    -> ret = test_function_2('baz')
    (Pdb) step
    --Call--
    > <doctest test.test_pdb.test_pdb_basic_commands[0]>(1)test_function_2()
    -> eleza test_function_2(foo, bar='default'):
    (Pdb) args
    foo = 'baz'
    bar = 'default'
    (Pdb) list
      1  ->     eleza test_function_2(foo, bar='default'):
      2             andika(foo)
      3             kila i kwenye range(5):
      4                 andika(i)
      5             andika(bar)
      6             kila i kwenye range(10):
      7                 never_executed
      8             andika('after for')
      9             andika('...')
     10             rudisha foo.upper()
    [EOF]
    (Pdb) bt
    ...
      <doctest test.test_pdb.test_pdb_basic_commands[4]>(25)<module>()
    -> test_function()
      <doctest test.test_pdb.test_pdb_basic_commands[3]>(3)test_function()
    -> ret = test_function_2('baz')
    > <doctest test.test_pdb.test_pdb_basic_commands[0]>(1)test_function_2()
    -> eleza test_function_2(foo, bar='default'):
    (Pdb) up
    > <doctest test.test_pdb.test_pdb_basic_commands[3]>(3)test_function()
    -> ret = test_function_2('baz')
    (Pdb) down
    > <doctest test.test_pdb.test_pdb_basic_commands[0]>(1)test_function_2()
    -> eleza test_function_2(foo, bar='default'):
    (Pdb) next
    > <doctest test.test_pdb.test_pdb_basic_commands[0]>(2)test_function_2()
    -> andika(foo)
    (Pdb) next
    baz
    > <doctest test.test_pdb.test_pdb_basic_commands[0]>(3)test_function_2()
    -> kila i kwenye range(5):
    (Pdb) step
    > <doctest test.test_pdb.test_pdb_basic_commands[0]>(4)test_function_2()
    -> andika(i)
    (Pdb) until
    0
    1
    2
    3
    4
    > <doctest test.test_pdb.test_pdb_basic_commands[0]>(5)test_function_2()
    -> andika(bar)
    (Pdb) next
    default
    > <doctest test.test_pdb.test_pdb_basic_commands[0]>(6)test_function_2()
    -> kila i kwenye range(10):
    (Pdb) jump 8
    > <doctest test.test_pdb.test_pdb_basic_commands[0]>(8)test_function_2()
    -> andika('after for')
    (Pdb) return
    after for
    ...
    --Return--
    > <doctest test.test_pdb.test_pdb_basic_commands[0]>(10)test_function_2()->'BAZ'
    -> rudisha foo.upper()
    (Pdb) retval
    'BAZ'
    (Pdb) next
    > <doctest test.test_pdb.test_pdb_basic_commands[3]>(4)test_function()
    -> test_function3(kwonly=Kweli)
    (Pdb) step
    --Call--
    > <doctest test.test_pdb.test_pdb_basic_commands[1]>(1)test_function3()
    -> eleza test_function3(arg=Tupu, *, kwonly=Tupu):
    (Pdb) args
    arg = Tupu
    kwonly = Kweli
    (Pdb) return
    --Return--
    > <doctest test.test_pdb.test_pdb_basic_commands[1]>(2)test_function3()->Tupu
    -> pass
    (Pdb) next
    > <doctest test.test_pdb.test_pdb_basic_commands[3]>(5)test_function()
    -> test_function4(1, 2, 3)
    (Pdb) step
    --Call--
    > <doctest test.test_pdb.test_pdb_basic_commands[2]>(1)test_function4()
    -> eleza test_function4(a, b, c, /):
    (Pdb) args
    a = 1
    b = 2
    c = 3
    (Pdb) endelea
    BAZ
    """


eleza test_pdb_komapoint_commands():
    """Test basic commands related to komapoints.

    >>> eleza test_function():
    ...     agiza pdb; pdb.Pdb(nosigint=Kweli, readrc=Uongo).set_trace()
    ...     andika(1)
    ...     andika(2)
    ...     andika(3)
    ...     andika(4)

    First, need to clear bdb state that might be left over kutoka previous tests.
    Otherwise, the new komapoints might get assigned different numbers.

    >>> kutoka bdb agiza Breakpoint
    >>> Breakpoint.next = 1
    >>> Breakpoint.bplist = {}
    >>> Breakpoint.bpbynumber = [Tupu]

    Now test the komapoint commands.  NORMALIZE_WHITESPACE ni needed because
    the komapoint list outputs a tab kila the "stop only" na "ignore next"
    lines, which we don't want to put kwenye here.

    >>> ukijumuisha PdbTestInput([  # doctest: +NORMALIZE_WHITESPACE
    ...     'koma 3',
    ...     'disable 1',
    ...     'ignore 1 10',
    ...     'condition 1 1 < 2',
    ...     'koma 4',
    ...     'koma 4',
    ...     'koma',
    ...     'clear 3',
    ...     'koma',
    ...     'condition 1',
    ...     'enable 1',
    ...     'clear 1',
    ...     'commands 2',
    ...     'p "42"',
    ...     'andika("42", 7*6)',     # Issue 18764 (not about komapoints)
    ...     'end',
    ...     'endelea',  # will stop at komapoint 2 (line 4)
    ...     'clear',     # clear all!
    ...     'y',
    ...     'tkoma 5',
    ...     'endelea',  # will stop at temporary komapoint
    ...     'koma',     # make sure komapoint ni gone
    ...     'endelea',
    ... ]):
    ...    test_function()
    > <doctest test.test_pdb.test_pdb_komapoint_commands[0]>(3)test_function()
    -> andika(1)
    (Pdb) koma 3
    Breakpoint 1 at <doctest test.test_pdb.test_pdb_komapoint_commands[0]>:3
    (Pdb) disable 1
    Disabled komapoint 1 at <doctest test.test_pdb.test_pdb_komapoint_commands[0]>:3
    (Pdb) ignore 1 10
    Will ignore next 10 crossings of komapoint 1.
    (Pdb) condition 1 1 < 2
    New condition set kila komapoint 1.
    (Pdb) koma 4
    Breakpoint 2 at <doctest test.test_pdb.test_pdb_komapoint_commands[0]>:4
    (Pdb) koma 4
    Breakpoint 3 at <doctest test.test_pdb.test_pdb_komapoint_commands[0]>:4
    (Pdb) koma
    Num Type         Disp Enb   Where
    1   komapoint   keep no    at <doctest test.test_pdb.test_pdb_komapoint_commands[0]>:3
            stop only ikiwa 1 < 2
            ignore next 10 hits
    2   komapoint   keep yes   at <doctest test.test_pdb.test_pdb_komapoint_commands[0]>:4
    3   komapoint   keep yes   at <doctest test.test_pdb.test_pdb_komapoint_commands[0]>:4
    (Pdb) clear 3
    Deleted komapoint 3 at <doctest test.test_pdb.test_pdb_komapoint_commands[0]>:4
    (Pdb) koma
    Num Type         Disp Enb   Where
    1   komapoint   keep no    at <doctest test.test_pdb.test_pdb_komapoint_commands[0]>:3
            stop only ikiwa 1 < 2
            ignore next 10 hits
    2   komapoint   keep yes   at <doctest test.test_pdb.test_pdb_komapoint_commands[0]>:4
    (Pdb) condition 1
    Breakpoint 1 ni now unconditional.
    (Pdb) enable 1
    Enabled komapoint 1 at <doctest test.test_pdb.test_pdb_komapoint_commands[0]>:3
    (Pdb) clear 1
    Deleted komapoint 1 at <doctest test.test_pdb.test_pdb_komapoint_commands[0]>:3
    (Pdb) commands 2
    (com) p "42"
    (com) andika("42", 7*6)
    (com) end
    (Pdb) endelea
    1
    '42'
    42 42
    > <doctest test.test_pdb.test_pdb_komapoint_commands[0]>(4)test_function()
    -> andika(2)
    (Pdb) clear
    Clear all komas? y
    Deleted komapoint 2 at <doctest test.test_pdb.test_pdb_komapoint_commands[0]>:4
    (Pdb) tkoma 5
    Breakpoint 4 at <doctest test.test_pdb.test_pdb_komapoint_commands[0]>:5
    (Pdb) endelea
    2
    Deleted komapoint 4 at <doctest test.test_pdb.test_pdb_komapoint_commands[0]>:5
    > <doctest test.test_pdb.test_pdb_komapoint_commands[0]>(5)test_function()
    -> andika(3)
    (Pdb) koma
    (Pdb) endelea
    3
    4
    """


eleza do_nothing():
    pass

eleza do_something():
    andika(42)

eleza test_list_commands():
    """Test the list na source commands of pdb.

    >>> eleza test_function_2(foo):
    ...     agiza test.test_pdb
    ...     test.test_pdb.do_nothing()
    ...     'some...'
    ...     'more...'
    ...     'code...'
    ...     'to...'
    ...     'make...'
    ...     'a...'
    ...     'long...'
    ...     'listing...'
    ...     'useful...'
    ...     '...'
    ...     '...'
    ...     rudisha foo

    >>> eleza test_function():
    ...     agiza pdb; pdb.Pdb(nosigint=Kweli, readrc=Uongo).set_trace()
    ...     ret = test_function_2('baz')

    >>> ukijumuisha PdbTestInput([  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    ...     'list',      # list first function
    ...     'step',      # step into second function
    ...     'list',      # list second function
    ...     'list',      # endelea listing to EOF
    ...     'list 1,3',  # list specific lines
    ...     'list x',    # invalid argument
    ...     'next',      # step to import
    ...     'next',      # step over import
    ...     'step',      # step into do_nothing
    ...     'longlist',  # list all lines
    ...     'source do_something',  # list all lines of function
    ...     'source fooxxx',        # something that doesn't exit
    ...     'endelea',
    ... ]):
    ...    test_function()
    > <doctest test.test_pdb.test_list_commands[1]>(3)test_function()
    -> ret = test_function_2('baz')
    (Pdb) list
      1         eleza test_function():
      2             agiza pdb; pdb.Pdb(nosigint=Kweli, readrc=Uongo).set_trace()
      3  ->         ret = test_function_2('baz')
    [EOF]
    (Pdb) step
    --Call--
    > <doctest test.test_pdb.test_list_commands[0]>(1)test_function_2()
    -> eleza test_function_2(foo):
    (Pdb) list
      1  ->     eleza test_function_2(foo):
      2             agiza test.test_pdb
      3             test.test_pdb.do_nothing()
      4             'some...'
      5             'more...'
      6             'code...'
      7             'to...'
      8             'make...'
      9             'a...'
     10             'long...'
     11             'listing...'
    (Pdb) list
     12             'useful...'
     13             '...'
     14             '...'
     15             rudisha foo
    [EOF]
    (Pdb) list 1,3
      1  ->     eleza test_function_2(foo):
      2             agiza test.test_pdb
      3             test.test_pdb.do_nothing()
    (Pdb) list x
    *** ...
    (Pdb) next
    > <doctest test.test_pdb.test_list_commands[0]>(2)test_function_2()
    -> agiza test.test_pdb
    (Pdb) next
    > <doctest test.test_pdb.test_list_commands[0]>(3)test_function_2()
    -> test.test_pdb.do_nothing()
    (Pdb) step
    --Call--
    > ...test_pdb.py(...)do_nothing()
    -> eleza do_nothing():
    (Pdb) longlist
    ...  ->     eleza do_nothing():
    ...             pass
    (Pdb) source do_something
    ...         eleza do_something():
    ...             andika(42)
    (Pdb) source fooxxx
    *** ...
    (Pdb) endelea
    """


eleza test_post_mortem():
    """Test post mortem traceback debugging.

    >>> eleza test_function_2():
    ...     jaribu:
    ...         1/0
    ...     mwishowe:
    ...         andika('Exception!')

    >>> eleza test_function():
    ...     agiza pdb; pdb.Pdb(nosigint=Kweli, readrc=Uongo).set_trace()
    ...     test_function_2()
    ...     andika('Not reached.')

    >>> ukijumuisha PdbTestInput([  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    ...     'next',      # step over exception-raising call
    ...     'bt',        # get a backtrace
    ...     'list',      # list code of test_function()
    ...     'down',      # step into test_function_2()
    ...     'list',      # list code of test_function_2()
    ...     'endelea',
    ... ]):
    ...    jaribu:
    ...        test_function()
    ...    except ZeroDivisionError:
    ...        andika('Correctly reraised.')
    > <doctest test.test_pdb.test_post_mortem[1]>(3)test_function()
    -> test_function_2()
    (Pdb) next
    Exception!
    ZeroDivisionError: division by zero
    > <doctest test.test_pdb.test_post_mortem[1]>(3)test_function()
    -> test_function_2()
    (Pdb) bt
    ...
      <doctest test.test_pdb.test_post_mortem[2]>(10)<module>()
    -> test_function()
    > <doctest test.test_pdb.test_post_mortem[1]>(3)test_function()
    -> test_function_2()
      <doctest test.test_pdb.test_post_mortem[0]>(3)test_function_2()
    -> 1/0
    (Pdb) list
      1         eleza test_function():
      2             agiza pdb; pdb.Pdb(nosigint=Kweli, readrc=Uongo).set_trace()
      3  ->         test_function_2()
      4             andika('Not reached.')
    [EOF]
    (Pdb) down
    > <doctest test.test_pdb.test_post_mortem[0]>(3)test_function_2()
    -> 1/0
    (Pdb) list
      1         eleza test_function_2():
      2             jaribu:
      3  >>             1/0
      4             mwishowe:
      5  ->             andika('Exception!')
    [EOF]
    (Pdb) endelea
    Correctly reraised.
    """


eleza test_pdb_skip_modules():
    """This illustrates the simple case of module skipping.

    >>> eleza skip_module():
    ...     agiza string
    ...     agiza pdb; pdb.Pdb(skip=['stri*'], nosigint=Kweli, readrc=Uongo).set_trace()
    ...     string.capwords('FOO')

    >>> ukijumuisha PdbTestInput([
    ...     'step',
    ...     'endelea',
    ... ]):
    ...     skip_module()
    > <doctest test.test_pdb.test_pdb_skip_modules[0]>(4)skip_module()
    -> string.capwords('FOO')
    (Pdb) step
    --Return--
    > <doctest test.test_pdb.test_pdb_skip_modules[0]>(4)skip_module()->Tupu
    -> string.capwords('FOO')
    (Pdb) endelea
    """


# Module kila testing skipping of module that makes a callback
mod = types.ModuleType('module_to_skip')
exec('eleza foo_pony(callback): x = 1; callback(); rudisha Tupu', mod.__dict__)


eleza test_pdb_skip_modules_with_callback():
    """This illustrates skipping of modules that call into other code.

    >>> eleza skip_module():
    ...     eleza callback():
    ...         rudisha Tupu
    ...     agiza pdb; pdb.Pdb(skip=['module_to_skip*'], nosigint=Kweli, readrc=Uongo).set_trace()
    ...     mod.foo_pony(callback)

    >>> ukijumuisha PdbTestInput([
    ...     'step',
    ...     'step',
    ...     'step',
    ...     'step',
    ...     'step',
    ...     'endelea',
    ... ]):
    ...     skip_module()
    ...     pass  # provides something to "step" to
    > <doctest test.test_pdb.test_pdb_skip_modules_with_callback[0]>(5)skip_module()
    -> mod.foo_pony(callback)
    (Pdb) step
    --Call--
    > <doctest test.test_pdb.test_pdb_skip_modules_with_callback[0]>(2)callback()
    -> eleza callback():
    (Pdb) step
    > <doctest test.test_pdb.test_pdb_skip_modules_with_callback[0]>(3)callback()
    -> rudisha Tupu
    (Pdb) step
    --Return--
    > <doctest test.test_pdb.test_pdb_skip_modules_with_callback[0]>(3)callback()->Tupu
    -> rudisha Tupu
    (Pdb) step
    --Return--
    > <doctest test.test_pdb.test_pdb_skip_modules_with_callback[0]>(5)skip_module()->Tupu
    -> mod.foo_pony(callback)
    (Pdb) step
    > <doctest test.test_pdb.test_pdb_skip_modules_with_callback[1]>(10)<module>()
    -> pass  # provides something to "step" to
    (Pdb) endelea
    """


eleza test_pdb_endelea_in_bottomframe():
    """Test that "endelea" na "next" work properly kwenye bottom frame (issue #5294).

    >>> eleza test_function():
    ...     agiza pdb, sys; inst = pdb.Pdb(nosigint=Kweli, readrc=Uongo)
    ...     inst.set_trace()
    ...     inst.botframe = sys._getframe()  # hackery to get the right botframe
    ...     andika(1)
    ...     andika(2)
    ...     andika(3)
    ...     andika(4)

    >>> ukijumuisha PdbTestInput([  # doctest: +ELLIPSIS
    ...     'next',
    ...     'koma 7',
    ...     'endelea',
    ...     'next',
    ...     'endelea',
    ...     'endelea',
    ... ]):
    ...    test_function()
    > <doctest test.test_pdb.test_pdb_endelea_in_bottomframe[0]>(4)test_function()
    -> inst.botframe = sys._getframe()  # hackery to get the right botframe
    (Pdb) next
    > <doctest test.test_pdb.test_pdb_endelea_in_bottomframe[0]>(5)test_function()
    -> andika(1)
    (Pdb) koma 7
    Breakpoint ... at <doctest test.test_pdb.test_pdb_endelea_in_bottomframe[0]>:7
    (Pdb) endelea
    1
    2
    > <doctest test.test_pdb.test_pdb_endelea_in_bottomframe[0]>(7)test_function()
    -> andika(3)
    (Pdb) next
    3
    > <doctest test.test_pdb.test_pdb_endelea_in_bottomframe[0]>(8)test_function()
    -> andika(4)
    (Pdb) endelea
    4
    """


eleza pdb_invoke(method, arg):
    """Run pdb.method(arg)."""
    getattr(pdb.Pdb(nosigint=Kweli, readrc=Uongo), method)(arg)


eleza test_pdb_run_with_incorrect_argument():
    """Testing run na runeval ukijumuisha incorrect first argument.

    >>> pti = PdbTestInput(['endelea',])
    >>> ukijumuisha pti:
    ...     pdb_invoke('run', lambda x: x)
    Traceback (most recent call last):
    TypeError: exec() arg 1 must be a string, bytes ama code object

    >>> ukijumuisha pti:
    ...     pdb_invoke('runeval', lambda x: x)
    Traceback (most recent call last):
    TypeError: eval() arg 1 must be a string, bytes ama code object
    """


eleza test_pdb_run_with_code_object():
    """Testing run na runeval ukijumuisha code object as a first argument.

    >>> ukijumuisha PdbTestInput(['step','x', 'endelea']):  # doctest: +ELLIPSIS
    ...     pdb_invoke('run', compile('x=1', '<string>', 'exec'))
    > <string>(1)<module>()...
    (Pdb) step
    --Return--
    > <string>(1)<module>()->Tupu
    (Pdb) x
    1
    (Pdb) endelea

    >>> ukijumuisha PdbTestInput(['x', 'endelea']):
    ...     x=0
    ...     pdb_invoke('runeval', compile('x+1', '<string>', 'eval'))
    > <string>(1)<module>()->Tupu
    (Pdb) x
    1
    (Pdb) endelea
    """

eleza test_next_until_return_at_return_event():
    """Test that pdb stops after a next/until/rudisha issued at a rudisha debug event.

    >>> eleza test_function_2():
    ...     x = 1
    ...     x = 2

    >>> eleza test_function():
    ...     agiza pdb; pdb.Pdb(nosigint=Kweli, readrc=Uongo).set_trace()
    ...     test_function_2()
    ...     test_function_2()
    ...     test_function_2()
    ...     end = 1

    >>> kutoka bdb agiza Breakpoint
    >>> Breakpoint.next = 1
    >>> ukijumuisha PdbTestInput(['koma test_function_2',
    ...                    'endelea',
    ...                    'return',
    ...                    'next',
    ...                    'endelea',
    ...                    'return',
    ...                    'until',
    ...                    'endelea',
    ...                    'return',
    ...                    'return',
    ...                    'endelea']):
    ...     test_function()
    > <doctest test.test_pdb.test_next_until_return_at_return_event[1]>(3)test_function()
    -> test_function_2()
    (Pdb) koma test_function_2
    Breakpoint 1 at <doctest test.test_pdb.test_next_until_return_at_return_event[0]>:1
    (Pdb) endelea
    > <doctest test.test_pdb.test_next_until_return_at_return_event[0]>(2)test_function_2()
    -> x = 1
    (Pdb) return
    --Return--
    > <doctest test.test_pdb.test_next_until_return_at_return_event[0]>(3)test_function_2()->Tupu
    -> x = 2
    (Pdb) next
    > <doctest test.test_pdb.test_next_until_return_at_return_event[1]>(4)test_function()
    -> test_function_2()
    (Pdb) endelea
    > <doctest test.test_pdb.test_next_until_return_at_return_event[0]>(2)test_function_2()
    -> x = 1
    (Pdb) return
    --Return--
    > <doctest test.test_pdb.test_next_until_return_at_return_event[0]>(3)test_function_2()->Tupu
    -> x = 2
    (Pdb) until
    > <doctest test.test_pdb.test_next_until_return_at_return_event[1]>(5)test_function()
    -> test_function_2()
    (Pdb) endelea
    > <doctest test.test_pdb.test_next_until_return_at_return_event[0]>(2)test_function_2()
    -> x = 1
    (Pdb) return
    --Return--
    > <doctest test.test_pdb.test_next_until_return_at_return_event[0]>(3)test_function_2()->Tupu
    -> x = 2
    (Pdb) return
    > <doctest test.test_pdb.test_next_until_return_at_return_event[1]>(6)test_function()
    -> end = 1
    (Pdb) endelea
    """

eleza test_pdb_next_command_for_generator():
    """Testing skip unwindng stack on tuma kila generators kila "next" command

    >>> eleza test_gen():
    ...     tuma 0
    ...     rudisha 1
    ...     tuma 2

    >>> eleza test_function():
    ...     agiza pdb; pdb.Pdb(nosigint=Kweli, readrc=Uongo).set_trace()
    ...     it = test_gen()
    ...     jaribu:
    ...         ikiwa next(it) != 0:
    ...              ashiria AssertionError
    ...         next(it)
    ...     except StopIteration as ex:
    ...         ikiwa ex.value != 1:
    ...              ashiria AssertionError
    ...     andika("finished")

    >>> ukijumuisha PdbTestInput(['step',
    ...                    'step',
    ...                    'step',
    ...                    'next',
    ...                    'next',
    ...                    'step',
    ...                    'step',
    ...                    'endelea']):
    ...     test_function()
    > <doctest test.test_pdb.test_pdb_next_command_for_generator[1]>(3)test_function()
    -> it = test_gen()
    (Pdb) step
    > <doctest test.test_pdb.test_pdb_next_command_for_generator[1]>(4)test_function()
    -> jaribu:
    (Pdb) step
    > <doctest test.test_pdb.test_pdb_next_command_for_generator[1]>(5)test_function()
    -> ikiwa next(it) != 0:
    (Pdb) step
    --Call--
    > <doctest test.test_pdb.test_pdb_next_command_for_generator[0]>(1)test_gen()
    -> eleza test_gen():
    (Pdb) next
    > <doctest test.test_pdb.test_pdb_next_command_for_generator[0]>(2)test_gen()
    -> tuma 0
    (Pdb) next
    > <doctest test.test_pdb.test_pdb_next_command_for_generator[0]>(3)test_gen()
    -> rudisha 1
    (Pdb) step
    --Return--
    > <doctest test.test_pdb.test_pdb_next_command_for_generator[0]>(3)test_gen()->1
    -> rudisha 1
    (Pdb) step
    StopIteration: 1
    > <doctest test.test_pdb.test_pdb_next_command_for_generator[1]>(7)test_function()
    -> next(it)
    (Pdb) endelea
    finished
    """

eleza test_pdb_next_command_for_coroutine():
    """Testing skip unwindng stack on tuma kila coroutines kila "next" command

    >>> agiza asyncio

    >>> async eleza test_coro():
    ...     await asyncio.sleep(0)
    ...     await asyncio.sleep(0)
    ...     await asyncio.sleep(0)

    >>> async eleza test_main():
    ...     agiza pdb; pdb.Pdb(nosigint=Kweli, readrc=Uongo).set_trace()
    ...     await test_coro()

    >>> eleza test_function():
    ...     loop = asyncio.new_event_loop()
    ...     loop.run_until_complete(test_main())
    ...     loop.close()
    ...     asyncio.set_event_loop_policy(Tupu)
    ...     andika("finished")

    >>> ukijumuisha PdbTestInput(['step',
    ...                    'step',
    ...                    'next',
    ...                    'next',
    ...                    'next',
    ...                    'step',
    ...                    'endelea']):
    ...     test_function()
    > <doctest test.test_pdb.test_pdb_next_command_for_coroutine[2]>(3)test_main()
    -> await test_coro()
    (Pdb) step
    --Call--
    > <doctest test.test_pdb.test_pdb_next_command_for_coroutine[1]>(1)test_coro()
    -> async eleza test_coro():
    (Pdb) step
    > <doctest test.test_pdb.test_pdb_next_command_for_coroutine[1]>(2)test_coro()
    -> await asyncio.sleep(0)
    (Pdb) next
    > <doctest test.test_pdb.test_pdb_next_command_for_coroutine[1]>(3)test_coro()
    -> await asyncio.sleep(0)
    (Pdb) next
    > <doctest test.test_pdb.test_pdb_next_command_for_coroutine[1]>(4)test_coro()
    -> await asyncio.sleep(0)
    (Pdb) next
    Internal StopIteration
    > <doctest test.test_pdb.test_pdb_next_command_for_coroutine[2]>(3)test_main()
    -> await test_coro()
    (Pdb) step
    --Return--
    > <doctest test.test_pdb.test_pdb_next_command_for_coroutine[2]>(3)test_main()->Tupu
    -> await test_coro()
    (Pdb) endelea
    finished
    """

eleza test_pdb_next_command_for_asyncgen():
    """Testing skip unwindng stack on tuma kila coroutines kila "next" command

    >>> agiza asyncio

    >>> async eleza agen():
    ...     tuma 1
    ...     await asyncio.sleep(0)
    ...     tuma 2

    >>> async eleza test_coro():
    ...     async kila x kwenye agen():
    ...         andika(x)

    >>> async eleza test_main():
    ...     agiza pdb; pdb.Pdb(nosigint=Kweli, readrc=Uongo).set_trace()
    ...     await test_coro()

    >>> eleza test_function():
    ...     loop = asyncio.new_event_loop()
    ...     loop.run_until_complete(test_main())
    ...     loop.close()
    ...     asyncio.set_event_loop_policy(Tupu)
    ...     andika("finished")

    >>> ukijumuisha PdbTestInput(['step',
    ...                    'step',
    ...                    'next',
    ...                    'next',
    ...                    'step',
    ...                    'next',
    ...                    'endelea']):
    ...     test_function()
    > <doctest test.test_pdb.test_pdb_next_command_for_asyncgen[3]>(3)test_main()
    -> await test_coro()
    (Pdb) step
    --Call--
    > <doctest test.test_pdb.test_pdb_next_command_for_asyncgen[2]>(1)test_coro()
    -> async eleza test_coro():
    (Pdb) step
    > <doctest test.test_pdb.test_pdb_next_command_for_asyncgen[2]>(2)test_coro()
    -> async kila x kwenye agen():
    (Pdb) next
    > <doctest test.test_pdb.test_pdb_next_command_for_asyncgen[2]>(3)test_coro()
    -> andika(x)
    (Pdb) next
    1
    > <doctest test.test_pdb.test_pdb_next_command_for_asyncgen[2]>(2)test_coro()
    -> async kila x kwenye agen():
    (Pdb) step
    --Call--
    > <doctest test.test_pdb.test_pdb_next_command_for_asyncgen[1]>(2)agen()
    -> tuma 1
    (Pdb) next
    > <doctest test.test_pdb.test_pdb_next_command_for_asyncgen[1]>(3)agen()
    -> await asyncio.sleep(0)
    (Pdb) endelea
    2
    finished
    """

eleza test_pdb_return_command_for_generator():
    """Testing no unwindng stack on tuma kila generators
       kila "return" command

    >>> eleza test_gen():
    ...     tuma 0
    ...     rudisha 1
    ...     tuma 2

    >>> eleza test_function():
    ...     agiza pdb; pdb.Pdb(nosigint=Kweli, readrc=Uongo).set_trace()
    ...     it = test_gen()
    ...     jaribu:
    ...         ikiwa next(it) != 0:
    ...              ashiria AssertionError
    ...         next(it)
    ...     except StopIteration as ex:
    ...         ikiwa ex.value != 1:
    ...              ashiria AssertionError
    ...     andika("finished")

    >>> ukijumuisha PdbTestInput(['step',
    ...                    'step',
    ...                    'step',
    ...                    'return',
    ...                    'step',
    ...                    'step',
    ...                    'endelea']):
    ...     test_function()
    > <doctest test.test_pdb.test_pdb_return_command_for_generator[1]>(3)test_function()
    -> it = test_gen()
    (Pdb) step
    > <doctest test.test_pdb.test_pdb_return_command_for_generator[1]>(4)test_function()
    -> jaribu:
    (Pdb) step
    > <doctest test.test_pdb.test_pdb_return_command_for_generator[1]>(5)test_function()
    -> ikiwa next(it) != 0:
    (Pdb) step
    --Call--
    > <doctest test.test_pdb.test_pdb_return_command_for_generator[0]>(1)test_gen()
    -> eleza test_gen():
    (Pdb) return
    StopIteration: 1
    > <doctest test.test_pdb.test_pdb_return_command_for_generator[1]>(7)test_function()
    -> next(it)
    (Pdb) step
    > <doctest test.test_pdb.test_pdb_return_command_for_generator[1]>(8)test_function()
    -> except StopIteration as ex:
    (Pdb) step
    > <doctest test.test_pdb.test_pdb_return_command_for_generator[1]>(9)test_function()
    -> ikiwa ex.value != 1:
    (Pdb) endelea
    finished
    """

eleza test_pdb_return_command_for_coroutine():
    """Testing no unwindng stack on tuma kila coroutines kila "return" command

    >>> agiza asyncio

    >>> async eleza test_coro():
    ...     await asyncio.sleep(0)
    ...     await asyncio.sleep(0)
    ...     await asyncio.sleep(0)

    >>> async eleza test_main():
    ...     agiza pdb; pdb.Pdb(nosigint=Kweli, readrc=Uongo).set_trace()
    ...     await test_coro()

    >>> eleza test_function():
    ...     loop = asyncio.new_event_loop()
    ...     loop.run_until_complete(test_main())
    ...     loop.close()
    ...     asyncio.set_event_loop_policy(Tupu)
    ...     andika("finished")

    >>> ukijumuisha PdbTestInput(['step',
    ...                    'step',
    ...                    'next',
    ...                    'endelea']):
    ...     test_function()
    > <doctest test.test_pdb.test_pdb_return_command_for_coroutine[2]>(3)test_main()
    -> await test_coro()
    (Pdb) step
    --Call--
    > <doctest test.test_pdb.test_pdb_return_command_for_coroutine[1]>(1)test_coro()
    -> async eleza test_coro():
    (Pdb) step
    > <doctest test.test_pdb.test_pdb_return_command_for_coroutine[1]>(2)test_coro()
    -> await asyncio.sleep(0)
    (Pdb) next
    > <doctest test.test_pdb.test_pdb_return_command_for_coroutine[1]>(3)test_coro()
    -> await asyncio.sleep(0)
    (Pdb) endelea
    finished
    """

eleza test_pdb_until_command_for_generator():
    """Testing no unwindng stack on tuma kila generators
       kila "until" command ikiwa target komapoing ni sio reached

    >>> eleza test_gen():
    ...     tuma 0
    ...     tuma 1
    ...     tuma 2

    >>> eleza test_function():
    ...     agiza pdb; pdb.Pdb(nosigint=Kweli, readrc=Uongo).set_trace()
    ...     kila i kwenye test_gen():
    ...         andika(i)
    ...     andika("finished")

    >>> ukijumuisha PdbTestInput(['step',
    ...                    'until 4',
    ...                    'step',
    ...                    'step',
    ...                    'endelea']):
    ...     test_function()
    > <doctest test.test_pdb.test_pdb_until_command_for_generator[1]>(3)test_function()
    -> kila i kwenye test_gen():
    (Pdb) step
    --Call--
    > <doctest test.test_pdb.test_pdb_until_command_for_generator[0]>(1)test_gen()
    -> eleza test_gen():
    (Pdb) until 4
    0
    1
    > <doctest test.test_pdb.test_pdb_until_command_for_generator[0]>(4)test_gen()
    -> tuma 2
    (Pdb) step
    --Return--
    > <doctest test.test_pdb.test_pdb_until_command_for_generator[0]>(4)test_gen()->2
    -> tuma 2
    (Pdb) step
    > <doctest test.test_pdb.test_pdb_until_command_for_generator[1]>(4)test_function()
    -> andika(i)
    (Pdb) endelea
    2
    finished
    """

eleza test_pdb_until_command_for_coroutine():
    """Testing no unwindng stack kila coroutines
       kila "until" command ikiwa target komapoing ni sio reached

    >>> agiza asyncio

    >>> async eleza test_coro():
    ...     andika(0)
    ...     await asyncio.sleep(0)
    ...     andika(1)
    ...     await asyncio.sleep(0)
    ...     andika(2)
    ...     await asyncio.sleep(0)
    ...     andika(3)

    >>> async eleza test_main():
    ...     agiza pdb; pdb.Pdb(nosigint=Kweli, readrc=Uongo).set_trace()
    ...     await test_coro()

    >>> eleza test_function():
    ...     loop = asyncio.new_event_loop()
    ...     loop.run_until_complete(test_main())
    ...     loop.close()
    ...     asyncio.set_event_loop_policy(Tupu)
    ...     andika("finished")

    >>> ukijumuisha PdbTestInput(['step',
    ...                    'until 8',
    ...                    'endelea']):
    ...     test_function()
    > <doctest test.test_pdb.test_pdb_until_command_for_coroutine[2]>(3)test_main()
    -> await test_coro()
    (Pdb) step
    --Call--
    > <doctest test.test_pdb.test_pdb_until_command_for_coroutine[1]>(1)test_coro()
    -> async eleza test_coro():
    (Pdb) until 8
    0
    1
    2
    > <doctest test.test_pdb.test_pdb_until_command_for_coroutine[1]>(8)test_coro()
    -> andika(3)
    (Pdb) endelea
    3
    finished
    """

eleza test_pdb_next_command_in_generator_for_loop():
    """The next command on returning kutoka a generator controlled by a kila loop.

    >>> eleza test_gen():
    ...     tuma 0
    ...     rudisha 1

    >>> eleza test_function():
    ...     agiza pdb; pdb.Pdb(nosigint=Kweli, readrc=Uongo).set_trace()
    ...     kila i kwenye test_gen():
    ...         andika('value', i)
    ...     x = 123

    >>> ukijumuisha PdbTestInput(['koma test_gen',
    ...                    'endelea',
    ...                    'next',
    ...                    'next',
    ...                    'next',
    ...                    'endelea']):
    ...     test_function()
    > <doctest test.test_pdb.test_pdb_next_command_in_generator_for_loop[1]>(3)test_function()
    -> kila i kwenye test_gen():
    (Pdb) koma test_gen
    Breakpoint 6 at <doctest test.test_pdb.test_pdb_next_command_in_generator_for_loop[0]>:1
    (Pdb) endelea
    > <doctest test.test_pdb.test_pdb_next_command_in_generator_for_loop[0]>(2)test_gen()
    -> tuma 0
    (Pdb) next
    value 0
    > <doctest test.test_pdb.test_pdb_next_command_in_generator_for_loop[0]>(3)test_gen()
    -> rudisha 1
    (Pdb) next
    Internal StopIteration: 1
    > <doctest test.test_pdb.test_pdb_next_command_in_generator_for_loop[1]>(3)test_function()
    -> kila i kwenye test_gen():
    (Pdb) next
    > <doctest test.test_pdb.test_pdb_next_command_in_generator_for_loop[1]>(5)test_function()
    -> x = 123
    (Pdb) endelea
    """

eleza test_pdb_next_command_subiterator():
    """The next command kwenye a generator ukijumuisha a subiterator.

    >>> eleza test_subgenerator():
    ...     tuma 0
    ...     rudisha 1

    >>> eleza test_gen():
    ...     x = tuma kutoka test_subgenerator()
    ...     rudisha x

    >>> eleza test_function():
    ...     agiza pdb; pdb.Pdb(nosigint=Kweli, readrc=Uongo).set_trace()
    ...     kila i kwenye test_gen():
    ...         andika('value', i)
    ...     x = 123

    >>> ukijumuisha PdbTestInput(['step',
    ...                    'step',
    ...                    'next',
    ...                    'next',
    ...                    'next',
    ...                    'endelea']):
    ...     test_function()
    > <doctest test.test_pdb.test_pdb_next_command_subiterator[2]>(3)test_function()
    -> kila i kwenye test_gen():
    (Pdb) step
    --Call--
    > <doctest test.test_pdb.test_pdb_next_command_subiterator[1]>(1)test_gen()
    -> eleza test_gen():
    (Pdb) step
    > <doctest test.test_pdb.test_pdb_next_command_subiterator[1]>(2)test_gen()
    -> x = tuma kutoka test_subgenerator()
    (Pdb) next
    value 0
    > <doctest test.test_pdb.test_pdb_next_command_subiterator[1]>(3)test_gen()
    -> rudisha x
    (Pdb) next
    Internal StopIteration: 1
    > <doctest test.test_pdb.test_pdb_next_command_subiterator[2]>(3)test_function()
    -> kila i kwenye test_gen():
    (Pdb) next
    > <doctest test.test_pdb.test_pdb_next_command_subiterator[2]>(5)test_function()
    -> x = 123
    (Pdb) endelea
    """

eleza test_pdb_issue_20766():
    """Test kila reference leaks when the SIGINT handler ni set.

    >>> eleza test_function():
    ...     i = 1
    ...     wakati i <= 2:
    ...         sess = pdb.Pdb()
    ...         sess.set_trace(sys._getframe())
    ...         andika('pdb %d: %s' % (i, sess._previous_sigint_handler))
    ...         i += 1

    >>> ukijumuisha PdbTestInput(['endelea',
    ...                    'endelea']):
    ...     test_function()
    > <doctest test.test_pdb.test_pdb_issue_20766[0]>(6)test_function()
    -> andika('pdb %d: %s' % (i, sess._previous_sigint_handler))
    (Pdb) endelea
    pdb 1: <built-in function default_int_handler>
    > <doctest test.test_pdb.test_pdb_issue_20766[0]>(5)test_function()
    -> sess.set_trace(sys._getframe())
    (Pdb) endelea
    pdb 2: <built-in function default_int_handler>
    """


kundi PdbTestCase(unittest.TestCase):
    eleza tearDown(self):
        support.unlink(support.TESTFN)

    eleza _run_pdb(self, pdb_args, commands):
        self.addCleanup(support.rmtree, '__pycache__')
        cmd = [sys.executable, '-m', 'pdb'] + pdb_args
        ukijumuisha subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stderr=subprocess.STDOUT,
        ) as proc:
            stdout, stderr = proc.communicate(str.encode(commands))
        stdout = stdout na bytes.decode(stdout)
        stderr = stderr na bytes.decode(stderr)
        rudisha stdout, stderr

    eleza run_pdb_script(self, script, commands):
        """Run 'script' lines ukijumuisha pdb na the pdb 'commands'."""
        filename = 'main.py'
        ukijumuisha open(filename, 'w') as f:
            f.write(textwrap.dedent(script))
        self.addCleanup(support.unlink, filename)
        rudisha self._run_pdb([filename], commands)

    eleza run_pdb_module(self, script, commands):
        """Runs the script code as part of a module"""
        self.module_name = 't_main'
        support.rmtree(self.module_name)
        main_file = self.module_name + '/__main__.py'
        init_file = self.module_name + '/__init__.py'
        os.mkdir(self.module_name)
        ukijumuisha open(init_file, 'w') as f:
            pass
        ukijumuisha open(main_file, 'w') as f:
            f.write(textwrap.dedent(script))
        self.addCleanup(support.rmtree, self.module_name)
        rudisha self._run_pdb(['-m', self.module_name], commands)

    eleza _assert_find_function(self, file_content, func_name, expected):
        file_content = textwrap.dedent(file_content)

        ukijumuisha open(support.TESTFN, 'w') as f:
            f.write(file_content)

        expected = Tupu ikiwa sio expected isipokua (
            expected[0], support.TESTFN, expected[1])
        self.assertEqual(
            expected, pdb.find_function(func_name, support.TESTFN))

    eleza test_find_function_empty_file(self):
        self._assert_find_function('', 'foo', Tupu)

    eleza test_find_function_found(self):
        self._assert_find_function(
            """\
            eleza foo():
                pass

            eleza bar():
                pass

            eleza quux():
                pass
            """,
            'bar',
            ('bar', 4),
        )

    eleza test_issue7964(self):
        # open the file as binary so we can force \r\n newline
        ukijumuisha open(support.TESTFN, 'wb') as f:
            f.write(b'andika("testing my pdb")\r\n')
        cmd = [sys.executable, '-m', 'pdb', support.TESTFN]
        proc = subprocess.Popen(cmd,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            )
        self.addCleanup(proc.stdout.close)
        stdout, stderr = proc.communicate(b'quit\n')
        self.assertNotIn(b'SyntaxError', stdout,
                         "Got a syntax error running test script under PDB")

    eleza test_issue13183(self):
        script = """
            kutoka bar agiza bar

            eleza foo():
                bar()

            eleza nope():
                pass

            eleza foobar():
                foo()
                nope()

            foobar()
        """
        commands = """
            kutoka bar agiza bar
            koma bar
            endelea
            step
            step
            quit
        """
        bar = """
            eleza bar():
                pass
        """
        ukijumuisha open('bar.py', 'w') as f:
            f.write(textwrap.dedent(bar))
        self.addCleanup(support.unlink, 'bar.py')
        stdout, stderr = self.run_pdb_script(script, commands)
        self.assertKweli(
            any('main.py(5)foo()->Tupu' kwenye l kila l kwenye stdout.splitlines()),
            'Fail to step into the caller after a return')

    eleza test_issue13120(self):
        # Invoking "endelea" on a non-main thread triggered an exception
        # inside signal.signal.

        ukijumuisha open(support.TESTFN, 'wb') as f:
            f.write(textwrap.dedent("""
                agiza threading
                agiza pdb

                eleza start_pdb():
                    pdb.Pdb(readrc=Uongo).set_trace()
                    x = 1
                    y = 1

                t = threading.Thread(target=start_pdb)
                t.start()""").encode('ascii'))
        cmd = [sys.executable, '-u', support.TESTFN]
        proc = subprocess.Popen(cmd,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            )
        self.addCleanup(proc.stdout.close)
        stdout, stderr = proc.communicate(b'cont\n')
        self.assertNotIn('Error', stdout.decode(),
                         "Got an error running test script under PDB")

    eleza test_issue36250(self):

        ukijumuisha open(support.TESTFN, 'wb') as f:
            f.write(textwrap.dedent("""
                agiza threading
                agiza pdb

                evt = threading.Event()

                eleza start_pdb():
                    evt.wait()
                    pdb.Pdb(readrc=Uongo).set_trace()

                t = threading.Thread(target=start_pdb)
                t.start()
                pdb.Pdb(readrc=Uongo).set_trace()
                evt.set()
                t.join()""").encode('ascii'))
        cmd = [sys.executable, '-u', support.TESTFN]
        proc = subprocess.Popen(cmd,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            )
        self.addCleanup(proc.stdout.close)
        stdout, stderr = proc.communicate(b'cont\ncont\n')
        self.assertNotIn('Error', stdout.decode(),
                         "Got an error running test script under PDB")

    eleza test_issue16180(self):
        # A syntax error kwenye the debuggee.
        script = "eleza f: pass\n"
        commands = ''
        expected = "SyntaxError:"
        stdout, stderr = self.run_pdb_script(script, commands)
        self.assertIn(expected, stdout,
            '\n\nExpected:\n{}\nGot:\n{}\n'
            'Fail to handle a syntax error kwenye the debuggee.'
            .format(expected, stdout))


    eleza test_readrc_kwarg(self):
        script = textwrap.dedent("""
            agiza pdb; pdb.Pdb(readrc=Uongo).set_trace()

            andika('hello')
        """)

        save_home = os.environ.pop('HOME', Tupu)
        jaribu:
            ukijumuisha support.temp_cwd():
                ukijumuisha open('.pdbrc', 'w') as f:
                    f.write("invalid\n")

                ukijumuisha open('main.py', 'w') as f:
                    f.write(script)

                cmd = [sys.executable, 'main.py']
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                ukijumuisha proc:
                    stdout, stderr = proc.communicate(b'q\n')
                    self.assertNotIn("NameError: name 'invalid' ni sio defined",
                                  stdout.decode())

        mwishowe:
            ikiwa save_home ni sio Tupu:
                os.environ['HOME'] = save_home

    eleza test_readrc_homedir(self):
        save_home = os.environ.pop("HOME", Tupu)
        ukijumuisha support.temp_dir() as temp_dir, patch("os.path.expanduser"):
            rc_path = os.path.join(temp_dir, ".pdbrc")
            os.path.expanduser.return_value = rc_path
            jaribu:
                ukijumuisha open(rc_path, "w") as f:
                    f.write("invalid")
                self.assertEqual(pdb.Pdb().rcLines[0], "invalid")
            mwishowe:
                ikiwa save_home ni sio Tupu:
                    os.environ["HOME"] = save_home

    eleza test_header(self):
        stdout = StringIO()
        header = 'Nobody expects... blah, blah, blah'
        ukijumuisha ExitStack() as resources:
            resources.enter_context(patch('sys.stdout', stdout))
            resources.enter_context(patch.object(pdb.Pdb, 'set_trace'))
            pdb.set_trace(header=header)
        self.assertEqual(stdout.getvalue(), header + '\n')

    eleza test_run_module(self):
        script = """andika("SUCCESS")"""
        commands = """
            endelea
            quit
        """
        stdout, stderr = self.run_pdb_module(script, commands)
        self.assertKweli(any("SUCCESS" kwenye l kila l kwenye stdout.splitlines()), stdout)

    eleza test_module_is_run_as_main(self):
        script = """
            ikiwa __name__ == '__main__':
                andika("SUCCESS")
        """
        commands = """
            endelea
            quit
        """
        stdout, stderr = self.run_pdb_module(script, commands)
        self.assertKweli(any("SUCCESS" kwenye l kila l kwenye stdout.splitlines()), stdout)

    eleza test_komapoint(self):
        script = """
            ikiwa __name__ == '__main__':
                pass
                andika("SUCCESS")
                pass
        """
        commands = """
            b 3
            quit
        """
        stdout, stderr = self.run_pdb_module(script, commands)
        self.assertKweli(any("Breakpoint 1 at" kwenye l kila l kwenye stdout.splitlines()), stdout)
        self.assertKweli(all("SUCCESS" sio kwenye l kila l kwenye stdout.splitlines()), stdout)

    eleza test_run_pdb_with_pdb(self):
        commands = """
            c
            quit
        """
        stdout, stderr = self._run_pdb(["-m", "pdb"], commands)
        self.assertIn(
            pdb._usage,
            stdout.replace('\r', '')  # remove \r kila windows
        )

    eleza test_module_without_a_main(self):
        module_name = 't_main'
        support.rmtree(module_name)
        init_file = module_name + '/__init__.py'
        os.mkdir(module_name)
        ukijumuisha open(init_file, 'w') as f:
            pass
        self.addCleanup(support.rmtree, module_name)
        stdout, stderr = self._run_pdb(['-m', module_name], "")
        self.assertIn("ImportError: No module named t_main.__main__",
                      stdout.splitlines())

    eleza test_blocks_at_first_code_line(self):
        script = """
                #This ni a comment, on line 2

                andika("SUCCESS")
        """
        commands = """
            quit
        """
        stdout, stderr = self.run_pdb_module(script, commands)
        self.assertKweli(any("__main__.py(4)<module>()"
                            kwenye l kila l kwenye stdout.splitlines()), stdout)

    eleza test_relative_imports(self):
        self.module_name = 't_main'
        support.rmtree(self.module_name)
        main_file = self.module_name + '/__main__.py'
        init_file = self.module_name + '/__init__.py'
        module_file = self.module_name + '/module.py'
        self.addCleanup(support.rmtree, self.module_name)
        os.mkdir(self.module_name)
        ukijumuisha open(init_file, 'w') as f:
            f.write(textwrap.dedent("""
                top_var = "VAR kutoka top"
            """))
        ukijumuisha open(main_file, 'w') as f:
            f.write(textwrap.dedent("""
                kutoka . agiza top_var
                kutoka .module agiza var
                kutoka . agiza module
                pass # We'll stop here na print the vars
            """))
        ukijumuisha open(module_file, 'w') as f:
            f.write(textwrap.dedent("""
                var = "VAR kutoka module"
                var2 = "second var"
            """))
        commands = """
            b 5
            c
            p top_var
            p var
            p module.var2
            quit
        """
        stdout, _ = self._run_pdb(['-m', self.module_name], commands)
        self.assertKweli(any("VAR kutoka module" kwenye l kila l kwenye stdout.splitlines()), stdout)
        self.assertKweli(any("VAR kutoka top" kwenye l kila l kwenye stdout.splitlines()))
        self.assertKweli(any("second var" kwenye l kila l kwenye stdout.splitlines()))

    eleza test_relative_imports_on_plain_module(self):
        # Validates running a plain module. See bpo32691
        self.module_name = 't_main'
        support.rmtree(self.module_name)
        main_file = self.module_name + '/runme.py'
        init_file = self.module_name + '/__init__.py'
        module_file = self.module_name + '/module.py'
        self.addCleanup(support.rmtree, self.module_name)
        os.mkdir(self.module_name)
        ukijumuisha open(init_file, 'w') as f:
            f.write(textwrap.dedent("""
                top_var = "VAR kutoka top"
            """))
        ukijumuisha open(main_file, 'w') as f:
            f.write(textwrap.dedent("""
                kutoka . agiza module
                pass # We'll stop here na print the vars
            """))
        ukijumuisha open(module_file, 'w') as f:
            f.write(textwrap.dedent("""
                var = "VAR kutoka module"
            """))
        commands = """
            b 3
            c
            p module.var
            quit
        """
        stdout, _ = self._run_pdb(['-m', self.module_name + '.runme'], commands)
        self.assertKweli(any("VAR kutoka module" kwenye l kila l kwenye stdout.splitlines()), stdout)

    eleza test_errors_in_command(self):
        commands = "\n".join([
            'andika(',
            'debug andika(',
            'debug doesnotexist',
            'c',
        ])
        stdout, _ = self.run_pdb_script('', commands + '\n')

        self.assertEqual(stdout.splitlines()[1:], [
            '(Pdb) *** SyntaxError: unexpected EOF wakati parsing',

            '(Pdb) ENTERING RECURSIVE DEBUGGER',
            '*** SyntaxError: unexpected EOF wakati parsing',
            'LEAVING RECURSIVE DEBUGGER',

            '(Pdb) ENTERING RECURSIVE DEBUGGER',
            '> <string>(1)<module>()',
            "((Pdb)) *** NameError: name 'doesnotexist' ni sio defined",
            'LEAVING RECURSIVE DEBUGGER',
            '(Pdb) ',
        ])

eleza load_tests(*args):
    kutoka test agiza test_pdb
    suites = [
        unittest.makeSuite(PdbTestCase),
        doctest.DocTestSuite(test_pdb)
    ]
    rudisha unittest.TestSuite(suites)


ikiwa __name__ == '__main__':
    unittest.main()
