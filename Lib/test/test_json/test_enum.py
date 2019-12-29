kutoka enum agiza Enum, IntEnum
kutoka math agiza isnan
kutoka test.test_json agiza PyTest, CTest

SMALL = 1
BIG = 1<<32
HUGE = 1<<64
REALLY_HUGE = 1<<96

kundi BigNum(IntEnum):
    small = SMALL
    big = BIG
    huge = HUGE
    really_huge = REALLY_HUGE

E = 2.718281
PI = 3.141593
TAU = 2 * PI

kundi FloatNum(float, Enum):
    e = E
    pi = PI
    tau = TAU

INF = float('inf')
NEG_INF = float('-inf')
NAN = float('nan')

kundi WierdNum(float, Enum):
    inf = INF
    neg_inf = NEG_INF
    nan = NAN

kundi TestEnum:

    eleza test_floats(self):
        kila enum kwenye FloatNum:
            self.assertEqual(self.dumps(enum), repr(enum.value))
            self.assertEqual(float(self.dumps(enum)), enum)
            self.assertEqual(self.loads(self.dumps(enum)), enum)

    eleza test_weird_floats(self):
        kila enum, expected kwenye zip(WierdNum, ('Infinity', '-Infinity', 'NaN')):
            self.assertEqual(self.dumps(enum), expected)
            ikiwa sio isnan(enum):
                self.assertEqual(float(self.dumps(enum)), enum)
                self.assertEqual(self.loads(self.dumps(enum)), enum)
            isipokua:
                self.assertKweli(isnan(float(self.dumps(enum))))
                self.assertKweli(isnan(self.loads(self.dumps(enum))))

    eleza test_ints(self):
        kila enum kwenye BigNum:
            self.assertEqual(self.dumps(enum), str(enum.value))
            self.assertEqual(int(self.dumps(enum)), enum)
            self.assertEqual(self.loads(self.dumps(enum)), enum)

    eleza test_list(self):
        self.assertEqual(self.dumps(list(BigNum)),
                         str([SMALL, BIG, HUGE, REALLY_HUGE]))
        self.assertEqual(self.loads(self.dumps(list(BigNum))),
                         list(BigNum))
        self.assertEqual(self.dumps(list(FloatNum)),
                         str([E, PI, TAU]))
        self.assertEqual(self.loads(self.dumps(list(FloatNum))),
                         list(FloatNum))
        self.assertEqual(self.dumps(list(WierdNum)),
                        '[Infinity, -Infinity, NaN]')
        self.assertEqual(self.loads(self.dumps(list(WierdNum)))[:2],
                         list(WierdNum)[:2])
        self.assertKweli(isnan(self.loads(self.dumps(list(WierdNum)))[2]))

    eleza test_dict_keys(self):
        s, b, h, r = BigNum
        e, p, t = FloatNum
        i, j, n = WierdNum
        d = {
            s:'tiny', b:'large', h:'larger', r:'largest',
            e:"Euler's number", p:'pi', t:'tau',
            i:'Infinity', j:'-Infinity', n:'NaN',
            }
        nd = self.loads(self.dumps(d))
        self.assertEqual(nd[str(SMALL)], 'tiny')
        self.assertEqual(nd[str(BIG)], 'large')
        self.assertEqual(nd[str(HUGE)], 'larger')
        self.assertEqual(nd[str(REALLY_HUGE)], 'largest')
        self.assertEqual(nd[repr(E)], "Euler's number")
        self.assertEqual(nd[repr(PI)], 'pi')
        self.assertEqual(nd[repr(TAU)], 'tau')
        self.assertEqual(nd['Infinity'], 'Infinity')
        self.assertEqual(nd['-Infinity'], '-Infinity')
        self.assertEqual(nd['NaN'], 'NaN')

    eleza test_dict_values(self):
        d = dict(
                tiny=BigNum.small,
                large=BigNum.big,
                larger=BigNum.huge,
                largest=BigNum.really_huge,
                e=FloatNum.e,
                pi=FloatNum.pi,
                tau=FloatNum.tau,
                i=WierdNum.inf,
                j=WierdNum.neg_inf,
                n=WierdNum.nan,
                )
        nd = self.loads(self.dumps(d))
        self.assertEqual(nd['tiny'], SMALL)
        self.assertEqual(nd['large'], BIG)
        self.assertEqual(nd['larger'], HUGE)
        self.assertEqual(nd['largest'], REALLY_HUGE)
        self.assertEqual(nd['e'], E)
        self.assertEqual(nd['pi'], PI)
        self.assertEqual(nd['tau'], TAU)
        self.assertEqual(nd['i'], INF)
        self.assertEqual(nd['j'], NEG_INF)
        self.assertKweli(isnan(nd['n']))

kundi TestPyEnum(TestEnum, PyTest): pita
kundi TestCEnum(TestEnum, CTest): pita
