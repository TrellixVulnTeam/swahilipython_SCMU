agiza unittest
agiza builtins
agiza os
kutoka platform agiza system kama platform_system


kundi ExceptionClassTests(unittest.TestCase):

    """Tests kila anything relating to exception objects themselves (e.g.,
    inheritance hierarchy)"""

    eleza test_builtins_new_style(self):
        self.assertKweli(issubclass(Exception, object))

    eleza verify_instance_interface(self, ins):
        kila attr kwenye ("args", "__str__", "__repr__"):
            self.assertKweli(hasattr(ins, attr),
                    "%s missing %s attribute" %
                        (ins.__class__.__name__, attr))

    eleza test_inheritance(self):
        # Make sure the inheritance hierarchy matches the documentation
        exc_set = set()
        kila object_ kwenye builtins.__dict__.values():
            jaribu:
                ikiwa issubclass(object_, BaseException):
                    exc_set.add(object_.__name__)
            tatizo TypeError:
                pita

        inheritance_tree = open(os.path.join(os.path.split(__file__)[0],
                                                'exception_hierarchy.txt'))
        jaribu:
            superclass_name = inheritance_tree.readline().rstrip()
            jaribu:
                last_exc = getattr(builtins, superclass_name)
            tatizo AttributeError:
                self.fail("base kundi %s sio a built-in" % superclass_name)
            self.assertIn(superclass_name, exc_set,
                          '%s sio found' % superclass_name)
            exc_set.discard(superclass_name)
            superclasses = []  # Loop will insert base exception
            last_depth = 0
            kila exc_line kwenye inheritance_tree:
                exc_line = exc_line.rstrip()
                depth = exc_line.rindex('-')
                exc_name = exc_line[depth+2:]  # Slice past space
                ikiwa '(' kwenye exc_name:
                    paren_index = exc_name.index('(')
                    platform_name = exc_name[paren_index+1:-1]
                    exc_name = exc_name[:paren_index-1]  # Slice off space
                    ikiwa platform_system() != platform_name:
                        exc_set.discard(exc_name)
                        endelea
                ikiwa '[' kwenye exc_name:
                    left_bracket = exc_name.index('[')
                    exc_name = exc_name[:left_bracket-1]  # cover space
                jaribu:
                    exc = getattr(builtins, exc_name)
                tatizo AttributeError:
                    self.fail("%s sio a built-in exception" % exc_name)
                ikiwa last_depth < depth:
                    superclasses.append((last_depth, last_exc))
                lasivyo last_depth > depth:
                    wakati superclasses[-1][0] >= depth:
                        superclasses.pop()
                self.assertKweli(issubclass(exc, superclasses[-1][1]),
                "%s ni sio a subkundi of %s" % (exc.__name__,
                    superclasses[-1][1].__name__))
                jaribu:  # Some exceptions require arguments; just skip them
                    self.verify_instance_interface(exc())
                tatizo TypeError:
                    pita
                self.assertIn(exc_name, exc_set)
                exc_set.discard(exc_name)
                last_exc = exc
                last_depth = depth
        mwishowe:
            inheritance_tree.close()
        self.assertEqual(len(exc_set), 0, "%s sio accounted for" % exc_set)

    interface_tests = ("length", "args", "str", "repr")

    eleza interface_test_driver(self, results):
        kila test_name, (given, expected) kwenye zip(self.interface_tests, results):
            self.assertEqual(given, expected, "%s: %s != %s" % (test_name,
                given, expected))

    eleza test_interface_single_arg(self):
        # Make sure interface works properly when given a single argument
        arg = "spam"
        exc = Exception(arg)
        results = ([len(exc.args), 1], [exc.args[0], arg],
                   [str(exc), str(arg)],
            [repr(exc), '%s(%r)' % (exc.__class__.__name__, arg)])
        self.interface_test_driver(results)

    eleza test_interface_multi_arg(self):
        # Make sure interface correct when multiple arguments given
        arg_count = 3
        args = tuple(range(arg_count))
        exc = Exception(*args)
        results = ([len(exc.args), arg_count], [exc.args, args],
                [str(exc), str(args)],
                [repr(exc), exc.__class__.__name__ + repr(exc.args)])
        self.interface_test_driver(results)

    eleza test_interface_no_arg(self):
        # Make sure that ukijumuisha no args that interface ni correct
        exc = Exception()
        results = ([len(exc.args), 0], [exc.args, tuple()],
                [str(exc), ''],
                [repr(exc), exc.__class__.__name__ + '()'])
        self.interface_test_driver(results)

kundi UsageTests(unittest.TestCase):

    """Test usage of exceptions"""

    eleza raise_fails(self, object_):
        """Make sure that raising 'object_' triggers a TypeError."""
        jaribu:
            ashiria object_
        tatizo TypeError:
            rudisha  # What ni expected.
        self.fail("TypeError expected kila raising %s" % type(object_))

    eleza catch_fails(self, object_):
        """Catching 'object_' should ashiria a TypeError."""
        jaribu:
            jaribu:
                ashiria Exception
            tatizo object_:
                pita
        tatizo TypeError:
            pita
        tatizo Exception:
            self.fail("TypeError expected when catching %s" % type(object_))

        jaribu:
            jaribu:
                ashiria Exception
            tatizo (object_,):
                pita
        tatizo TypeError:
            rudisha
        tatizo Exception:
            self.fail("TypeError expected when catching %s kama specified kwenye a "
                        "tuple" % type(object_))

    eleza test_raise_new_style_non_exception(self):
        # You cannot ashiria a new-style kundi that does sio inerit from
        # BaseException; the ability was sio possible until BaseException's
        # introduction so no need to support new-style objects that do sio
        # inherit kutoka it.
        kundi NewStyleClass(object):
            pita
        self.raise_fails(NewStyleClass)
        self.raise_fails(NewStyleClass())

    eleza test_raise_string(self):
        # Raising a string raises TypeError.
        self.raise_fails("spam")

    eleza test_catch_non_BaseException(self):
        # Trying to catch an object that does sio inerit kutoka BaseException
        # ni sio allowed.
        kundi NonBaseException(object):
            pita
        self.catch_fails(NonBaseException)
        self.catch_fails(NonBaseException())

    eleza test_catch_BaseException_instance(self):
        # Catching an instance of a BaseException subkundi won't work.
        self.catch_fails(BaseException())

    eleza test_catch_string(self):
        # Catching a string ni bad.
        self.catch_fails("spam")


ikiwa __name__ == '__main__':
    unittest.main()
