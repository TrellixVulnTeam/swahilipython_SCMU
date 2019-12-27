#! /usr/bin/env python3
"""Interfaces for launching and remotely controlling Web browsers."""
# Maintained by Georg Brandl.

agiza os
agiza shlex
agiza shutil
agiza sys
agiza subprocess
agiza threading

__all__ = ["Error", "open", "open_new", "open_new_tab", "get", "register"]

kundi Error(Exception):
    pass

_lock = threading.RLock()
_browsers = {}                  # Dictionary of available browser controllers
_tryorder = None                # Preference order of available browsers
_os_preferred_browser = None    # The preferred browser

eleza register(name, klass, instance=None, *, preferred=False):
    """Register a browser connector."""
    with _lock:
        ikiwa _tryorder is None:
            register_standard_browsers()
        _browsers[name.lower()] = [klass, instance]

        # Preferred browsers go to the front of the list.
        # Need to match to the default browser returned by xdg-settings, which
        # may be of the form e.g. "firefox.desktop".
        ikiwa preferred or (_os_preferred_browser and name in _os_preferred_browser):
            _tryorder.insert(0, name)
        else:
            _tryorder.append(name)

eleza get(using=None):
    """Return a browser launcher instance appropriate for the environment."""
    ikiwa _tryorder is None:
        with _lock:
            ikiwa _tryorder is None:
                register_standard_browsers()
    ikiwa using is not None:
        alternatives = [using]
    else:
        alternatives = _tryorder
    for browser in alternatives:
        ikiwa '%s' in browser:
            # User gave us a command line, split it into name and args
            browser = shlex.split(browser)
            ikiwa browser[-1] == '&':
                rudisha BackgroundBrowser(browser[:-1])
            else:
                rudisha GenericBrowser(browser)
        else:
            # User gave us a browser name or path.
            try:
                command = _browsers[browser.lower()]
            except KeyError:
                command = _synthesize(browser)
            ikiwa command[1] is not None:
                rudisha command[1]
            elikiwa command[0] is not None:
                rudisha command[0]()
    raise Error("could not locate runnable browser")

# Please note: the following definition hides a builtin function.
# It is recommended one does "agiza webbrowser" and uses webbrowser.open(url)
# instead of "kutoka webbrowser agiza *".

eleza open(url, new=0, autoraise=True):
    ikiwa _tryorder is None:
        with _lock:
            ikiwa _tryorder is None:
                register_standard_browsers()
    for name in _tryorder:
        browser = get(name)
        ikiwa browser.open(url, new, autoraise):
            rudisha True
    rudisha False

eleza open_new(url):
    rudisha open(url, 1)

eleza open_new_tab(url):
    rudisha open(url, 2)


eleza _synthesize(browser, *, preferred=False):
    """Attempt to synthesize a controller base on existing controllers.

    This is useful to create a controller when a user specifies a path to
    an entry in the BROWSER environment variable -- we can copy a general
    controller to operate using a specific installation of the desired
    browser in this way.

    If we can't create a controller in this way, or ikiwa there is no
    executable for the requested browser, rudisha [None, None].

    """
    cmd = browser.split()[0]
    ikiwa not shutil.which(cmd):
        rudisha [None, None]
    name = os.path.basename(cmd)
    try:
        command = _browsers[name.lower()]
    except KeyError:
        rudisha [None, None]
    # now attempt to clone to fit the new name:
    controller = command[1]
    ikiwa controller and name.lower() == controller.basename:
        agiza copy
        controller = copy.copy(controller)
        controller.name = browser
        controller.basename = os.path.basename(browser)
        register(browser, None, instance=controller, preferred=preferred)
        rudisha [None, controller]
    rudisha [None, None]


# General parent classes

kundi BaseBrowser(object):
    """Parent kundi for all browsers. Do not use directly."""

    args = ['%s']

    eleza __init__(self, name=""):
        self.name = name
        self.basename = name

    eleza open(self, url, new=0, autoraise=True):
        raise NotImplementedError

    eleza open_new(self, url):
        rudisha self.open(url, 1)

    eleza open_new_tab(self, url):
        rudisha self.open(url, 2)


