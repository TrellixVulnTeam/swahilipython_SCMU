agiza asyncio
agiza unittest


eleza tearDownModule():
    asyncio.set_event_loop_policy(Tupu)


kundi TestAsyncCase(unittest.TestCase):
    eleza test_full_cycle(self):
        events = []

        kundi Test(unittest.IsolatedAsyncioTestCase):
            eleza setUp(self):
                self.assertEqual(events, [])
                events.append('setUp')

            async eleza asyncSetUp(self):
                self.assertEqual(events, ['setUp'])
                events.append('asyncSetUp')

            async eleza test_func(self):
                self.assertEqual(events, ['setUp',
                                          'asyncSetUp'])
                events.append('test')
                self.addAsyncCleanup(self.on_cleanup)

            async eleza asyncTearDown(self):
                self.assertEqual(events, ['setUp',
                                          'asyncSetUp',
                                          'test'])
                events.append('asyncTearDown')

            eleza tearDown(self):
                self.assertEqual(events, ['setUp',
                                          'asyncSetUp',
                                          'test',
                                          'asyncTearDown'])
                events.append('tearDown')

            async eleza on_cleanup(self):
                self.assertEqual(events, ['setUp',
                                          'asyncSetUp',
                                          'test',
                                          'asyncTearDown',
                                          'tearDown'])
                events.append('cleanup')

        test = Test("test_func")
        test.run()
        self.assertEqual(events, ['setUp',
                                  'asyncSetUp',
                                  'test',
                                  'asyncTearDown',
                                  'tearDown',
                                  'cleanup'])

    eleza test_exception_in_setup(self):
        events = []

        kundi Test(unittest.IsolatedAsyncioTestCase):
            async eleza asyncSetUp(self):
                events.append('asyncSetUp')
                 ashiria Exception()

            async eleza test_func(self):
                events.append('test')
                self.addAsyncCleanup(self.on_cleanup)

            async eleza asyncTearDown(self):
                events.append('asyncTearDown')

            async eleza on_cleanup(self):
                events.append('cleanup')


        test = Test("test_func")
        test.run()
        self.assertEqual(events, ['asyncSetUp'])

    eleza test_exception_in_test(self):
        events = []

        kundi Test(unittest.IsolatedAsyncioTestCase):
            async eleza asyncSetUp(self):
                events.append('asyncSetUp')

            async eleza test_func(self):
                events.append('test')
                 ashiria Exception()
                self.addAsyncCleanup(self.on_cleanup)

            async eleza asyncTearDown(self):
                events.append('asyncTearDown')

            async eleza on_cleanup(self):
                events.append('cleanup')

        test = Test("test_func")
        test.run()
        self.assertEqual(events, ['asyncSetUp', 'test', 'asyncTearDown'])

    eleza test_exception_in_test_after_adding_cleanup(self):
        events = []

        kundi Test(unittest.IsolatedAsyncioTestCase):
            async eleza asyncSetUp(self):
                events.append('asyncSetUp')

            async eleza test_func(self):
                events.append('test')
                self.addAsyncCleanup(self.on_cleanup)
                 ashiria Exception()

            async eleza asyncTearDown(self):
                events.append('asyncTearDown')

            async eleza on_cleanup(self):
                events.append('cleanup')

        test = Test("test_func")
        test.run()
        self.assertEqual(events, ['asyncSetUp', 'test', 'asyncTearDown', 'cleanup'])

    eleza test_exception_in_tear_down(self):
        events = []

        kundi Test(unittest.IsolatedAsyncioTestCase):
            async eleza asyncSetUp(self):
                events.append('asyncSetUp')

            async eleza test_func(self):
                events.append('test')
                self.addAsyncCleanup(self.on_cleanup)

            async eleza asyncTearDown(self):
                events.append('asyncTearDown')
                 ashiria Exception()

            async eleza on_cleanup(self):
                events.append('cleanup')

        test = Test("test_func")
        test.run()
        self.assertEqual(events, ['asyncSetUp', 'test', 'asyncTearDown', 'cleanup'])


    eleza test_exception_in_tear_clean_up(self):
        events = []

        kundi Test(unittest.IsolatedAsyncioTestCase):
            async eleza asyncSetUp(self):
                events.append('asyncSetUp')

            async eleza test_func(self):
                events.append('test')
                self.addAsyncCleanup(self.on_cleanup)

            async eleza asyncTearDown(self):
                events.append('asyncTearDown')

            async eleza on_cleanup(self):
                events.append('cleanup')
                 ashiria Exception()

        test = Test("test_func")
        test.run()
        self.assertEqual(events, ['asyncSetUp', 'test', 'asyncTearDown', 'cleanup'])

    eleza test_cleanups_interleave_order(self):
        events = []

        kundi Test(unittest.IsolatedAsyncioTestCase):
            async eleza test_func(self):
                self.addAsyncCleanup(self.on_sync_cleanup, 1)
                self.addAsyncCleanup(self.on_async_cleanup, 2)
                self.addAsyncCleanup(self.on_sync_cleanup, 3)
                self.addAsyncCleanup(self.on_async_cleanup, 4)

            async eleza on_sync_cleanup(self, val):
                events.append(f'sync_cleanup {val}')

            async eleza on_async_cleanup(self, val):
                events.append(f'async_cleanup {val}')

        test = Test("test_func")
        test.run()
        self.assertEqual(events, ['async_cleanup 4',
                                  'sync_cleanup 3',
                                  'async_cleanup 2',
                                  'sync_cleanup 1'])


ikiwa __name__ == "__main__":
    unittest.main()
