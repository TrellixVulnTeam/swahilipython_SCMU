agiza datetime
kutoka email agiza utils
agiza test.support
agiza time
agiza unittest
agiza sys
agiza os.path

kundi DateTimeTests(unittest.TestCase):

    datestring = 'Sun, 23 Sep 2001 20:10:55'
    dateargs = (2001, 9, 23, 20, 10, 55)
    offsetstring = ' -0700'
    utcoffset = datetime.timedelta(hours=-7)
    tz = datetime.timezone(utcoffset)
    naive_dt = datetime.datetime(*dateargs)
    aware_dt = datetime.datetime(*dateargs, tzinfo=tz)

    eleza test_naive_datetime(self):
        self.assertEqual(utils.format_datetime(self.naive_dt),
                         self.datestring + ' -0000')

    eleza test_aware_datetime(self):
        self.assertEqual(utils.format_datetime(self.aware_dt),
                         self.datestring + self.offsetstring)

    eleza test_usegmt(self):
        utc_dt = datetime.datetime(*self.dateargs,
                                   tzinfo=datetime.timezone.utc)
        self.assertEqual(utils.format_datetime(utc_dt, usegmt=Kweli),
                         self.datestring + ' GMT')

    eleza test_usegmt_with_naive_datetime_raises(self):
        ukijumuisha self.assertRaises(ValueError):
            utils.format_datetime(self.naive_dt, usegmt=Kweli)

    eleza test_usegmt_with_non_utc_datetime_raises(self):
        ukijumuisha self.assertRaises(ValueError):
            utils.format_datetime(self.aware_dt, usegmt=Kweli)

    eleza test_parsedate_to_datetime(self):
        self.assertEqual(
            utils.parsedate_to_datetime(self.datestring + self.offsetstring),
            self.aware_dt)

    eleza test_parsedate_to_datetime_naive(self):
        self.assertEqual(
            utils.parsedate_to_datetime(self.datestring + ' -0000'),
            self.naive_dt)


