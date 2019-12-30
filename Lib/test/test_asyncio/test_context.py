agiza asyncio
agiza decimal
agiza unittest


eleza tearDownModule():
    asyncio.set_event_loop_policy(Tupu)


kundi DecimalContextTest(unittest.TestCase):

    eleza test_asyncio_task_decimal_context(self):
        async eleza fractions(t, precision, x, y):
            ukijumuisha decimal.localcontext() as ctx:
                ctx.prec = precision
                a = decimal.Decimal(x) / decimal.Decimal(y)
                await asyncio.sleep(t)
                b = decimal.Decimal(x) / decimal.Decimal(y ** 2)
                rudisha a, b

        async eleza main():
            r1, r2 = await asyncio.gather(
                fractions(0.1, 3, 1, 3), fractions(0.2, 6, 1, 3))

            rudisha r1, r2

        r1, r2 = asyncio.run(main())

        self.assertEqual(str(r1[0]), '0.333')
        self.assertEqual(str(r1[1]), '0.111')

        self.assertEqual(str(r2[0]), '0.333333')
        self.assertEqual(str(r2[1]), '0.111111')