kundi GenericBrowser(BaseBrowser):
    """Class for all browsers started with a command
       and without remote functionality."""

    eleza __init__(self, name):
        ikiwa isinstance(name, str):
            self.name = name
            self.args = ["%s"]
        else:
            # name should be a list with arguments
            self.name = name[0]
            self.args = name[1:]
        self.basename = os.path.basename(self.name)

    eleza open(self, url, new=0, autoraise=True):
        sys.audit("webbrowser.open", url)
        cmdline = [self.name] + [arg.replace("%s", url)
                                 for arg in self.args]
        try:
            ikiwa sys.platform[:3] == 'win':
                p = subprocess.Popen(cmdline)
            else:
                p = subprocess.Popen(cmdline, close_fds=True)
            rudisha not p.wait()
        except OSError:
            rudisha False


kundi BackgroundBrowser(GenericBrowser):
    """Class for all browsers which are to be started in the
       background."""

    eleza open(self, url, new=0, autoraise=True):
        cmdline = [self.name] + [arg.replace("%s", url)
                                 for arg in self.args]
        sys.audit("webbrowser.open", url)
        try:
            ikiwa sys.platform[:3] == 'win':
                p = subprocess.Popen(cmdline)
            else:
                p = subprocess.Popen(cmdline, close_fds=True,
                                     start_new_session=True)
            rudisha (p.poll() is None)
        except OSError:
            rudisha False


kundi UnixBrowser(BaseBrowser):
    """Parent kundi for all Unix browsers with remote functionality."""

    raise_opts = None
    background = False
    redirect_stdout = True
    # In remote_args, %s will be replaced with the requested URL.  %action will
    # be replaced depending on the value of 'new' passed to open.
    # remote_action is used for new=0 (open).  If newwin is not None, it is
    # used for new=1 (open_new).  If newtab is not None, it is used for
    # new=3 (open_new_tab).  After both substitutions are made, any empty
    # strings in the transformed remote_args list will be removed.
    remote_args = ['%action', '%s']
    remote_action = None
    remote_action_newwin = None
    remote_action_newtab = None

    eleza _invoke(self, args, remote, autoraise, url=None):
        raise_opt = []
        ikiwa remote and self.raise_opts:
            # use autoraise argument only for remote invocation
            autoraise = int(autoraise)
            opt = self.raise_opts[autoraise]
            ikiwa opt: raise_opt = [opt]

        cmdline = [self.name] + raise_opt + args

        ikiwa remote or self.background:
            inout = subprocess.DEVNULL
        else:
            # for TTY browsers, we need stdin/out
            inout = None
        p = subprocess.Popen(cmdline, close_fds=True, stdin=inout,
                             stdout=(self.redirect_stdout and inout or None),
                             stderr=inout, start_new_session=True)
        ikiwa remote:
            # wait at most five seconds. If the subprocess is not finished, the
            # remote invocation has (hopefully) started a new instance.
            try:
                rc = p.wait(5)
                # ikiwa remote call failed, open() will try direct invocation
                rudisha not rc
            except subprocess.TimeoutExpired:
                rudisha True
        elikiwa self.background:
            ikiwa p.poll() is None:
                rudisha True
            else:
                rudisha False
        else:
            rudisha not p.wait()

    eleza open(self, url, new=0, autoraise=True):
        sys.audit("webbrowser.open", url)
        ikiwa new == 0:
            action = self.remote_action
        elikiwa new == 1:
            action = self.remote_action_newwin
        elikiwa new == 2:
            ikiwa self.remote_action_newtab is None:
                action = self.remote_action_newwin
            else:
                action = self.remote_action_newtab
        else:
            raise Error("Bad 'new' parameter to open(); " +
                        "expected 0, 1, or 2, got %s" % new)

        args = [arg.replace("%s", url).replace("%action", action)
                for arg in self.remote_args]
        args = [arg for arg in args ikiwa arg]
        success = self._invoke(args, True, autoraise, url)
        ikiwa not success:
            # remote invocation failed, try straight way
            args = [arg.replace("%s", url) for arg in self.args]
            rudisha self._invoke(args, False, False)
        else:
            rudisha True


kundi Mozilla(UnixBrowser):
    """Launcher kundi for Mozilla browsers."""

    remote_args = ['%action', '%s']
    remote_action = ""
    remote_action_newwin = "-new-window"
    remote_action_newtab = "-new-tab"
    background = True


kundi Netscape(UnixBrowser):
    """Launcher kundi for Netscape browser."""

    raise_opts = ["-noraise", "-raise"]
    remote_args = ['-remote', 'openURL(%s%action)']
    remote_action = ""
    remote_action_newwin = ",new-window"
    remote_action_newtab = ",new-tab"
    background = True


