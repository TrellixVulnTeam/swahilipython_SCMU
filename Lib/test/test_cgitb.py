kutoka test.support agiza temp_dir
kutoka test.support.script_helper agiza assert_python_failure
agiza unittest
agiza sys
agiza cgitb

kundi TestCgitb(unittest.TestCase):

    eleza test_fonts(self):
        text = "Hello Robbie!"
        self.assertEqual(cgitb.small(text), "<small>{}</small>".format(text))
        self.assertEqual(cgitb.strong(text), "<strong>{}</strong>".format(text))
        self.assertEqual(cgitb.grey(text),
                         '<font color="#909090">{}</font>'.format(text))

    eleza test_blanks(self):
        self.assertEqual(cgitb.small(""), "")
        self.assertEqual(cgitb.strong(""), "")
        self.assertEqual(cgitb.grey(""), "")

    eleza test_html(self):
        jaribu:
            ashiria ValueError("Hello World")
        tatizo ValueError kama err:
            # If the html was templated we could do a bit more here.
            # At least check that we get details on what we just ashiriad.
            html = cgitb.html(sys.exc_info())
            self.assertIn("ValueError", html)
            self.assertIn(str(err), html)

    eleza test_text(self):
        jaribu:
            ashiria ValueError("Hello World")
        tatizo ValueError kama err:
            text = cgitb.text(sys.exc_info())
            self.assertIn("ValueError", text)
            self.assertIn("Hello World", text)

    eleza test_syshook_no_logdir_default_format(self):
        ukijumuisha temp_dir() kama tracedir:
            rc, out, err = assert_python_failure(
                  '-c',
                  ('agiza cgitb; cgitb.enable(logdir=%s); '
                   'ashiria ValueError("Hello World")') % repr(tracedir))
        out = out.decode(sys.getfilesystemencoding())
        self.assertIn("ValueError", out)
        self.assertIn("Hello World", out)
        self.assertIn("<strong>&lt;module&gt;</strong>", out)
        # By default we emit HTML markup.
        self.assertIn('<p>', out)
        self.assertIn('</p>', out)

    eleza test_syshook_no_logdir_text_format(self):
        # Issue 12890: we were emitting the <p> tag kwenye text mode.
        ukijumuisha temp_dir() kama tracedir:
            rc, out, err = assert_python_failure(
                  '-c',
                  ('agiza cgitb; cgitb.enable(format="text", logdir=%s); '
                   'ashiria ValueError("Hello World")') % repr(tracedir))
        out = out.decode(sys.getfilesystemencoding())
        self.assertIn("ValueError", out)
        self.assertIn("Hello World", out)
        self.assertNotIn('<p>', out)
        self.assertNotIn('</p>', out)


ikiwa __name__ == "__main__":
    unittest.main()