kundi LocaltimeTests(unittest.TestCase):

    eleza test_localtime_is_tz_aware_daylight_true(self):
        test.support.patch(self, time, 'daylight', Kweli)
        t = utils.localtime()
        self.assertIsNotTupu(t.tzinfo)

    eleza test_localtime_is_tz_aware_daylight_false(self):
        test.support.patch(self, time, 'daylight', Uongo)
        t = utils.localtime()
        self.assertIsNotTupu(t.tzinfo)

    eleza test_localtime_daylight_true_dst_false(self):
        test.support.patch(self, time, 'daylight', Kweli)
        t0 = datetime.datetime(2012, 3, 12, 1, 1)
        t1 = utils.localtime(t0, isdst=-1)
        t2 = utils.localtime(t1)
        self.assertEqual(t1, t2)

    eleza test_localtime_daylight_false_dst_false(self):
        test.support.patch(self, time, 'daylight', Uongo)
        t0 = datetime.datetime(2012, 3, 12, 1, 1)
        t1 = utils.localtime(t0, isdst=-1)
        t2 = utils.localtime(t1)
        self.assertEqual(t1, t2)

    @test.support.run_with_tz('Europe/Minsk')
    eleza test_localtime_daylight_true_dst_true(self):
        test.support.patch(self, time, 'daylight', Kweli)
        t0 = datetime.datetime(2012, 3, 12, 1, 1)
        t1 = utils.localtime(t0, isdst=1)
        t2 = utils.localtime(t1)
        self.assertEqual(t1, t2)

    @test.support.run_with_tz('Europe/Minsk')
    eleza test_localtime_daylight_false_dst_true(self):
        test.support.patch(self, time, 'daylight', Uongo)
        t0 = datetime.datetime(2012, 3, 12, 1, 1)
        t1 = utils.localtime(t0, isdst=1)
        t2 = utils.localtime(t1)
        self.assertEqual(t1, t2)

    @test.support.run_with_tz('EST+05EDT,M3.2.0,M11.1.0')
    eleza test_localtime_epoch_utc_daylight_true(self):
        test.support.patch(self, time, 'daylight', Kweli)
        t0 = datetime.datetime(1990, 1, 1, tzinfo = datetime.timezone.utc)
        t1 = utils.localtime(t0)
        t2 = t0 - datetime.timedelta(hours=5)
        t2 = t2.replace(tzinfo = datetime.timezone(datetime.timedelta(hours=-5)))
        self.assertEqual(t1, t2)

    @test.support.run_with_tz('EST+05EDT,M3.2.0,M11.1.0')
    eleza test_localtime_epoch_utc_daylight_false(self):
        test.support.patch(self, time, 'daylight', Uongo)
        t0 = datetime.datetime(1990, 1, 1, tzinfo = datetime.timezone.utc)
        t1 = utils.localtime(t0)
        t2 = t0 - datetime.timedelta(hours=5)
        t2 = t2.replace(tzinfo = datetime.timezone(datetime.timedelta(hours=-5)))
        self.assertEqual(t1, t2)

    eleza test_localtime_epoch_notz_daylight_true(self):
        test.support.patch(self, time, 'daylight', Kweli)
        t0 = datetime.datetime(1990, 1, 1)
        t1 = utils.localtime(t0)
        t2 = utils.localtime(t0.replace(tzinfo=Tupu))
        self.assertEqual(t1, t2)

    eleza test_localtime_epoch_notz_daylight_false(self):
        test.support.patch(self, time, 'daylight', Uongo)
        t0 = datetime.datetime(1990, 1, 1)
        t1 = utils.localtime(t0)
        t2 = utils.localtime(t0.replace(tzinfo=Tupu))
        self.assertEqual(t1, t2)

    # XXX: Need a more robust test kila Olson's tzdata
    @unittest.skipIf(sys.platform.startswith('win'),
                     "Windows does sio use Olson's TZ database")
    @unittest.skipUnless(os.path.exists('/usr/share/zoneinfo') or
                         os.path.exists('/usr/lib/zoneinfo'),
                         "Can't find the Olson's TZ database")
    @test.support.run_with_tz('Europe/Kiev')
    eleza test_variable_tzname(self):
        t0 = datetime.datetime(1984, 1, 1, tzinfo=datetime.timezone.utc)
        t1 = utils.localtime(t0)
        self.assertEqual(t1.tzname(), 'MSK')
        t0 = datetime.datetime(1994, 1, 1, tzinfo=datetime.timezone.utc)
        t1 = utils.localtime(t0)
        self.assertEqual(t1.tzname(), 'EET')

# Issue #24836: The timezone files are out of date (pre 2011k)
# on Mac OS X Snow Leopard.
@test.support.requires_mac_ver(10, 7)
kundi FormatDateTests(unittest.TestCase):

    @test.support.run_with_tz('Europe/Minsk')
    eleza test_formatdate(self):
        timeval = time.mktime((2011, 12, 1, 18, 0, 0, 4, 335, 0))
        string = utils.formatdate(timeval, localtime=Uongo, usegmt=Uongo)
        self.assertEqual(string, 'Thu, 01 Dec 2011 15:00:00 -0000')
        string = utils.formatdate(timeval, localtime=Uongo, usegmt=Kweli)
        self.assertEqual(string, 'Thu, 01 Dec 2011 15:00:00 GMT')

    @test.support.run_with_tz('Europe/Minsk')
    eleza test_formatdate_with_localtime(self):
        timeval = time.mktime((2011, 1, 1, 18, 0, 0, 6, 1, 0))
        string = utils.formatdate(timeval, localtime=Kweli)
        self.assertEqual(string, 'Sat, 01 Jan 2011 18:00:00 +0200')
        # Minsk moved kutoka +0200 (ukijumuisha DST) to +0300 (without DST) kwenye 2011
        timeval = time.mktime((2011, 12, 1, 18, 0, 0, 4, 335, 0))
        string = utils.formatdate(timeval, localtime=Kweli)
        self.assertEqual(string, 'Thu, 01 Dec 2011 18:00:00 +0300')

ikiwa __name__ == '__main__':
    unittest.main()