kundi Galeon(UnixBrowser):
    """Launcher kundi for Galeon/Epiphany browsers."""

    raise_opts = ["-noraise", ""]
    remote_args = ['%action', '%s']
    remote_action = "-n"
    remote_action_newwin = "-w"
    background = True


kundi Chrome(UnixBrowser):
    "Launcher kundi for Google Chrome browser."

    remote_args = ['%action', '%s']
    remote_action = ""
    remote_action_newwin = "--new-window"
    remote_action_newtab = ""
    background = True

Chromium = Chrome


kundi Opera(UnixBrowser):
    "Launcher kundi for Opera browser."

    remote_args = ['%action', '%s']
    remote_action = ""
    remote_action_newwin = "--new-window"
    remote_action_newtab = ""
    background = True


kundi Elinks(UnixBrowser):
    "Launcher kundi for Elinks browsers."

    remote_args = ['-remote', 'openURL(%s%action)']
    remote_action = ""
    remote_action_newwin = ",new-window"
    remote_action_newtab = ",new-tab"
    background = False

    # elinks doesn't like its stdout to be redirected -
    # it uses redirected stdout as a signal to do -dump
    redirect_stdout = False


kundi Konqueror(BaseBrowser):
    """Controller for the KDE File Manager (kfm, or Konqueror).

    See the output of ``kfmclient --commands``
    for more information on the Konqueror remote-control interface.
    """

    eleza open(self, url, new=0, autoraise=True):
        sys.audit("webbrowser.open", url)
        # XXX Currently I know no way to prevent KFM kutoka opening a new win.
        ikiwa new == 2:
            action = "newTab"
        else:
            action = "openURL"

        devnull = subprocess.DEVNULL

        try:
            p = subprocess.Popen(["kfmclient", action, url],
                                 close_fds=True, stdin=devnull,
                                 stdout=devnull, stderr=devnull)
        except OSError:
            # fall through to next variant
            pass
        else:
            p.wait()
            # kfmclient's rudisha code unfortunately has no meaning as it seems
            rudisha True

        try:
            p = subprocess.Popen(["konqueror", "--silent", url],
                                 close_fds=True, stdin=devnull,
                                 stdout=devnull, stderr=devnull,
                                 start_new_session=True)
        except OSError:
            # fall through to next variant
            pass
        else:
            ikiwa p.poll() is None:
                # Should be running now.
                rudisha True

        try:
            p = subprocess.Popen(["kfm", "-d", url],
                                 close_fds=True, stdin=devnull,
                                 stdout=devnull, stderr=devnull,
                                 start_new_session=True)
        except OSError:
            rudisha False
        else:
            rudisha (p.poll() is None)


kundi Grail(BaseBrowser):
    # There should be a way to maintain a connection to Grail, but the
    # Grail remote control protocol doesn't really allow that at this
    # point.  It probably never will!
    eleza _find_grail_rc(self):
        agiza glob
        agiza pwd
        agiza socket
        agiza tempfile
        tempdir = os.path.join(tempfile.gettempdir(),
                               ".grail-unix")
        user = pwd.getpwuid(os.getuid())[0]
        filename = os.path.join(tempdir, user + "-*")
        maybes = glob.glob(filename)
        ikiwa not maybes:
            rudisha None
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        for fn in maybes:
            # need to PING each one until we find one that's live
            try:
                s.connect(fn)
            except OSError:
                # no good; attempt to clean it out, but don't fail:
                try:
                    os.unlink(fn)
                except OSError:
                    pass
            else:
                rudisha s

    eleza _remote(self, action):
        s = self._find_grail_rc()
        ikiwa not s:
            rudisha 0
        s.send(action)
        s.close()
        rudisha 1

    eleza open(self, url, new=0, autoraise=True):
        sys.audit("webbrowser.open", url)
        ikiwa new:
            ok = self._remote("LOADNEW " + url)
        else:
            ok = self._remote("LOAD " + url)
        rudisha ok


#
# Platform support for Unix
#

# These are the right tests because all these Unix browsers require either
# a console terminal or an X display to run.

