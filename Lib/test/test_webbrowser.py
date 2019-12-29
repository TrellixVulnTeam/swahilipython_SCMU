agiza webbrowser
agiza unittest
agiza os
agiza sys
agiza subprocess
kutoka unittest agiza mock
kutoka test agiza support


URL = 'http://www.example.com'
CMD_NAME = 'test'


kundi PopenMock(mock.MagicMock):

    eleza poll(self):
        rudisha 0

    eleza wait(self, seconds=Tupu):
        rudisha 0


kundi CommandTestMixin:

    eleza _test(self, meth, *, args=[URL], kw={}, options, arguments):
        """Given a web browser instance method name along ukijumuisha arguments and
        keywords kila same (which defaults to the single argument URL), creates
        a browser instance kutoka the kundi pointed to by self.browser, calls the
        indicated instance method ukijumuisha the indicated arguments, na compares
        the resulting options na arguments pitaed to Popen by the browser
        instance against the 'options' na 'args' lists.  Options are compared
        kwenye a position independent fashion, na the arguments are compared in
        sequence order to whatever ni left over after removing the options.

        """
        popen = PopenMock()
        support.patch(self, subprocess, 'Popen', popen)
        browser = self.browser_class(name=CMD_NAME)
        getattr(browser, meth)(*args, **kw)
        popen_args = subprocess.Popen.call_args[0][0]
        self.assertEqual(popen_args[0], CMD_NAME)
        popen_args.pop(0)
        kila option kwenye options:
            self.assertIn(option, popen_args)
            popen_args.pop(popen_args.index(option))
        self.assertEqual(popen_args, arguments)


kundi GenericBrowserCommandTest(CommandTestMixin, unittest.TestCase):

    browser_kundi = webbrowser.GenericBrowser

    eleza test_open(self):
        self._test('open',
                   options=[],
                   arguments=[URL])


kundi BackgroundBrowserCommandTest(CommandTestMixin, unittest.TestCase):

    browser_kundi = webbrowser.BackgroundBrowser

    eleza test_open(self):
        self._test('open',
                   options=[],
                   arguments=[URL])


kundi ChromeCommandTest(CommandTestMixin, unittest.TestCase):

    browser_kundi = webbrowser.Chrome

    eleza test_open(self):
        self._test('open',
                   options=[],
                   arguments=[URL])

    eleza test_open_with_autoashiria_false(self):
        self._test('open', kw=dict(autoashiria=Uongo),
                   options=[],
                   arguments=[URL])

    eleza test_open_new(self):
        self._test('open_new',
                   options=['--new-window'],
                   arguments=[URL])

    eleza test_open_new_tab(self):
        self._test('open_new_tab',
                   options=[],
                   arguments=[URL])


kundi MozillaCommandTest(CommandTestMixin, unittest.TestCase):

    browser_kundi = webbrowser.Mozilla

    eleza test_open(self):
        self._test('open',
                   options=[],
                   arguments=[URL])

    eleza test_open_with_autoashiria_false(self):
        self._test('open', kw=dict(autoashiria=Uongo),
                   options=[],
                   arguments=[URL])

    eleza test_open_new(self):
        self._test('open_new',
                   options=[],
                   arguments=['-new-window', URL])

    eleza test_open_new_tab(self):
        self._test('open_new_tab',
                   options=[],
                   arguments=['-new-tab', URL])


kundi NetscapeCommandTest(CommandTestMixin, unittest.TestCase):

    browser_kundi = webbrowser.Netscape

    eleza test_open(self):
        self._test('open',
                   options=['-ashiria', '-remote'],
                   arguments=['openURL({})'.format(URL)])

    eleza test_open_with_autoashiria_false(self):
        self._test('open', kw=dict(autoashiria=Uongo),
                   options=['-noashiria', '-remote'],
                   arguments=['openURL({})'.format(URL)])

    eleza test_open_new(self):
        self._test('open_new',
                   options=['-ashiria', '-remote'],
                   arguments=['openURL({},new-window)'.format(URL)])

    eleza test_open_new_tab(self):
        self._test('open_new_tab',
                   options=['-ashiria', '-remote'],
                   arguments=['openURL({},new-tab)'.format(URL)])


kundi GaleonCommandTest(CommandTestMixin, unittest.TestCase):

    browser_kundi = webbrowser.Galeon

    eleza test_open(self):
        self._test('open',
                   options=['-n'],
                   arguments=[URL])

    eleza test_open_with_autoashiria_false(self):
        self._test('open', kw=dict(autoashiria=Uongo),
                   options=['-noashiria', '-n'],
                   arguments=[URL])

    eleza test_open_new(self):
        self._test('open_new',
                   options=['-w'],
                   arguments=[URL])

    eleza test_open_new_tab(self):
        self._test('open_new_tab',
                   options=['-w'],
                   arguments=[URL])


kundi OperaCommandTest(CommandTestMixin, unittest.TestCase):

    browser_kundi = webbrowser.Opera

    eleza test_open(self):
        self._test('open',
                   options=[],
                   arguments=[URL])

    eleza test_open_with_autoashiria_false(self):
        self._test('open', kw=dict(autoashiria=Uongo),
                   options=[],
                   arguments=[URL])

    eleza test_open_new(self):
        self._test('open_new',
                   options=['--new-window'],
                   arguments=[URL])

    eleza test_open_new_tab(self):
        self._test('open_new_tab',
                   options=[],
                   arguments=[URL])


