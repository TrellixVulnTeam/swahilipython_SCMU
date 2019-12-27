
kutoka test agiza support
syslog = support.import_module("syslog") #skip ikiwa not supported
agiza unittest

# XXX(nnorwitz): This test sucks.  I don't know of a platform independent way
# to verify that the messages were really logged.
# The only purpose of this test is to verify the code doesn't crash or leak.

kundi Test(unittest.TestCase):

    eleza test_openlog(self):
        syslog.openlog('python')
        # Issue #6697.
        self.assertRaises(UnicodeEncodeError, syslog.openlog, '\uD800')

    eleza test_syslog(self):
        syslog.openlog('python')
        syslog.syslog('test message kutoka python test_syslog')
        syslog.syslog(syslog.LOG_ERR, 'test error kutoka python test_syslog')

    eleza test_closelog(self):
        syslog.openlog('python')
        syslog.closelog()

    eleza test_setlogmask(self):
        syslog.setlogmask(syslog.LOG_DEBUG)

    eleza test_log_mask(self):
        syslog.LOG_MASK(syslog.LOG_INFO)

    eleza test_log_upto(self):
        syslog.LOG_UPTO(syslog.LOG_INFO)

    eleza test_openlog_noargs(self):
        syslog.openlog()
        syslog.syslog('test message kutoka python test_syslog')

ikiwa __name__ == "__main__":
    unittest.main()