eleza register_X_browsers():

    # use xdg-open ikiwa around
    ikiwa shutil.which("xdg-open"):
        register("xdg-open", None, BackgroundBrowser("xdg-open"))

    # The default GNOME3 browser
    ikiwa "GNOME_DESKTOP_SESSION_ID" in os.environ and shutil.which("gvfs-open"):
        register("gvfs-open", None, BackgroundBrowser("gvfs-open"))

    # The default GNOME browser
    ikiwa "GNOME_DESKTOP_SESSION_ID" in os.environ and shutil.which("gnome-open"):
        register("gnome-open", None, BackgroundBrowser("gnome-open"))

    # The default KDE browser
    ikiwa "KDE_FULL_SESSION" in os.environ and shutil.which("kfmclient"):
        register("kfmclient", Konqueror, Konqueror("kfmclient"))

    ikiwa shutil.which("x-www-browser"):
        register("x-www-browser", None, BackgroundBrowser("x-www-browser"))

    # The Mozilla browsers
    for browser in ("firefox", "iceweasel", "iceape", "seamonkey"):
        ikiwa shutil.which(browser):
            register(browser, None, Mozilla(browser))

    # The Netscape and old Mozilla browsers
    for browser in ("mozilla-firefox",
                    "mozilla-firebird", "firebird",
                    "mozilla", "netscape"):
        ikiwa shutil.which(browser):
            register(browser, None, Netscape(browser))

    # Konqueror/kfm, the KDE browser.
    ikiwa shutil.which("kfm"):
        register("kfm", Konqueror, Konqueror("kfm"))
    elikiwa shutil.which("konqueror"):
        register("konqueror", Konqueror, Konqueror("konqueror"))

    # Gnome's Galeon and Epiphany
    for browser in ("galeon", "epiphany"):
        ikiwa shutil.which(browser):
            register(browser, None, Galeon(browser))

    # Skipstone, another Gtk/Mozilla based browser
    ikiwa shutil.which("skipstone"):
        register("skipstone", None, BackgroundBrowser("skipstone"))

    # Google Chrome/Chromium browsers
    for browser in ("google-chrome", "chrome", "chromium", "chromium-browser"):
        ikiwa shutil.which(browser):
            register(browser, None, Chrome(browser))

    # Opera, quite popular
    ikiwa shutil.which("opera"):
        register("opera", None, Opera("opera"))

    # Next, Mosaic -- old but still in use.
    ikiwa shutil.which("mosaic"):
        register("mosaic", None, BackgroundBrowser("mosaic"))

    # Grail, the Python browser. Does anybody still use it?
    ikiwa shutil.which("grail"):
        register("grail", Grail, None)

eleza register_standard_browsers():
    global _tryorder
    _tryorder = []

    ikiwa sys.platform == 'darwin':
        register("MacOSX", None, MacOSXOSAScript('default'))
        register("chrome", None, MacOSXOSAScript('chrome'))
        register("firefox", None, MacOSXOSAScript('firefox'))
        register("safari", None, MacOSXOSAScript('safari'))
        # OS X can use below Unix support (but we prefer using the OS X
        # specific stuff)

    ikiwa sys.platform[:3] == "win":
        # First try to use the default Windows browser
        register("windows-default", WindowsDefault)

        # Detect some common Windows browsers, fallback to IE
        iexplore = os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"),
                                "Internet Explorer\\IEXPLORE.EXE")
        for browser in ("firefox", "firebird", "seamonkey", "mozilla",
                        "netscape", "opera", iexplore):
            ikiwa shutil.which(browser):
                register(browser, None, BackgroundBrowser(browser))
    else:
        # Prefer X browsers ikiwa present
        ikiwa os.environ.get("DISPLAY"):
            try:
                cmd = "xdg-settings get default-web-browser".split()
                raw_result = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
                result = raw_result.decode().strip()
            except (FileNotFoundError, subprocess.CalledProcessError):
                pass
            else:
                global _os_preferred_browser
                _os_preferred_browser = result

            register_X_browsers()

        # Also try console browsers
        ikiwa os.environ.get("TERM"):
            ikiwa shutil.which("www-browser"):
                register("www-browser", None, GenericBrowser("www-browser"))
            # The Links/elinks browsers <http://artax.karlin.mff.cuni.cz/~mikulas/links/>
            ikiwa shutil.which("links"):
                register("links", None, GenericBrowser("links"))
            ikiwa shutil.which("elinks"):
                register("elinks", None, Elinks("elinks"))
            # The Lynx browser <http://lynx.isc.org/>, <http://lynx.browser.org/>
            ikiwa shutil.which("lynx"):
                register("lynx", None, GenericBrowser("lynx"))
            # The w3m browser <http://w3m.sourceforge.net/>
            ikiwa shutil.which("w3m"):
                register("w3m", None, GenericBrowser("w3m"))

    # OK, now that we know what the default preference orders for each
    # platform are, allow user to override them with the BROWSER variable.
    ikiwa "BROWSER" in os.environ:
        userchoices = os.environ["BROWSER"].split(os.pathsep)
        userchoices.reverse()

        # Treat choices in same way as ikiwa passed into get() but do register
        # and prepend to _tryorder
        for cmdline in userchoices:
            ikiwa cmdline != '':
                cmd = _synthesize(cmdline, preferred=True)
                ikiwa cmd[1] is None:
                    register(cmdline, None, GenericBrowser(cmdline), preferred=True)

    # what to do ikiwa _tryorder is now empty?


