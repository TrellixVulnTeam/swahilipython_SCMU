# Python test set -- part 5, built-in exceptions

agiza copy
agiza os
agiza sys
agiza unittest
agiza pickle
agiza weakref
agiza errno

kutoka test.support agiza (TESTFN, captured_stderr, check_impl_detail,
                          check_warnings, cpython_only, gc_collect,
                          no_tracing, unlink, import_module, script_helper,
                          SuppressCrashReport)
kutoka test agiza support


kundi NaiveException(Exception):
    eleza __init__(self, x):
        self.x = x

kundi SlottedNaiveException(Exception):
    __slots__ = ('x',)
    eleza __init__(self, x):
        self.x = x

kundi BrokenStrException(Exception):
    eleza __str__(self):
         ashiria Exception("str() ni broken")

# XXX This ni sio really enough, each *operation* should be tested!

kundi ExceptionTests(unittest.TestCase):

    eleza raise_catch(self, exc, excname):
        jaribu:
             ashiria exc("spam")
        except exc as err:
            buf1 = str(err)
        jaribu:
             ashiria exc("spam")
        except exc as err:
            buf2 = str(err)
        self.assertEqual(buf1, buf2)
        self.assertEqual(exc.__name__, excname)

    eleza testRaising(self):
        self.raise_catch(AttributeError, "AttributeError")
        self.assertRaises(AttributeError, getattr, sys, "undefined_attribute")

        self.raise_catch(EOFError, "EOFError")
        fp = open(TESTFN, 'w')
        fp.close()
        fp = open(TESTFN, 'r')
        savestdin = sys.stdin
        jaribu:
            jaribu:
                agiza marshal
                marshal.loads(b'')
            except EOFError:
                pass
        mwishowe:
            sys.stdin = savestdin
            fp.close()
            unlink(TESTFN)

        self.raise_catch(OSError, "OSError")
        self.assertRaises(OSError, open, 'this file does sio exist', 'r')

        self.raise_catch(ImportError, "ImportError")
        self.assertRaises(ImportError, __import__, "undefined_module")

        self.raise_catch(IndexError, "IndexError")
        x = []
        self.assertRaises(IndexError, x.__getitem__, 10)

        self.raise_catch(KeyError, "KeyError")
        x = {}
        self.assertRaises(KeyError, x.__getitem__, 'key')

        self.raise_catch(KeyboardInterrupt, "KeyboardInterrupt")

        self.raise_catch(MemoryError, "MemoryError")

        self.raise_catch(NameError, "NameError")
        jaribu: x = undefined_variable
        except NameError: pass

        self.raise_catch(OverflowError, "OverflowError")
        x = 1
        kila dummy kwenye range(128):
            x += x  # this simply shouldn't blow up

        self.raise_catch(RuntimeError, "RuntimeError")
        self.raise_catch(RecursionError, "RecursionError")

        self.raise_catch(SyntaxError, "SyntaxError")
        jaribu: exec('/\n')
        except SyntaxError: pass

        self.raise_catch(IndentationError, "IndentationError")

        self.raise_catch(TabError, "TabError")
        jaribu: compile("jaribu:\n\t1/0\n    \t1/0\nmwishowe:\n pass\n",
                     '<string>', 'exec')
        except TabError: pass
        isipokua: self.fail("TabError sio raised")

        self.raise_catch(SystemError, "SystemError")

        self.raise_catch(SystemExit, "SystemExit")
        self.assertRaises(SystemExit, sys.exit, 0)

        self.raise_catch(TypeError, "TypeError")
        jaribu: [] + ()
        except TypeError: pass

        self.raise_catch(ValueError, "ValueError")
        self.assertRaises(ValueError, chr, 17<<16)

        self.raise_catch(ZeroDivisionError, "ZeroDivisionError")
        jaribu: x = 1/0
        except ZeroDivisionError: pass

        self.raise_catch(Exception, "Exception")
        jaribu: x = 1/0
        except Exception as e: pass

        self.raise_catch(StopAsyncIteration, "StopAsyncIteration")

    eleza testSyntaxErrorMessage(self):
        # make sure the right exception message ni raised kila each of
        # these code fragments

        eleza ckmsg(src, msg):
            jaribu:
                compile(src, '<fragment>', 'exec')
            except SyntaxError as e:
                ikiwa e.msg != msg:
                    self.fail("expected %s, got %s" % (msg, e.msg))
            isipokua:
                self.fail("failed to get expected SyntaxError")

        s = '''ikiwa 1:
        jaribu:
            endelea
        tatizo:
            pass'''

        ckmsg(s, "'endelea' sio properly kwenye loop")
        ckmsg("endelea\n", "'endelea' sio properly kwenye loop")

    eleza testSyntaxErrorMissingParens(self):
        eleza ckmsg(src, msg, exception=SyntaxError):
            jaribu:
                compile(src, '<fragment>', 'exec')
            except exception as e:
                ikiwa e.msg != msg:
                    self.fail("expected %s, got %s" % (msg, e.msg))
            isipokua:
                self.fail("failed to get expected SyntaxError")

        s = '''print "old style"'''
        ckmsg(s, "Missing parentheses kwenye call to 'print'. "
                 "Did you mean andika(\"old style\")?")

        s = '''print "old style",'''
        ckmsg(s, "Missing parentheses kwenye call to 'print'. "
                 "Did you mean andika(\"old style\", end=\" \")?")

        s = '''exec "old style"'''
        ckmsg(s, "Missing parentheses kwenye call to 'exec'")

        # should sio apply to subclasses, see issue #31161
        s = '''ikiwa Kweli:\nprint "No indent"'''
        ckmsg(s, "expected an indented block", IndentationError)

        s = '''ikiwa Kweli:\n        andika()\n\texec "mixed tabs na spaces"'''
        ckmsg(s, "inconsistent use of tabs na spaces kwenye indentation", TabError)

    eleza testSyntaxErrorOffset(self):
        eleza check(src, lineno, offset):
            ukijumuisha self.assertRaises(SyntaxError) as cm:
                compile(src, '<fragment>', 'exec')
            self.assertEqual(cm.exception.lineno, lineno)
            self.assertEqual(cm.exception.offset, offset)

        check('eleza fact(x):\n\trudisha x!\n', 2, 10)
        check('1 +\n', 1, 4)
        check('eleza spam():\n  andika(1)\n andika(2)', 3, 10)
        check('Python = "Python" +', 1, 20)
        check('Python = "\u1e54\xfd\u0163\u0125\xf2\xf1" +', 1, 20)
        check('x = "a', 1, 7)
        check('lambda x: x = 2', 1, 1)

        # Errors thrown by compile.c
        check('kundi foo:rudisha 1', 1, 11)
        check('eleza f():\n  endelea', 2, 3)
        check('eleza f():\n  koma', 2, 3)
        check('jaribu:\n  pass\ntatizo:\n  pass\nexcept ValueError:\n  pass', 2, 3)

        # Errors thrown by tokenizer.c
        check('(0x+1)', 1, 3)
        check('x = 0xI', 1, 6)
        check('0010 + 2', 1, 4)
        check('x = 32e-+4', 1, 8)
        check('x = 0o9', 1, 6)

        # Errors thrown by symtable.c
        check('x = [(tuma i) kila i kwenye range(3)]', 1, 5)
        check('eleza f():\n  kutoka _ agiza *', 1, 1)
        check('eleza f(x, x):\n  pass', 1, 1)
        check('eleza f(x):\n  nonlocal x', 2, 3)
        check('eleza f(x):\n  x = 1\n  global x', 3, 3)
        check('nonlocal x', 1, 1)
        check('eleza f():\n  global x\n  nonlocal x', 2, 3)

        # Errors thrown by ast.c
        check('kila 1 kwenye []: pass', 1, 5)
        check('eleza f(*):\n  pass', 1, 7)
        check('[*x kila x kwenye xs]', 1, 2)
        check('eleza f():\n  x, y: int', 2, 3)
        check('(tuma i) = 2', 1, 1)
        check('foo(x kila x kwenye range(10), 100)', 1, 5)
        check('foo(1=2)', 1, 5)

        # Errors thrown by future.c
        check('kutoka __future__ agiza doesnt_exist', 1, 1)
        check('kutoka __future__ agiza braces', 1, 1)
        check('x=1\nkutoka __future__ agiza division', 2, 1)


    @cpython_only
    eleza testSettingException(self):
        # test that setting an exception at the C level works even ikiwa the
        # exception object can't be constructed.

        kundi BadException(Exception):
            eleza __init__(self_):
                 ashiria RuntimeError("can't instantiate BadException")

        kundi InvalidException:
            pass

        eleza test_capi1():
            agiza _testcapi
            jaribu:
                _testcapi.raise_exception(BadException, 1)
            except TypeError as err:
                exc, err, tb = sys.exc_info()
                co = tb.tb_frame.f_code
                self.assertEqual(co.co_name, "test_capi1")
                self.assertKweli(co.co_filename.endswith('test_exceptions.py'))
            isipokua:
                self.fail("Expected exception")

        eleza test_capi2():
            agiza _testcapi
            jaribu:
                _testcapi.raise_exception(BadException, 0)
            except RuntimeError as err:
                exc, err, tb = sys.exc_info()
                co = tb.tb_frame.f_code
                self.assertEqual(co.co_name, "__init__")
                self.assertKweli(co.co_filename.endswith('test_exceptions.py'))
                co2 = tb.tb_frame.f_back.f_code
                self.assertEqual(co2.co_name, "test_capi2")
            isipokua:
                self.fail("Expected exception")

        eleza test_capi3():
            agiza _testcapi
            self.assertRaises(SystemError, _testcapi.raise_exception,
                              InvalidException, 1)

        ikiwa sio sys.platform.startswith('java'):
            test_capi1()
            test_capi2()
            test_capi3()

    eleza test_WindowsError(self):
        jaribu:
            WindowsError
        except NameError:
            pass
        isipokua:
            self.assertIs(WindowsError, OSError)
            self.assertEqual(str(OSError(1001)), "1001")
            self.assertEqual(str(OSError(1001, "message")),
                             "[Errno 1001] message")
            # POSIX errno (9 aka EBADF) ni untranslated
            w = OSError(9, 'foo', 'bar')
            self.assertEqual(w.errno, 9)
            self.assertEqual(w.winerror, Tupu)
            self.assertEqual(str(w), "[Errno 9] foo: 'bar'")
            # ERROR_PATH_NOT_FOUND (win error 3) becomes ENOENT (2)
            w = OSError(0, 'foo', 'bar', 3)
            self.assertEqual(w.errno, 2)
            self.assertEqual(w.winerror, 3)
            self.assertEqual(w.strerror, 'foo')
            self.assertEqual(w.filename, 'bar')
            self.assertEqual(w.filename2, Tupu)
            self.assertEqual(str(w), "[WinError 3] foo: 'bar'")
            # Unknown win error becomes EINVAL (22)
            w = OSError(0, 'foo', Tupu, 1001)
            self.assertEqual(w.errno, 22)
            self.assertEqual(w.winerror, 1001)
            self.assertEqual(w.strerror, 'foo')
            self.assertEqual(w.filename, Tupu)
            self.assertEqual(w.filename2, Tupu)
            self.assertEqual(str(w), "[WinError 1001] foo")
            # Non-numeric "errno"
            w = OSError('bar', 'foo')
            self.assertEqual(w.errno, 'bar')
            self.assertEqual(w.winerror, Tupu)
            self.assertEqual(w.strerror, 'foo')
            self.assertEqual(w.filename, Tupu)
            self.assertEqual(w.filename2, Tupu)

    @unittest.skipUnless(sys.platform == 'win32',
                         'test specific to Windows')
    eleza test_windows_message(self):
        """Should fill kwenye unknown error code kwenye Windows error message"""
        ctypes = import_module('ctypes')
        # this error code has no message, Python formats it as hexadecimal
        code = 3765269347
        ukijumuisha self.assertRaisesRegex(OSError, 'Windows Error 0x%x' % code):
            ctypes.pythonapi.PyErr_SetFromWindowsErr(code)

    eleza testAttributes(self):
        # test that exception attributes are happy

        exceptionList = [
            (BaseException, (), {'args' : ()}),
            (BaseException, (1, ), {'args' : (1,)}),
            (BaseException, ('foo',),
                {'args' : ('foo',)}),
            (BaseException, ('foo', 1),
                {'args' : ('foo', 1)}),
            (SystemExit, ('foo',),
                {'args' : ('foo',), 'code' : 'foo'}),
            (OSError, ('foo',),
                {'args' : ('foo',), 'filename' : Tupu, 'filename2' : Tupu,
                 'errno' : Tupu, 'strerror' : Tupu}),
            (OSError, ('foo', 'bar'),
                {'args' : ('foo', 'bar'),
                 'filename' : Tupu, 'filename2' : Tupu,
                 'errno' : 'foo', 'strerror' : 'bar'}),
            (OSError, ('foo', 'bar', 'baz'),
                {'args' : ('foo', 'bar'),
                 'filename' : 'baz', 'filename2' : Tupu,
                 'errno' : 'foo', 'strerror' : 'bar'}),
            (OSError, ('foo', 'bar', 'baz', Tupu, 'quux'),
                {'args' : ('foo', 'bar'), 'filename' : 'baz', 'filename2': 'quux'}),
            (OSError, ('errnoStr', 'strErrorStr', 'filenameStr'),
                {'args' : ('errnoStr', 'strErrorStr'),
                 'strerror' : 'strErrorStr', 'errno' : 'errnoStr',
                 'filename' : 'filenameStr'}),
            (OSError, (1, 'strErrorStr', 'filenameStr'),
                {'args' : (1, 'strErrorStr'), 'errno' : 1,
                 'strerror' : 'strErrorStr',
                 'filename' : 'filenameStr', 'filename2' : Tupu}),
            (SyntaxError, (), {'msg' : Tupu, 'text' : Tupu,
                'filename' : Tupu, 'lineno' : Tupu, 'offset' : Tupu,
                'print_file_and_line' : Tupu}),
            (SyntaxError, ('msgStr',),
                {'args' : ('msgStr',), 'text' : Tupu,
                 'print_file_and_line' : Tupu, 'msg' : 'msgStr',
                 'filename' : Tupu, 'lineno' : Tupu, 'offset' : Tupu}),
            (SyntaxError, ('msgStr', ('filenameStr', 'linenoStr', 'offsetStr',
                           'textStr')),
                {'offset' : 'offsetStr', 'text' : 'textStr',
                 'args' : ('msgStr', ('filenameStr', 'linenoStr',
                                      'offsetStr', 'textStr')),
                 'print_file_and_line' : Tupu, 'msg' : 'msgStr',
                 'filename' : 'filenameStr', 'lineno' : 'linenoStr'}),
            (SyntaxError, ('msgStr', 'filenameStr', 'linenoStr', 'offsetStr',
                           'textStr', 'print_file_and_lineStr'),
                {'text' : Tupu,
                 'args' : ('msgStr', 'filenameStr', 'linenoStr', 'offsetStr',
                           'textStr', 'print_file_and_lineStr'),
                 'print_file_and_line' : Tupu, 'msg' : 'msgStr',
                 'filename' : Tupu, 'lineno' : Tupu, 'offset' : Tupu}),
            (UnicodeError, (), {'args' : (),}),
            (UnicodeEncodeError, ('ascii', 'a', 0, 1,
                                  'ordinal sio kwenye range'),
                {'args' : ('ascii', 'a', 0, 1,
                                           'ordinal sio kwenye range'),
                 'encoding' : 'ascii', 'object' : 'a',
                 'start' : 0, 'reason' : 'ordinal sio kwenye range'}),
            (UnicodeDecodeError, ('ascii', bytearray(b'\xff'), 0, 1,
                                  'ordinal sio kwenye range'),
                {'args' : ('ascii', bytearray(b'\xff'), 0, 1,
                                           'ordinal sio kwenye range'),
                 'encoding' : 'ascii', 'object' : b'\xff',
                 'start' : 0, 'reason' : 'ordinal sio kwenye range'}),
            (UnicodeDecodeError, ('ascii', b'\xff', 0, 1,
                                  'ordinal sio kwenye range'),
                {'args' : ('ascii', b'\xff', 0, 1,
                                           'ordinal sio kwenye range'),
                 'encoding' : 'ascii', 'object' : b'\xff',
                 'start' : 0, 'reason' : 'ordinal sio kwenye range'}),
            (UnicodeTranslateError, ("\u3042", 0, 1, "ouch"),
                {'args' : ('\u3042', 0, 1, 'ouch'),
                 'object' : '\u3042', 'reason' : 'ouch',
                 'start' : 0, 'end' : 1}),
            (NaiveException, ('foo',),
                {'args': ('foo',), 'x': 'foo'}),
            (SlottedNaiveException, ('foo',),
                {'args': ('foo',), 'x': 'foo'}),
        ]
        jaribu:
            # More tests are kwenye test_WindowsError
            exceptionList.append(
                (WindowsError, (1, 'strErrorStr', 'filenameStr'),
                    {'args' : (1, 'strErrorStr'),
                     'strerror' : 'strErrorStr', 'winerror' : Tupu,
                     'errno' : 1,
                     'filename' : 'filenameStr', 'filename2' : Tupu})
            )
        except NameError:
            pass

        kila exc, args, expected kwenye exceptionList:
            jaribu:
                e = exc(*args)
            tatizo:
                andika("\nexc=%r, args=%r" % (exc, args), file=sys.stderr)
                raise
            isipokua:
                # Verify module name
                ikiwa sio type(e).__name__.endswith('NaiveException'):
                    self.assertEqual(type(e).__module__, 'builtins')
                # Verify no ref leaks kwenye Exc_str()
                s = str(e)
                kila checkArgName kwenye expected:
                    value = getattr(e, checkArgName)
                    self.assertEqual(repr(value),
                                     repr(expected[checkArgName]),
                                     '%r.%s == %r, expected %r' % (
                                     e, checkArgName,
                                     value, expected[checkArgName]))

                # test kila pickling support
                kila p kwenye [pickle]:
                    kila protocol kwenye range(p.HIGHEST_PROTOCOL + 1):
                        s = p.dumps(e, protocol)
                        new = p.loads(s)
                        kila checkArgName kwenye expected:
                            got = repr(getattr(new, checkArgName))
                            want = repr(expected[checkArgName])
                            self.assertEqual(got, want,
                                             'pickled "%r", attribute "%s' %
                                             (e, checkArgName))

    eleza testWithTraceback(self):
        jaribu:
             ashiria IndexError(4)
        tatizo:
            tb = sys.exc_info()[2]

        e = BaseException().with_traceback(tb)
        self.assertIsInstance(e, BaseException)
        self.assertEqual(e.__traceback__, tb)

        e = IndexError(5).with_traceback(tb)
        self.assertIsInstance(e, IndexError)
        self.assertEqual(e.__traceback__, tb)

        kundi MyException(Exception):
            pass

        e = MyException().with_traceback(tb)
        self.assertIsInstance(e, MyException)
        self.assertEqual(e.__traceback__, tb)

    eleza testInvalidTraceback(self):
        jaribu:
            Exception().__traceback__ = 5
        except TypeError as e:
            self.assertIn("__traceback__ must be a traceback", str(e))
        isipokua:
            self.fail("No exception raised")

    eleza testInvalidAttrs(self):
        self.assertRaises(TypeError, setattr, Exception(), '__cause__', 1)
        self.assertRaises(TypeError, delattr, Exception(), '__cause__')
        self.assertRaises(TypeError, setattr, Exception(), '__context__', 1)
        self.assertRaises(TypeError, delattr, Exception(), '__context__')

    eleza testTupuClearsTracebackAttr(self):
        jaribu:
             ashiria IndexError(4)
        tatizo:
            tb = sys.exc_info()[2]

        e = Exception()
        e.__traceback__ = tb
        e.__traceback__ = Tupu
        self.assertEqual(e.__traceback__, Tupu)

    eleza testChainingAttrs(self):
        e = Exception()
        self.assertIsTupu(e.__context__)
        self.assertIsTupu(e.__cause__)

        e = TypeError()
        self.assertIsTupu(e.__context__)
        self.assertIsTupu(e.__cause__)

        kundi MyException(OSError):
            pass

        e = MyException()
        self.assertIsTupu(e.__context__)
        self.assertIsTupu(e.__cause__)

    eleza testChainingDescriptors(self):
        jaribu:
             ashiria Exception()
        except Exception as exc:
            e = exc

        self.assertIsTupu(e.__context__)
        self.assertIsTupu(e.__cause__)
        self.assertUongo(e.__suppress_context__)

        e.__context__ = NameError()
        e.__cause__ = Tupu
        self.assertIsInstance(e.__context__, NameError)
        self.assertIsTupu(e.__cause__)
        self.assertKweli(e.__suppress_context__)
        e.__suppress_context__ = Uongo
        self.assertUongo(e.__suppress_context__)

    eleza testKeywordArgs(self):
        # test that builtin exception don't take keyword args,
        # but user-defined subclasses can ikiwa they want
        self.assertRaises(TypeError, BaseException, a=1)

        kundi DerivedException(BaseException):
            eleza __init__(self, fancy_arg):
                BaseException.__init__(self)
                self.fancy_arg = fancy_arg

        x = DerivedException(fancy_arg=42)
        self.assertEqual(x.fancy_arg, 42)

    @no_tracing
    eleza testInfiniteRecursion(self):
        eleza f():
            rudisha f()
        self.assertRaises(RecursionError, f)

        eleza g():
            jaribu:
                rudisha g()
            except ValueError:
                rudisha -1
        self.assertRaises(RecursionError, g)

    eleza test_str(self):
        # Make sure both instances na classes have a str representation.
        self.assertKweli(str(Exception))
        self.assertKweli(str(Exception('a')))
        self.assertKweli(str(Exception('a', 'b')))

    eleza testExceptionCleanupNames(self):
        # Make sure the local variable bound to the exception instance by
        # an "except" statement ni only visible inside the except block.
        jaribu:
             ashiria Exception()
        except Exception as e:
            self.assertKweli(e)
            toa e
        self.assertNotIn('e', locals())

    eleza testExceptionCleanupState(self):
        # Make sure exception state ni cleaned up as soon as the except
        # block ni left. See #2507

        kundi MyException(Exception):
            eleza __init__(self, obj):
                self.obj = obj
        kundi MyObj:
            pass

        eleza inner_raising_func():
            # Create some references kwenye exception value na traceback
            local_ref = obj
             ashiria MyException(obj)

        # Qualified "except" ukijumuisha "as"
        obj = MyObj()
        wr = weakref.ref(obj)
        jaribu:
            inner_raising_func()
        except MyException as e:
            pass
        obj = Tupu
        obj = wr()
        self.assertIsTupu(obj)

        # Qualified "except" without "as"
        obj = MyObj()
        wr = weakref.ref(obj)
        jaribu:
            inner_raising_func()
        except MyException:
            pass
        obj = Tupu
        obj = wr()
        self.assertIsTupu(obj)

        # Bare "except"
        obj = MyObj()
        wr = weakref.ref(obj)
        jaribu:
            inner_raising_func()
        tatizo:
            pass
        obj = Tupu
        obj = wr()
        self.assertIsTupu(obj)

        # "except" ukijumuisha premature block leave
        obj = MyObj()
        wr = weakref.ref(obj)
        kila i kwenye [0]:
            jaribu:
                inner_raising_func()
            tatizo:
                koma
        obj = Tupu
        obj = wr()
        self.assertIsTupu(obj)

        # "except" block raising another exception
        obj = MyObj()
        wr = weakref.ref(obj)
        jaribu:
            jaribu:
                inner_raising_func()
            tatizo:
                 ashiria KeyError
        except KeyError as e:
            # We want to test that the except block above got rid of
            # the exception raised kwenye inner_raising_func(), but it
            # also ends up kwenye the __context__ of the KeyError, so we
            # must clear the latter manually kila our test to succeed.
            e.__context__ = Tupu
            obj = Tupu
            obj = wr()
            # guarantee no ref cycles on CPython (don't gc_collect)
            ikiwa check_impl_detail(cpython=Uongo):
                gc_collect()
            self.assertIsTupu(obj)

        # Some complicated construct
        obj = MyObj()
        wr = weakref.ref(obj)
        jaribu:
            inner_raising_func()
        except MyException:
            jaribu:
                jaribu:
                    raise
                mwishowe:
                    raise
            except MyException:
                pass
        obj = Tupu
        ikiwa check_impl_detail(cpython=Uongo):
            gc_collect()
        obj = wr()
        self.assertIsTupu(obj)

        # Inside an exception-silencing "with" block
        kundi Context:
            eleza __enter__(self):
                rudisha self
            eleza __exit__ (self, exc_type, exc_value, exc_tb):
                rudisha Kweli
        obj = MyObj()
        wr = weakref.ref(obj)
        ukijumuisha Context():
            inner_raising_func()
        obj = Tupu
        ikiwa check_impl_detail(cpython=Uongo):
            gc_collect()
        obj = wr()
        self.assertIsTupu(obj)

    eleza test_exception_target_in_nested_scope(self):
        # issue 4617: This used to  ashiria a SyntaxError
        # "can sio delete variable 'e' referenced kwenye nested scope"
        eleza print_error():
            e
        jaribu:
            something
        except Exception as e:
            print_error()
            # implicit "toa e" here

    eleza test_generator_leaking(self):
        # Test that generator exception state doesn't leak into the calling
        # frame
        eleza yield_raise():
            jaribu:
                 ashiria KeyError("caught")
            except KeyError:
                tuma sys.exc_info()[0]
                tuma sys.exc_info()[0]
            tuma sys.exc_info()[0]
        g = yield_raise()
        self.assertEqual(next(g), KeyError)
        self.assertEqual(sys.exc_info()[0], Tupu)
        self.assertEqual(next(g), KeyError)
        self.assertEqual(sys.exc_info()[0], Tupu)
        self.assertEqual(next(g), Tupu)

        # Same test, but inside an exception handler
        jaribu:
             ashiria TypeError("foo")
        except TypeError:
            g = yield_raise()
            self.assertEqual(next(g), KeyError)
            self.assertEqual(sys.exc_info()[0], TypeError)
            self.assertEqual(next(g), KeyError)
            self.assertEqual(sys.exc_info()[0], TypeError)
            self.assertEqual(next(g), TypeError)
            toa g
            self.assertEqual(sys.exc_info()[0], TypeError)

    eleza test_generator_leaking2(self):
        # See issue 12475.
        eleza g():
            yield
        jaribu:
             ashiria RuntimeError
        except RuntimeError:
            it = g()
            next(it)
        jaribu:
            next(it)
        except StopIteration:
            pass
        self.assertEqual(sys.exc_info(), (Tupu, Tupu, Tupu))

    eleza test_generator_leaking3(self):
        # See issue #23353.  When gen.throw() ni called, the caller's
        # exception state should be save na restored.
        eleza g():
            jaribu:
                yield
            except ZeroDivisionError:
                tuma sys.exc_info()[1]
        it = g()
        next(it)
        jaribu:
            1/0
        except ZeroDivisionError as e:
            self.assertIs(sys.exc_info()[1], e)
            gen_exc = it.throw(e)
            self.assertIs(sys.exc_info()[1], e)
            self.assertIs(gen_exc, e)
        self.assertEqual(sys.exc_info(), (Tupu, Tupu, Tupu))

    eleza test_generator_leaking4(self):
        # See issue #23353.  When an exception ni raised by a generator,
        # the caller's exception state should still be restored.
        eleza g():
            jaribu:
                1/0
            except ZeroDivisionError:
                tuma sys.exc_info()[0]
                raise
        it = g()
        jaribu:
             ashiria TypeError
        except TypeError:
            # The caller's exception state (TypeError) ni temporarily
            # saved kwenye the generator.
            tp = next(it)
        self.assertIs(tp, ZeroDivisionError)
        jaribu:
            next(it)
            # We can't check it immediately, but wakati next() returns
            # ukijumuisha an exception, it shouldn't have restored the old
            # exception state (TypeError).
        except ZeroDivisionError as e:
            self.assertIs(sys.exc_info()[1], e)
        # We used to find TypeError here.
        self.assertEqual(sys.exc_info(), (Tupu, Tupu, Tupu))

    eleza test_generator_doesnt_retain_old_exc(self):
        eleza g():
            self.assertIsInstance(sys.exc_info()[1], RuntimeError)
            yield
            self.assertEqual(sys.exc_info(), (Tupu, Tupu, Tupu))
        it = g()
        jaribu:
             ashiria RuntimeError
        except RuntimeError:
            next(it)
        self.assertRaises(StopIteration, next, it)

    eleza test_generator_finalizing_and_exc_info(self):
        # See #7173
        eleza simple_gen():
            tuma 1
        eleza run_gen():
            gen = simple_gen()
            jaribu:
                 ashiria RuntimeError
            except RuntimeError:
                rudisha next(gen)
        run_gen()
        gc_collect()
        self.assertEqual(sys.exc_info(), (Tupu, Tupu, Tupu))

    eleza _check_generator_cleanup_exc_state(self, testfunc):
        # Issue #12791: exception state ni cleaned up as soon as a generator
        # ni closed (reference cycles are broken).
        kundi MyException(Exception):
            eleza __init__(self, obj):
                self.obj = obj
        kundi MyObj:
            pass

        eleza raising_gen():
            jaribu:
                 ashiria MyException(obj)
            except MyException:
                yield

        obj = MyObj()
        wr = weakref.ref(obj)
        g = raising_gen()
        next(g)
        testfunc(g)
        g = obj = Tupu
        obj = wr()
        self.assertIsTupu(obj)

    eleza test_generator_throw_cleanup_exc_state(self):
        eleza do_throw(g):
            jaribu:
                g.throw(RuntimeError())
            except RuntimeError:
                pass
        self._check_generator_cleanup_exc_state(do_throw)

    eleza test_generator_close_cleanup_exc_state(self):
        eleza do_close(g):
            g.close()
        self._check_generator_cleanup_exc_state(do_close)

    eleza test_generator_del_cleanup_exc_state(self):
        eleza do_del(g):
            g = Tupu
        self._check_generator_cleanup_exc_state(do_del)

    eleza test_generator_next_cleanup_exc_state(self):
        eleza do_next(g):
            jaribu:
                next(g)
            except StopIteration:
                pass
            isipokua:
                self.fail("should have raised StopIteration")
        self._check_generator_cleanup_exc_state(do_next)

    eleza test_generator_send_cleanup_exc_state(self):
        eleza do_send(g):
            jaribu:
                g.send(Tupu)
            except StopIteration:
                pass
            isipokua:
                self.fail("should have raised StopIteration")
        self._check_generator_cleanup_exc_state(do_send)

    eleza test_3114(self):
        # Bug #3114: kwenye its destructor, MyObject retrieves a pointer to
        # obsolete and/or deallocated objects.
        kundi MyObject:
            eleza __del__(self):
                nonlocal e
                e = sys.exc_info()
        e = ()
        jaribu:
             ashiria Exception(MyObject())
        tatizo:
            pass
        self.assertEqual(e, (Tupu, Tupu, Tupu))

    eleza test_unicode_change_attributes(self):
        # See issue 7309. This was a crasher.

        u = UnicodeEncodeError('baz', 'xxxxx', 1, 5, 'foo')
        self.assertEqual(str(u), "'baz' codec can't encode characters kwenye position 1-4: foo")
        u.end = 2
        self.assertEqual(str(u), "'baz' codec can't encode character '\\x78' kwenye position 1: foo")
        u.end = 5
        u.reason = 0x345345345345345345
        self.assertEqual(str(u), "'baz' codec can't encode characters kwenye position 1-4: 965230951443685724997")
        u.encoding = 4000
        self.assertEqual(str(u), "'4000' codec can't encode characters kwenye position 1-4: 965230951443685724997")
        u.start = 1000
        self.assertEqual(str(u), "'4000' codec can't encode characters kwenye position 1000-4: 965230951443685724997")

        u = UnicodeDecodeError('baz', b'xxxxx', 1, 5, 'foo')
        self.assertEqual(str(u), "'baz' codec can't decode bytes kwenye position 1-4: foo")
        u.end = 2
        self.assertEqual(str(u), "'baz' codec can't decode byte 0x78 kwenye position 1: foo")
        u.end = 5
        u.reason = 0x345345345345345345
        self.assertEqual(str(u), "'baz' codec can't decode bytes kwenye position 1-4: 965230951443685724997")
        u.encoding = 4000
        self.assertEqual(str(u), "'4000' codec can't decode bytes kwenye position 1-4: 965230951443685724997")
        u.start = 1000
        self.assertEqual(str(u), "'4000' codec can't decode bytes kwenye position 1000-4: 965230951443685724997")

        u = UnicodeTranslateError('xxxx', 1, 5, 'foo')
        self.assertEqual(str(u), "can't translate characters kwenye position 1-4: foo")
        u.end = 2
        self.assertEqual(str(u), "can't translate character '\\x78' kwenye position 1: foo")
        u.end = 5
        u.reason = 0x345345345345345345
        self.assertEqual(str(u), "can't translate characters kwenye position 1-4: 965230951443685724997")
        u.start = 1000
        self.assertEqual(str(u), "can't translate characters kwenye position 1000-4: 965230951443685724997")

    eleza test_unicode_errors_no_object(self):
        # See issue #21134.
        klasses = UnicodeEncodeError, UnicodeDecodeError, UnicodeTranslateError
        kila klass kwenye klasses:
            self.assertEqual(str(klass.__new__(klass)), "")

    @no_tracing
    eleza test_badisinstance(self):
        # Bug #2542: ikiwa issubclass(e, MyException) raises an exception,
        # it should be ignored
        kundi Meta(type):
            eleza __subclasscheck__(cls, subclass):
                 ashiria ValueError()
        kundi MyException(Exception, metaclass=Meta):
            pass

        ukijumuisha captured_stderr() as stderr:
            jaribu:
                 ashiria KeyError()
            except MyException as e:
                self.fail("exception should sio be a MyException")
            except KeyError:
                pass
            tatizo:
                self.fail("Should have raised KeyError")
            isipokua:
                self.fail("Should have raised KeyError")

        eleza g():
            jaribu:
                rudisha g()
            except RecursionError:
                rudisha sys.exc_info()
        e, v, tb = g()
        self.assertIsInstance(v, RecursionError, type(v))
        self.assertIn("maximum recursion depth exceeded", str(v))

    @cpython_only
    eleza test_recursion_normalizing_exception(self):
        # Issue #22898.
        # Test that a RecursionError ni raised when tstate->recursion_depth is
        # equal to recursion_limit kwenye PyErr_NormalizeException() na check
        # that a ResourceWarning ni printed.
        # Prior to #22898, the recursivity of PyErr_NormalizeException() was
        # controlled by tstate->recursion_depth na a PyExc_RecursionErrorInst
        # singleton was being used kwenye that case, that held traceback data and
        # locals indefinitely na would cause a segfault kwenye _PyExc_Fini() upon
        # finalization of these locals.
        code = """ikiwa 1:
            agiza sys
            kutoka _testcapi agiza get_recursion_depth

            kundi MyException(Exception): pass

            eleza setrecursionlimit(depth):
                wakati 1:
                    jaribu:
                        sys.setrecursionlimit(depth)
                        rudisha depth
                    except RecursionError:
                        # sys.setrecursionlimit() raises a RecursionError if
                        # the new recursion limit ni too low (issue #25274).
                        depth += 1

            eleza recurse(cnt):
                cnt -= 1
                ikiwa cnt:
                    recurse(cnt)
                isipokua:
                    generator.throw(MyException)

            eleza gen():
                f = open(%a, mode='rb', buffering=0)
                yield

            generator = gen()
            next(generator)
            recursionlimit = sys.getrecursionlimit()
            depth = get_recursion_depth()
            jaribu:
                # Upon the last recursive invocation of recurse(),
                # tstate->recursion_depth ni equal to (recursion_limit - 1)
                # na ni equal to recursion_limit when _gen_throw() calls
                # PyErr_NormalizeException().
                recurse(setrecursionlimit(depth + 2) - depth - 1)
            mwishowe:
                sys.setrecursionlimit(recursionlimit)
                andika('Done.')
        """ % __file__
        rc, out, err = script_helper.assert_python_failure("-Wd", "-c", code)
        # Check that the program does sio fail ukijumuisha SIGABRT.
        self.assertEqual(rc, 1)
        self.assertIn(b'RecursionError', err)
        self.assertIn(b'ResourceWarning', err)
        self.assertIn(b'Done.', out)

    @cpython_only
    eleza test_recursion_normalizing_infinite_exception(self):
        # Issue #30697. Test that a RecursionError ni raised when
        # PyErr_NormalizeException() maximum recursion depth has been
        # exceeded.
        code = """ikiwa 1:
            agiza _testcapi
            jaribu:
                 ashiria _testcapi.RecursingInfinitelyError
            mwishowe:
                andika('Done.')
        """
        rc, out, err = script_helper.assert_python_failure("-c", code)
        self.assertEqual(rc, 1)
        self.assertIn(b'RecursionError: maximum recursion depth exceeded '
                      b'wakati normalizing an exception', err)
        self.assertIn(b'Done.', out)

    @cpython_only
    eleza test_recursion_normalizing_with_no_memory(self):
        # Issue #30697. Test that kwenye the abort that occurs when there ni no
        # memory left na the size of the Python frames stack ni greater than
        # the size of the list of preallocated MemoryError instances, the
        # Fatal Python error message mentions MemoryError.
        code = """ikiwa 1:
            agiza _testcapi
            kundi C(): pass
            eleza recurse(cnt):
                cnt -= 1
                ikiwa cnt:
                    recurse(cnt)
                isipokua:
                    _testcapi.set_nomemory(0)
                    C()
            recurse(16)
        """
        ukijumuisha SuppressCrashReport():
            rc, out, err = script_helper.assert_python_failure("-c", code)
            self.assertIn(b'Fatal Python error: Cannot recover kutoka '
                          b'MemoryErrors wakati normalizing exceptions.', err)

    @cpython_only
    eleza test_MemoryError(self):
        # PyErr_NoMemory always raises the same exception instance.
        # Check that the traceback ni sio doubled.
        agiza traceback
        kutoka _testcapi agiza raise_memoryerror
        eleza raiseMemError():
            jaribu:
                raise_memoryerror()
            except MemoryError as e:
                tb = e.__traceback__
            isipokua:
                self.fail("Should have raises a MemoryError")
            rudisha traceback.format_tb(tb)

        tb1 = raiseMemError()
        tb2 = raiseMemError()
        self.assertEqual(tb1, tb2)

    @cpython_only
    eleza test_exception_with_doc(self):
        agiza _testcapi
        doc2 = "This ni a test docstring."
        doc4 = "This ni another test docstring."

        self.assertRaises(SystemError, _testcapi.make_exception_with_doc,
                          "error1")

        # test basic usage of PyErr_NewException
        error1 = _testcapi.make_exception_with_doc("_testcapi.error1")
        self.assertIs(type(error1), type)
        self.assertKweli(issubclass(error1, Exception))
        self.assertIsTupu(error1.__doc__)

        # test ukijumuisha given docstring
        error2 = _testcapi.make_exception_with_doc("_testcapi.error2", doc2)
        self.assertEqual(error2.__doc__, doc2)

        # test ukijumuisha explicit base (without docstring)
        error3 = _testcapi.make_exception_with_doc("_testcapi.error3",
                                                   base=error2)
        self.assertKweli(issubclass(error3, error2))

        # test ukijumuisha explicit base tuple
        kundi C(object):
            pass
        error4 = _testcapi.make_exception_with_doc("_testcapi.error4", doc4,
                                                   (error3, C))
        self.assertKweli(issubclass(error4, error3))
        self.assertKweli(issubclass(error4, C))
        self.assertEqual(error4.__doc__, doc4)

        # test ukijumuisha explicit dictionary
        error5 = _testcapi.make_exception_with_doc("_testcapi.error5", "",
                                                   error4, {'a': 1})
        self.assertKweli(issubclass(error5, error4))
        self.assertEqual(error5.a, 1)
        self.assertEqual(error5.__doc__, "")

    @cpython_only
    eleza test_memory_error_cleanup(self):
        # Issue #5437: preallocated MemoryError instances should sio keep
        # traceback objects alive.
        kutoka _testcapi agiza raise_memoryerror
        kundi C:
            pass
        wr = Tupu
        eleza inner():
            nonlocal wr
            c = C()
            wr = weakref.ref(c)
            raise_memoryerror()
        # We cannot use assertRaises since it manually deletes the traceback
        jaribu:
            inner()
        except MemoryError as e:
            self.assertNotEqual(wr(), Tupu)
        isipokua:
            self.fail("MemoryError sio raised")
        self.assertEqual(wr(), Tupu)

    @no_tracing
    eleza test_recursion_error_cleanup(self):
        # Same test as above, but ukijumuisha "recursion exceeded" errors
        kundi C:
            pass
        wr = Tupu
        eleza inner():
            nonlocal wr
            c = C()
            wr = weakref.ref(c)
            inner()
        # We cannot use assertRaises since it manually deletes the traceback
        jaribu:
            inner()
        except RecursionError as e:
            self.assertNotEqual(wr(), Tupu)
        isipokua:
            self.fail("RecursionError sio raised")
        self.assertEqual(wr(), Tupu)

    eleza test_errno_ENOTDIR(self):
        # Issue #12802: "not a directory" errors are ENOTDIR even on Windows
        ukijumuisha self.assertRaises(OSError) as cm:
            os.listdir(__file__)
        self.assertEqual(cm.exception.errno, errno.ENOTDIR, cm.exception)

    eleza test_unraisable(self):
        # Issue #22836: PyErr_WriteUnraisable() should give sensible reports
        kundi BrokenDel:
            eleza __del__(self):
                exc = ValueError("toa ni broken")
                # The following line ni included kwenye the traceback report:
                 ashiria exc

        obj = BrokenDel()
        ukijumuisha support.catch_unraisable_exception() as cm:
            toa obj

            self.assertEqual(cm.unraisable.object, BrokenDel.__del__)
            self.assertIsNotTupu(cm.unraisable.exc_traceback)

    eleza test_unhandled(self):
        # Check kila sensible reporting of unhandled exceptions
        kila exc_type kwenye (ValueError, BrokenStrException):
            ukijumuisha self.subTest(exc_type):
                jaribu:
                    exc = exc_type("test message")
                    # The following line ni included kwenye the traceback report:
                     ashiria exc
                except exc_type:
                    ukijumuisha captured_stderr() as stderr:
                        sys.__excepthook__(*sys.exc_info())
                report = stderr.getvalue()
                self.assertIn("test_exceptions.py", report)
                self.assertIn(" ashiria exc", report)
                self.assertIn(exc_type.__name__, report)
                ikiwa exc_type ni BrokenStrException:
                    self.assertIn("<exception str() failed>", report)
                isipokua:
                    self.assertIn("test message", report)
                self.assertKweli(report.endswith("\n"))

    @cpython_only
    eleza test_memory_error_in_PyErr_PrintEx(self):
        code = """ikiwa 1:
            agiza _testcapi
            kundi C(): pass
            _testcapi.set_nomemory(0, %d)
            C()
        """

        # Issue #30817: Abort kwenye PyErr_PrintEx() when no memory.
        # Span a large range of tests as the CPython code always evolves with
        # changes that add ama remove memory allocations.
        kila i kwenye range(1, 20):
            rc, out, err = script_helper.assert_python_failure("-c", code % i)
            self.assertIn(rc, (1, 120))
            self.assertIn(b'MemoryError', err)

    eleza test_yield_in_nested_try_excepts(self):
        #Issue #25612
        kundi MainError(Exception):
            pass

        kundi SubError(Exception):
            pass

        eleza main():
            jaribu:
                 ashiria MainError()
            except MainError:
                jaribu:
                    yield
                except SubError:
                    pass
                raise

        coro = main()
        coro.send(Tupu)
        ukijumuisha self.assertRaises(MainError):
            coro.throw(SubError())

    eleza test_generator_doesnt_retain_old_exc2(self):
        #Issue 28884#msg282532
        eleza g():
            jaribu:
                 ashiria ValueError
            except ValueError:
                tuma 1
            self.assertEqual(sys.exc_info(), (Tupu, Tupu, Tupu))
            tuma 2

        gen = g()

        jaribu:
             ashiria IndexError
        except IndexError:
            self.assertEqual(next(gen), 1)
        self.assertEqual(next(gen), 2)

    eleza test_raise_in_generator(self):
        #Issue 25612#msg304117
        eleza g():
            tuma 1
            raise
            tuma 2

        ukijumuisha self.assertRaises(ZeroDivisionError):
            i = g()
            jaribu:
                1/0
            tatizo:
                next(i)
                next(i)


