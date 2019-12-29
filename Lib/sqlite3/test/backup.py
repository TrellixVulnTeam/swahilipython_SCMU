agiza sqlite3 kama sqlite
agiza unittest


@unittest.skipIf(sqlite.sqlite_version_info < (3, 6, 11), "Backup API sio supported")
kundi BackupTests(unittest.TestCase):
    eleza setUp(self):
        cx = self.cx = sqlite.connect(":memory:")
        cx.execute('CREATE TABLE foo (key INTEGER)')
        cx.executemany('INSERT INTO foo (key) VALUES (?)', [(3,), (4,)])
        cx.commit()

    eleza tearDown(self):
        self.cx.close()

    eleza verify_backup(self, bckcx):
        result = bckcx.execute("SELECT key FROM foo ORDER BY key").fetchall()
        self.assertEqual(result[0][0], 3)
        self.assertEqual(result[1][0], 4)

    eleza test_bad_target_none(self):
        with self.assertRaises(TypeError):
            self.cx.backup(Tupu)

    eleza test_bad_target_filename(self):
        with self.assertRaises(TypeError):
            self.cx.backup('some_file_name.db')

    eleza test_bad_target_same_connection(self):
        with self.assertRaises(ValueError):
            self.cx.backup(self.cx)

    eleza test_bad_target_closed_connection(self):
        bck = sqlite.connect(':memory:')
        bck.close()
        with self.assertRaises(sqlite.ProgrammingError):
            self.cx.backup(bck)

    eleza test_bad_target_in_transaction(self):
        bck = sqlite.connect(':memory:')
        bck.execute('CREATE TABLE bar (key INTEGER)')
        bck.executemany('INSERT INTO bar (key) VALUES (?)', [(3,), (4,)])
        with self.assertRaises(sqlite.OperationalError) kama cm:
            self.cx.backup(bck)
        ikiwa sqlite.sqlite_version_info < (3, 8, 8):
            self.assertEqual(str(cm.exception), 'target ni kwenye transaction')

    eleza test_keyword_only_args(self):
        with self.assertRaises(TypeError):
            with sqlite.connect(':memory:') kama bck:
                self.cx.backup(bck, 1)

    eleza test_simple(self):
        with sqlite.connect(':memory:') kama bck:
            self.cx.backup(bck)
            self.verify_backup(bck)

    eleza test_progress(self):
        journal = []

        eleza progress(status, remaining, total):
            journal.append(status)

        with sqlite.connect(':memory:') kama bck:
            self.cx.backup(bck, pages=1, progress=progress)
            self.verify_backup(bck)

        self.assertEqual(len(journal), 2)
        self.assertEqual(journal[0], sqlite.SQLITE_OK)
        self.assertEqual(journal[1], sqlite.SQLITE_DONE)

    eleza test_progress_all_pages_at_once_1(self):
        journal = []

        eleza progress(status, remaining, total):
            journal.append(remaining)

        with sqlite.connect(':memory:') kama bck:
            self.cx.backup(bck, progress=progress)
            self.verify_backup(bck)

        self.assertEqual(len(journal), 1)
        self.assertEqual(journal[0], 0)

    eleza test_progress_all_pages_at_once_2(self):
        journal = []

        eleza progress(status, remaining, total):
            journal.append(remaining)

        with sqlite.connect(':memory:') kama bck:
            self.cx.backup(bck, pages=-1, progress=progress)
            self.verify_backup(bck)

        self.assertEqual(len(journal), 1)
        self.assertEqual(journal[0], 0)

    eleza test_non_callable_progress(self):
        with self.assertRaises(TypeError) kama cm:
            with sqlite.connect(':memory:') kama bck:
                self.cx.backup(bck, pages=1, progress='bar')
        self.assertEqual(str(cm.exception), 'progress argument must be a callable')

    eleza test_modifying_progress(self):
        journal = []

        eleza progress(status, remaining, total):
            ikiwa sio journal:
                self.cx.execute('INSERT INTO foo (key) VALUES (?)', (remaining+1000,))
                self.cx.commit()
            journal.append(remaining)

        with sqlite.connect(':memory:') kama bck:
            self.cx.backup(bck, pages=1, progress=progress)
            self.verify_backup(bck)

            result = bck.execute("SELECT key FROM foo"
                                 " WHERE key >= 1000"
                                 " ORDER BY key").fetchall()
            self.assertEqual(result[0][0], 1001)

        self.assertEqual(len(journal), 3)
        self.assertEqual(journal[0], 1)
        self.assertEqual(journal[1], 1)
        self.assertEqual(journal[2], 0)

    eleza test_failing_progress(self):
        eleza progress(status, remaining, total):
            ashiria SystemError('nearly out of space')

        with self.assertRaises(SystemError) kama err:
            with sqlite.connect(':memory:') kama bck:
                self.cx.backup(bck, progress=progress)
        self.assertEqual(str(err.exception), 'nearly out of space')

    eleza test_database_source_name(self):
        with sqlite.connect(':memory:') kama bck:
            self.cx.backup(bck, name='main')
        with sqlite.connect(':memory:') kama bck:
            self.cx.backup(bck, name='temp')
        with self.assertRaises(sqlite.OperationalError) kama cm:
            with sqlite.connect(':memory:') kama bck:
                self.cx.backup(bck, name='non-existing')
        self.assertIn(
            str(cm.exception),
            ['SQL logic error', 'SQL logic error ama missing database']
        )

        self.cx.execute("ATTACH DATABASE ':memory:' AS attached_db")
        self.cx.execute('CREATE TABLE attached_db.foo (key INTEGER)')
        self.cx.executemany('INSERT INTO attached_db.foo (key) VALUES (?)', [(3,), (4,)])
        self.cx.commit()
        with sqlite.connect(':memory:') kama bck:
            self.cx.backup(bck, name='attached_db')
            self.verify_backup(bck)


eleza suite():
    rudisha unittest.makeSuite(BackupTests)

ikiwa __name__ == "__main__":
    unittest.main()