#
# Platform support for Windows
#

ikiwa sys.platform[:3] == "win":
    kundi WindowsDefault(BaseBrowser):
        eleza open(self, url, new=0, autoraise=True):
            sys.audit("webbrowser.open", url)
            try:
                os.startfile(url)
            except OSError:
                # [Error 22] No application is associated with the specified
                # file for this operation: '<URL>'
                rudisha False
            else:
                rudisha True

#
# Platform support for MacOS
#

ikiwa sys.platform == 'darwin':
    # Adapted kutoka patch submitted to SourceForge by Steven J. Burr
    kundi MacOSX(BaseBrowser):
        """Launcher kundi for Aqua browsers on Mac OS X

        Optionally specify a browser name on instantiation.  Note that this
        will not work for Aqua browsers ikiwa the user has moved the application
        package after installation.

        If no browser is specified, the default browser, as specified in the
        Internet System Preferences panel, will be used.
        """
        eleza __init__(self, name):
            self.name = name

        eleza open(self, url, new=0, autoraise=True):
            sys.audit("webbrowser.open", url)
            assert "'" not in url
            # hack for local urls
            ikiwa not ':' in url:
                url = 'file:'+url

            # new must be 0 or 1
            new = int(bool(new))
            ikiwa self.name == "default":
                # User called open, open_new or get without a browser parameter
                script = 'open location "%s"' % url.replace('"', '%22') # opens in default browser
            else:
                # User called get and chose a browser
                ikiwa self.name == "OmniWeb":
                    toWindow = ""
                else:
                    # Include toWindow parameter of OpenURL command for browsers
                    # that support it.  0 == new window; -1 == existing
                    toWindow = "toWindow %d" % (new - 1)
                cmd = 'OpenURL "%s"' % url.replace('"', '%22')
                script = '''tell application "%s"
                                activate
                                %s %s
                            end tell''' % (self.name, cmd, toWindow)
            # Open pipe to AppleScript through osascript command
            osapipe = os.popen("osascript", "w")
            ikiwa osapipe is None:
                rudisha False
            # Write script to osascript's stdin
            osapipe.write(script)
            rc = osapipe.close()
            rudisha not rc

    kundi MacOSXOSAScript(BaseBrowser):
        eleza __init__(self, name):
            self._name = name

        eleza open(self, url, new=0, autoraise=True):
            ikiwa self._name == 'default':
                script = 'open location "%s"' % url.replace('"', '%22') # opens in default browser
            else:
                script = '''
                   tell application "%s"
                       activate
                       open location "%s"
                   end
                   '''%(self._name, url.replace('"', '%22'))

            osapipe = os.popen("osascript", "w")
            ikiwa osapipe is None:
                rudisha False

            osapipe.write(script)
            rc = osapipe.close()
            rudisha not rc


eleza main():
    agiza getopt
    usage = """Usage: %s [-n | -t] url
    -n: open new window
    -t: open new tab""" % sys.argv[0]
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'ntd')
    except getopt.error as msg:
        andika(msg, file=sys.stderr)
        andika(usage, file=sys.stderr)
        sys.exit(1)
    new_win = 0
    for o, a in opts:
        ikiwa o == '-n': new_win = 1
        elikiwa o == '-t': new_win = 2
    ikiwa len(args) != 1:
        andika(usage, file=sys.stderr)
        sys.exit(1)

    url = args[0]
    open(url, new_win)

    andika("\a")

ikiwa __name__ == "__main__":
    main()
