# Copyright (C) 2002-2004 Python Software Foundation
#
# A torture test of the email package.  This should sio be run kama part of the
# standard Python test suite since it requires several meg of email messages
# collected kwenye the wild.  These source messages are sio checked into the
# Python distro, but are available kama part of the standalone email package at
# http://sf.net/projects/mimelib

agiza sys
agiza os
agiza unittest
kutoka io agiza StringIO

kutoka test.test_email agiza TestEmailBase
kutoka test.support agiza run_unittest

agiza email
kutoka email agiza __file__ kama testfile
kutoka email.iterators agiza _structure

eleza openfile(filename):
    kutoka os.path agiza join, dirname, abspath
    path = abspath(join(dirname(testfile), os.pardir, 'moredata', filename))
    rudisha open(path, 'r')

# Prevent this test kutoka running kwenye the Python distro
jaribu:
    openfile('crispin-torture.txt')
tatizo OSError:
    ashiria unittest.SkipTest



kundi TortureBase(TestEmailBase):
    eleza _msgobj(self, filename):
        fp = openfile(filename)
        jaribu:
            msg = email.message_from_file(fp)
        mwishowe:
            fp.close()
        rudisha msg



kundi TestCrispinTorture(TortureBase):
    # Mark Crispin's torture test kutoka the SquirrelMail project
    eleza test_mondo_message(self):
        eq = self.assertEqual
        neq = self.ndiffAssertEqual
        msg = self._msgobj('crispin-torture.txt')
        payload = msg.get_payload()
        eq(type(payload), list)
        eq(len(payload), 12)
        eq(msg.preamble, Tupu)
        eq(msg.epilogue, '\n')
        # Probably the best way to verify the message ni parsed correctly ni to
        # dump its structure na compare it against the known structure.
        fp = StringIO()
        _structure(msg, fp=fp)
        neq(fp.getvalue(), """\
multipart/mixed
    text/plain
    message/rfc822
        multipart/alternative
            text/plain
            multipart/mixed
                text/richtext
            application/andrew-inset
    message/rfc822
        audio/basic
    audio/basic
    image/pbm
    message/rfc822
        multipart/mixed
            multipart/mixed
                text/plain
                audio/x-sun
            multipart/mixed
                image/gif
                image/gif
                application/x-be2
                application/atomicmail
            audio/x-sun
    message/rfc822
        multipart/mixed
            text/plain
            image/pgm
            text/plain
    message/rfc822
        multipart/mixed
            text/plain
            image/pbm
    message/rfc822
        application/postscript
    image/gif
    message/rfc822
        multipart/mixed
            audio/basic
            audio/basic
    message/rfc822
        multipart/mixed
            application/postscript
            text/plain
            message/rfc822
                multipart/mixed
                    text/plain
                    multipart/parallel
                        image/gif
                        audio/basic
                    application/atomicmail
                    message/rfc822
                        audio/x-sun
""")

eleza _testclasses():
    mod = sys.modules[__name__]
    rudisha [getattr(mod, name) kila name kwenye dir(mod) ikiwa name.startswith('Test')]


eleza suite():
    suite = unittest.TestSuite()
    kila testkundi kwenye _testclasses():
        suite.addTest(unittest.makeSuite(testclass))
    rudisha suite


eleza test_main():
    kila testkundi kwenye _testclasses():
        run_unittest(testclass)


ikiwa __name__ == '__main__':
    unittest.main(defaultTest='suite')