kundi ELinksCommandTest(CommandTestMixin, unittest.TestCase):

    browser_kundi = webbrowser.Elinks

    eleza test_open(self):
        self._test('open', options=['-remote'],
                           arguments=['openURL({})'.format(URL)])

    eleza test_open_with_autoashiria_false(self):
        self._test('open',
                   options=['-remote'],
                   arguments=['openURL({})'.format(URL)])

    eleza test_open_new(self):
        self._test('open_new',
                   options=['-remote'],
                   arguments=['openURL({},new-window)'.format(URL)])

    eleza test_open_new_tab(self):
        self._test('open_new_tab',
                   options=['-remote'],
                   arguments=['openURL({},new-tab)'.format(URL)])


kundi BrowserRegistrationTest(unittest.TestCase):

    eleza setUp(self):
        # Ensure we don't alter the real registered browser details
        self._saved_tryorder = webbrowser._tryorder
        webbrowser._tryorder = []
        self._saved_browsers = webbrowser._browsers
        webbrowser._browsers = {}

    eleza tearDown(self):
        webbrowser._tryorder = self._saved_tryorder
        webbrowser._browsers = self._saved_browsers

    eleza _check_registration(self, preferred):
        kundi ExampleBrowser:
            pita

        expected_tryorder = []
        expected_browsers = {}

        self.assertEqual(webbrowser._tryorder, expected_tryorder)
        self.assertEqual(webbrowser._browsers, expected_browsers)

        webbrowser.register('Example1', ExampleBrowser)
        expected_tryorder = ['Example1']
        expected_browsers['example1'] = [ExampleBrowser, Tupu]
        self.assertEqual(webbrowser._tryorder, expected_tryorder)
        self.assertEqual(webbrowser._browsers, expected_browsers)

        instance = ExampleBrowser()
        ikiwa preferred ni sio Tupu:
            webbrowser.register('example2', ExampleBrowser, instance,
                                preferred=preferred)
        isipokua:
            webbrowser.register('example2', ExampleBrowser, instance)
        ikiwa preferred:
            expected_tryorder = ['example2', 'Example1']
        isipokua:
            expected_tryorder = ['Example1', 'example2']
        expected_browsers['example2'] = [ExampleBrowser, instance]
        self.assertEqual(webbrowser._tryorder, expected_tryorder)
        self.assertEqual(webbrowser._browsers, expected_browsers)

    eleza test_register(self):
        self._check_registration(preferred=Uongo)

    eleza test_register_default(self):
        self._check_registration(preferred=Tupu)

    eleza test_register_preferred(self):
        self._check_registration(preferred=Kweli)


kundi ImportTest(unittest.TestCase):
    eleza test_register(self):
        webbrowser = support.import_fresh_module('webbrowser')
        self.assertIsTupu(webbrowser._tryorder)
        self.assertUongo(webbrowser._browsers)

        kundi ExampleBrowser:
            pita
        webbrowser.register('Example1', ExampleBrowser)
        self.assertKweli(webbrowser._tryorder)
        self.assertEqual(webbrowser._tryorder[-1], 'Example1')
        self.assertKweli(webbrowser._browsers)
        self.assertIn('example1', webbrowser._browsers)
        self.assertEqual(webbrowser._browsers['example1'], [ExampleBrowser, Tupu])

    eleza test_get(self):
        webbrowser = support.import_fresh_module('webbrowser')
        self.assertIsTupu(webbrowser._tryorder)
        self.assertUongo(webbrowser._browsers)

        ukijumuisha self.assertRaises(webbrowser.Error):
            webbrowser.get('fakebrowser')
        self.assertIsNotTupu(webbrowser._tryorder)

    eleza test_synthesize(self):
        webbrowser = support.import_fresh_module('webbrowser')
        name = os.path.basename(sys.executable).lower()
        webbrowser.register(name, Tupu, webbrowser.GenericBrowser(name))
        webbrowser.get(sys.executable)

    eleza test_environment(self):
        webbrowser = support.import_fresh_module('webbrowser')
        jaribu:
            browser = webbrowser.get().name
        tatizo (webbrowser.Error, AttributeError) kama err:
            self.skipTest(str(err))
        ukijumuisha support.EnvironmentVarGuard() kama env:
            env["BROWSER"] = browser
            webbrowser = support.import_fresh_module('webbrowser')
            webbrowser.get()

    eleza test_environment_preferred(self):
        webbrowser = support.import_fresh_module('webbrowser')
        jaribu:
            webbrowser.get()
            least_preferred_browser = webbrowser.get(webbrowser._tryorder[-1]).name
        tatizo (webbrowser.Error, AttributeError, IndexError) kama err:
            self.skipTest(str(err))

        ukijumuisha support.EnvironmentVarGuard() kama env:
            env["BROWSER"] = least_preferred_browser
            webbrowser = support.import_fresh_module('webbrowser')
            self.assertEqual(webbrowser.get().name, least_preferred_browser)

        ukijumuisha support.EnvironmentVarGuard() kama env:
            env["BROWSER"] = sys.executable
            webbrowser = support.import_fresh_module('webbrowser')
            self.assertEqual(webbrowser.get().name, sys.executable)


ikiwa __name__=='__main__':
    unittest.main()
