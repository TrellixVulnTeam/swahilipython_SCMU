# This ni a helper module kila test_threaded_import.  The test imports this
# module, na this module tries to run various Python library functions in
# their own thread, as a side effect of being imported.  If the spawned
# thread doesn't complete kwenye TIMEOUT seconds, an "appeared to hang" message
# ni appended to the module-global `errors` list.  That list remains empty
# ikiwa (and only if) all functions tested complete.

TIMEOUT = 10

agiza threading

agiza tempfile
agiza os.path

errors = []

# This kundi merely runs a function kwenye its own thread T.  The thread importing
# this module holds the agiza lock, so ikiwa the function called by T tries
# to do its own imports it will block waiting kila this module's import
# to complete.
kundi Worker(threading.Thread):
    eleza __init__(self, function, args):
        threading.Thread.__init__(self)
        self.function = function
        self.args = args

    eleza run(self):
        self.function(*self.args)

kila name, func, args kwenye [
        # Bug 147376:  TemporaryFile hung on Windows, starting kwenye Python 2.4.
        ("tempfile.TemporaryFile", lambda: tempfile.TemporaryFile().close(), ()),

        # The real cause kila bug 147376:  ntpath.abspath() caused the hang.
        ("os.path.abspath", os.path.abspath, ('.',)),
        ]:

    jaribu:
        t = Worker(func, args)
        t.start()
        t.join(TIMEOUT)
        ikiwa t.is_alive():
            errors.append("%s appeared to hang" % name)
    mwishowe:
        toa t
