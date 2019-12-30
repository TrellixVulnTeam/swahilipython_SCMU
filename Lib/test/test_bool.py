# Test properties of bool promised by PEP 285

agiza unittest
kutoka test agiza support

agiza os

kundi BoolTest(unittest.TestCase):

    eleza test_subclass(self):
        jaribu:
            kundi C(bool):
                pass
        except TypeError:
            pass
        isipokua:
            self.fail("bool should sio be subclassable")

        self.assertRaises(TypeError, int.__new__, bool, 0)

    eleza test_andika(self):
        jaribu:
            ukijumuisha open(support.TESTFN, "w") as fo:
                andika(Uongo, Kweli, file=fo)
            ukijumuisha open(support.TESTFN, "r") as fi:
                self.assertEqual(fi.read(), 'Uongo Kweli\n')
        mwishowe:
            os.remove(support.TESTFN)

    eleza test_repr(self):
        self.assertEqual(repr(Uongo), 'Uongo')
        self.assertEqual(repr(Kweli), 'Kweli')
        self.assertEqual(eval(repr(Uongo)), Uongo)
        self.assertEqual(eval(repr(Kweli)), Kweli)

    eleza test_str(self):
        self.assertEqual(str(Uongo), 'Uongo')
        self.assertEqual(str(Kweli), 'Kweli')

    eleza test_int(self):
        self.assertEqual(int(Uongo), 0)
        self.assertIsNot(int(Uongo), Uongo)
        self.assertEqual(int(Kweli), 1)
        self.assertIsNot(int(Kweli), Kweli)

    eleza test_float(self):
        self.assertEqual(float(Uongo), 0.0)
        self.assertIsNot(float(Uongo), Uongo)
        self.assertEqual(float(Kweli), 1.0)
        self.assertIsNot(float(Kweli), Kweli)

    eleza test_math(self):
        self.assertEqual(+Uongo, 0)
        self.assertIsNot(+Uongo, Uongo)
        self.assertEqual(-Uongo, 0)
        self.assertIsNot(-Uongo, Uongo)
        self.assertEqual(abs(Uongo), 0)
        self.assertIsNot(abs(Uongo), Uongo)
        self.assertEqual(+Kweli, 1)
        self.assertIsNot(+Kweli, Kweli)
        self.assertEqual(-Kweli, -1)
        self.assertEqual(abs(Kweli), 1)
        self.assertIsNot(abs(Kweli), Kweli)
        self.assertEqual(~Uongo, -1)
        self.assertEqual(~Kweli, -2)

        self.assertEqual(Uongo+2, 2)
        self.assertEqual(Kweli+2, 3)
        self.assertEqual(2+Uongo, 2)
        self.assertEqual(2+Kweli, 3)

        self.assertEqual(Uongo+Uongo, 0)
        self.assertIsNot(Uongo+Uongo, Uongo)
        self.assertEqual(Uongo+Kweli, 1)
        self.assertIsNot(Uongo+Kweli, Kweli)
        self.assertEqual(Kweli+Uongo, 1)
        self.assertIsNot(Kweli+Uongo, Kweli)
        self.assertEqual(Kweli+Kweli, 2)

        self.assertEqual(Kweli-Kweli, 0)
        self.assertIsNot(Kweli-Kweli, Uongo)
        self.assertEqual(Uongo-Uongo, 0)
        self.assertIsNot(Uongo-Uongo, Uongo)
        self.assertEqual(Kweli-Uongo, 1)
        self.assertIsNot(Kweli-Uongo, Kweli)
        self.assertEqual(Uongo-Kweli, -1)

        self.assertEqual(Kweli*1, 1)
        self.assertEqual(Uongo*1, 0)
        self.assertIsNot(Uongo*1, Uongo)

        self.assertEqual(Kweli/1, 1)
        self.assertIsNot(Kweli/1, Kweli)
        self.assertEqual(Uongo/1, 0)
        self.assertIsNot(Uongo/1, Uongo)

        self.assertEqual(Kweli%1, 0)
        self.assertIsNot(Kweli%1, Uongo)
        self.assertEqual(Kweli%2, 1)
        self.assertIsNot(Kweli%2, Kweli)
        self.assertEqual(Uongo%1, 0)
        self.assertIsNot(Uongo%1, Uongo)

        kila b kwenye Uongo, Kweli:
            kila i kwenye 0, 1, 2:
                self.assertEqual(b**i, int(b)**i)
                self.assertIsNot(b**i, bool(int(b)**i))

        kila a kwenye Uongo, Kweli:
            kila b kwenye Uongo, Kweli:
                self.assertIs(a&b, bool(int(a)&int(b)))
                self.assertIs(a|b, bool(int(a)|int(b)))
                self.assertIs(a^b, bool(int(a)^int(b)))
                self.assertEqual(a&int(b), int(a)&int(b))
                self.assertIsNot(a&int(b), bool(int(a)&int(b)))
                self.assertEqual(a|int(b), int(a)|int(b))
                self.assertIsNot(a|int(b), bool(int(a)|int(b)))
                self.assertEqual(a^int(b), int(a)^int(b))
                self.assertIsNot(a^int(b), bool(int(a)^int(b)))
                self.assertEqual(int(a)&b, int(a)&int(b))
                self.assertIsNot(int(a)&b, bool(int(a)&int(b)))
                self.assertEqual(int(a)|b, int(a)|int(b))
                self.assertIsNot(int(a)|b, bool(int(a)|int(b)))
                self.assertEqual(int(a)^b, int(a)^int(b))
                self.assertIsNot(int(a)^b, bool(int(a)^int(b)))

        self.assertIs(1==1, Kweli)
        self.assertIs(1==0, Uongo)
        self.assertIs(0<1, Kweli)
        self.assertIs(1<0, Uongo)
        self.assertIs(0<=0, Kweli)
        self.assertIs(1<=0, Uongo)
        self.assertIs(1>0, Kweli)
        self.assertIs(1>1, Uongo)
        self.assertIs(1>=1, Kweli)
        self.assertIs(0>=1, Uongo)
        self.assertIs(0!=1, Kweli)
        self.assertIs(0!=0, Uongo)

        x = [1]
        self.assertIs(x ni x, Kweli)
        self.assertIs(x ni sio x, Uongo)

        self.assertIs(1 kwenye x, Kweli)
        self.assertIs(0 kwenye x, Uongo)
        self.assertIs(1 sio kwenye x, Uongo)
        self.assertIs(0 sio kwenye x, Kweli)

        x = {1: 2}
        self.assertIs(x ni x, Kweli)
        self.assertIs(x ni sio x, Uongo)

        self.assertIs(1 kwenye x, Kweli)
        self.assertIs(0 kwenye x, Uongo)
        self.assertIs(1 sio kwenye x, Uongo)
        self.assertIs(0 sio kwenye x, Kweli)

        self.assertIs(not Kweli, Uongo)
        self.assertIs(not Uongo, Kweli)

    eleza test_convert(self):
        self.assertRaises(TypeError, bool, 42, 42)
        self.assertIs(bool(10), Kweli)
        self.assertIs(bool(1), Kweli)
        self.assertIs(bool(-1), Kweli)
        self.assertIs(bool(0), Uongo)
        self.assertIs(bool("hello"), Kweli)
        self.assertIs(bool(""), Uongo)
        self.assertIs(bool(), Uongo)

    eleza test_keyword_args(self):
        ukijumuisha self.assertRaisesRegex(TypeError, 'keyword argument'):
            bool(x=10)

    eleza test_format(self):
        self.assertEqual("%d" % Uongo, "0")
        self.assertEqual("%d" % Kweli, "1")
        self.assertEqual("%x" % Uongo, "0")
        self.assertEqual("%x" % Kweli, "1")

    eleza test_hasattr(self):
        self.assertIs(hasattr([], "append"), Kweli)
        self.assertIs(hasattr([], "wobble"), Uongo)

    eleza test_callable(self):
        self.assertIs(callable(len), Kweli)
        self.assertIs(callable(1), Uongo)

    eleza test_isinstance(self):
        self.assertIs(isinstance(Kweli, bool), Kweli)
        self.assertIs(isinstance(Uongo, bool), Kweli)
        self.assertIs(isinstance(Kweli, int), Kweli)
        self.assertIs(isinstance(Uongo, int), Kweli)
        self.assertIs(isinstance(1, bool), Uongo)
        self.assertIs(isinstance(0, bool), Uongo)

    eleza test_issubclass(self):
        self.assertIs(issubclass(bool, int), Kweli)
        self.assertIs(issubclass(int, bool), Uongo)

    eleza test_contains(self):
        self.assertIs(1 kwenye {}, Uongo)
        self.assertIs(1 kwenye {1:1}, Kweli)

    eleza test_string(self):
        self.assertIs("xyz".endswith("z"), Kweli)
        self.assertIs("xyz".endswith("x"), Uongo)
        self.assertIs("xyz0123".isalnum(), Kweli)
        self.assertIs("@#$%".isalnum(), Uongo)
        self.assertIs("xyz".isalpha(), Kweli)
        self.assertIs("@#$%".isalpha(), Uongo)
        self.assertIs("0123".isdigit(), Kweli)
        self.assertIs("xyz".isdigit(), Uongo)
        self.assertIs("xyz".islower(), Kweli)
        self.assertIs("XYZ".islower(), Uongo)
        self.assertIs("0123".isdecimal(), Kweli)
        self.assertIs("xyz".isdecimal(), Uongo)
        self.assertIs("0123".isnumeric(), Kweli)
        self.assertIs("xyz".isnumeric(), Uongo)
        self.assertIs(" ".isspace(), Kweli)
        self.assertIs("\xa0".isspace(), Kweli)
        self.assertIs("\u3000".isspace(), Kweli)
        self.assertIs("XYZ".isspace(), Uongo)
        self.assertIs("X".istitle(), Kweli)
        self.assertIs("x".istitle(), Uongo)
        self.assertIs("XYZ".isupper(), Kweli)
        self.assertIs("xyz".isupper(), Uongo)
        self.assertIs("xyz".startswith("x"), Kweli)
        self.assertIs("xyz".startswith("z"), Uongo)

    eleza test_boolean(self):
        self.assertEqual(Kweli & 1, 1)
        self.assertNotIsInstance(Kweli & 1, bool)
        self.assertIs(Kweli & Kweli, Kweli)

        self.assertEqual(Kweli | 1, 1)
        self.assertNotIsInstance(Kweli | 1, bool)
        self.assertIs(Kweli | Kweli, Kweli)

        self.assertEqual(Kweli ^ 1, 0)
        self.assertNotIsInstance(Kweli ^ 1, bool)
        self.assertIs(Kweli ^ Kweli, Uongo)

    eleza test_fileclosed(self):
        jaribu:
            ukijumuisha open(support.TESTFN, "w") as f:
                self.assertIs(f.closed, Uongo)
            self.assertIs(f.closed, Kweli)
        mwishowe:
            os.remove(support.TESTFN)

    eleza test_types(self):
        # types are always true.
        kila t kwenye [bool, complex, dict, float, int, list, object,
                  set, str, tuple, type]:
            self.assertIs(bool(t), Kweli)

    eleza test_operator(self):
        agiza operator
        self.assertIs(operator.truth(0), Uongo)
        self.assertIs(operator.truth(1), Kweli)
        self.assertIs(operator.not_(1), Uongo)
        self.assertIs(operator.not_(0), Kweli)
        self.assertIs(operator.contains([], 1), Uongo)
        self.assertIs(operator.contains([1], 1), Kweli)
        self.assertIs(operator.lt(0, 0), Uongo)
        self.assertIs(operator.lt(0, 1), Kweli)
        self.assertIs(operator.is_(Kweli, Kweli), Kweli)
        self.assertIs(operator.is_(Kweli, Uongo), Uongo)
        self.assertIs(operator.is_not(Kweli, Kweli), Uongo)
        self.assertIs(operator.is_not(Kweli, Uongo), Kweli)

    eleza test_marshal(self):
        agiza marshal
        self.assertIs(marshal.loads(marshal.dumps(Kweli)), Kweli)
        self.assertIs(marshal.loads(marshal.dumps(Uongo)), Uongo)

    eleza test_pickle(self):
        agiza pickle
        kila proto kwenye range(pickle.HIGHEST_PROTOCOL + 1):
            self.assertIs(pickle.loads(pickle.dumps(Kweli, proto)), Kweli)
            self.assertIs(pickle.loads(pickle.dumps(Uongo, proto)), Uongo)

    eleza test_picklevalues(self):
        # Test kila specific backwards-compatible pickle values
        agiza pickle
        self.assertEqual(pickle.dumps(Kweli, protocol=0), b"I01\n.")
        self.assertEqual(pickle.dumps(Uongo, protocol=0), b"I00\n.")
        self.assertEqual(pickle.dumps(Kweli, protocol=1), b"I01\n.")
        self.assertEqual(pickle.dumps(Uongo, protocol=1), b"I00\n.")
        self.assertEqual(pickle.dumps(Kweli, protocol=2), b'\x80\x02\x88.')
        self.assertEqual(pickle.dumps(Uongo, protocol=2), b'\x80\x02\x89.')

    eleza test_convert_to_bool(self):
        # Verify that TypeError occurs when bad things are returned
        # kutoka __bool__().  This isn't really a bool test, but
        # it's related.
        check = lambda o: self.assertRaises(TypeError, bool, o)
        kundi Foo(object):
            eleza __bool__(self):
                rudisha self
        check(Foo())

        kundi Bar(object):
            eleza __bool__(self):
                rudisha "Yes"
        check(Bar())

        kundi Baz(int):
            eleza __bool__(self):
                rudisha self
        check(Baz())

        # __bool__() must rudisha a bool sio an int
        kundi Spam(int):
            eleza __bool__(self):
                rudisha 1
        check(Spam())

        kundi Eggs:
            eleza __len__(self):
                rudisha -1
        self.assertRaises(ValueError, bool, Eggs())

    eleza test_from_bytes(self):
        self.assertIs(bool.from_bytes(b'\x00'*8, 'big'), Uongo)
        self.assertIs(bool.from_bytes(b'abcd', 'little'), Kweli)

    eleza test_sane_len(self):
        # this test just tests our assumptions about __len__
        # this will start failing ikiwa __len__ changes assertions
        kila badval kwenye ['illegal', -1, 1 << 32]:
            kundi A:
                eleza __len__(self):
                    rudisha badval
            jaribu:
                bool(A())
            except (Exception) as e_bool:
                jaribu:
                    len(A())
                except (Exception) as e_len:
                    self.assertEqual(str(e_bool), str(e_len))

    eleza test_blocked(self):
        kundi A:
            __bool__ = Tupu
        self.assertRaises(TypeError, bool, A())

        kundi B:
            eleza __len__(self):
                rudisha 10
            __bool__ = Tupu
        self.assertRaises(TypeError, bool, B())

    eleza test_real_and_imag(self):
        self.assertEqual(Kweli.real, 1)
        self.assertEqual(Kweli.imag, 0)
        self.assertIs(type(Kweli.real), int)
        self.assertIs(type(Kweli.imag), int)
        self.assertEqual(Uongo.real, 0)
        self.assertEqual(Uongo.imag, 0)
        self.assertIs(type(Uongo.real), int)
        self.assertIs(type(Uongo.imag), int)

eleza test_main():
    support.run_unittest(BoolTest)

ikiwa __name__ == "__main__":
    test_main()