kundi ImportErrorTests(unittest.TestCase):

    eleza test_attributes(self):
        # Setting 'name' na 'path' should sio be a problem.
        exc = ImportError('test')
        self.assertIsTupu(exc.name)
        self.assertIsTupu(exc.path)

        exc = ImportError('test', name='somemodule')
        self.assertEqual(exc.name, 'somemodule')
        self.assertIsTupu(exc.path)

        exc = ImportError('test', path='somepath')
        self.assertEqual(exc.path, 'somepath')
        self.assertIsTupu(exc.name)

        exc = ImportError('test', path='somepath', name='somename')
        self.assertEqual(exc.name, 'somename')
        self.assertEqual(exc.path, 'somepath')

        msg = "'invalid' ni an invalid keyword argument kila ImportError"
        ukijumuisha self.assertRaisesRegex(TypeError, msg):
            ImportError('test', invalid='keyword')

        ukijumuisha self.assertRaisesRegex(TypeError, msg):
            ImportError('test', name='name', invalid='keyword')

        ukijumuisha self.assertRaisesRegex(TypeError, msg):
            ImportError('test', path='path', invalid='keyword')

        ukijumuisha self.assertRaisesRegex(TypeError, msg):
            ImportError(invalid='keyword')

        ukijumuisha self.assertRaisesRegex(TypeError, msg):
            ImportError('test', invalid='keyword', another=Kweli)

    eleza test_reset_attributes(self):
        exc = ImportError('test', name='name', path='path')
        self.assertEqual(exc.args, ('test',))
        self.assertEqual(exc.msg, 'test')
        self.assertEqual(exc.name, 'name')
        self.assertEqual(exc.path, 'path')

        # Reset sio specified attributes
        exc.__init__()
        self.assertEqual(exc.args, ())
        self.assertEqual(exc.msg, Tupu)
        self.assertEqual(exc.name, Tupu)
        self.assertEqual(exc.path, Tupu)

    eleza test_non_str_argument(self):
        # Issue #15778
        ukijumuisha check_warnings(('', BytesWarning), quiet=Kweli):
            arg = b'abc'
            exc = ImportError(arg)
            self.assertEqual(str(arg), str(exc))

    eleza test_copy_pickle(self):
        kila kwargs kwenye (dict(),
                       dict(name='somename'),
                       dict(path='somepath'),
                       dict(name='somename', path='somepath')):
            orig = ImportError('test', **kwargs)
            kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
                exc = pickle.loads(pickle.dumps(orig, proto))
                self.assertEqual(exc.args, ('test',))
                self.assertEqual(exc.msg, 'test')
                self.assertEqual(exc.name, orig.name)
                self.assertEqual(exc.path, orig.path)
            kila c kwenye copy.copy, copy.deepcopy:
                exc = c(orig)
                self.assertEqual(exc.args, ('test',))
                self.assertEqual(exc.msg, 'test')
                self.assertEqual(exc.name, orig.name)
                self.assertEqual(exc.path, orig.path)


ikiwa __name__ == '__main__':
    unittest.main()
