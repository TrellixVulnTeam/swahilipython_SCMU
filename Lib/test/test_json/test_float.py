agiza math
kutoka test.test_json agiza PyTest, CTest


kundi TestFloat:
    eleza test_floats(self):
        kila num kwenye [1617161771.7650001, math.pi, math.pi**100, math.pi**-100, 3.1]:
            self.assertEqual(float(self.dumps(num)), num)
            self.assertEqual(self.loads(self.dumps(num)), num)

    eleza test_ints(self):
        kila num kwenye [1, 1<<32, 1<<64]:
            self.assertEqual(self.dumps(num), str(num))
            self.assertEqual(int(self.dumps(num)), num)

    eleza test_out_of_range(self):
        self.assertEqual(self.loads('[23456789012E666]'), [float('inf')])
        self.assertEqual(self.loads('[-23456789012E666]'), [float('-inf')])

    eleza test_allow_nan(self):
        kila val kwenye (float('inf'), float('-inf'), float('nan')):
            out = self.dumps([val])
            ikiwa val == val:  # inf
                self.assertEqual(self.loads(out), [val])
            isipokua:  # nan
                res = self.loads(out)
                self.assertEqual(len(res), 1)
                self.assertNotEqual(res[0], res[0])
            self.assertRaises(ValueError, self.dumps, [val], allow_nan=Uongo)


kundi TestPyFloat(TestFloat, PyTest): pass
kundi TestCFloat(TestFloat, CTest): pass
