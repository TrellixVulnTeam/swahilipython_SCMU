#! /usr/bin/env python3
"""Interfaces kila launching na remotely controlling Web browsers."""
# Maintained by Georg Brandl.

agiza os
agiza shlex
agiza shutil
agiza sys
agiza subprocess
agiza threading

__all__ = ["Error", "open", "open_new", "open_new_tab", "get", "register"]

kundi Error(Exception):
    pita

_lock = threading.RLock()
_browsers = {}                  # Dictionary of available browser controllers
_tryorder = Tupu                # Preference order of available browsers
_os_preferred_browser = Tupu    # The preferred browser

eleza register(name, klass, instance=Tupu, *, preferred=Uongo):
    """Register a browser connector."""
    ukijumuisha _lock:
        ikiwa _tryorder ni Tupu:
            register_standard_browsers()
        _browsers[name.lower()] = [klass, instance]

        # Preferred browsers go to the front of the list.
        # Need to match to the default browser returned by xdg-settings, which
        # may be of the form e.g. "firefox.desktop".
        ikiwa preferred ama (_os_preferred_browser na name kwenye _os_preferred_browser):
            _tryorder.insert(0, name)
        isipokua:
            _tryorder.append(name)

eleza get(using=Tupu):
    """Return a browser launcher instance appropriate kila the environment."""
    ikiwa _tryorder ni Tupu:
        ukijumuisha _lock:
            ikiwa _tryorder ni Tupu:
                register_standard_browsers()
    ikiwa using ni sio Tupu:
        alternatives = [using]
    isipokua:
        alternatives = _tryorder
    kila browser kwenye alternatives:
        ikiwa '%s' kwenye browser:
            # User gave us a command line, split it into name na args
            browser = shlex.split(browser)
            ikiwa browser[-1] == '&':
                rudisha BackgroundBrowser(browser[:-1])
            isipokua:
                rudisha GenericBrowser(browser)
        isipokua:
            # User gave us a browser name ama path.
            jaribu:
                command = _browsers[browser.lower()]
            tatizo KeyError:
                command = _synthesize(browser)
            ikiwa command[1] ni sio Tupu:
                rudisha command[1]
            lasivyo command[0] ni sio Tupu:
                rudisha command[0]()
    ashiria Error("could sio locate runnable browser")

# Please note: the following definition hides a builtin function.
# It ni recommended one does "agiza webbrowser" na uses webbrowser.open(url)
# instead of "kutoka webbrowser agiza *".

eleza open(url, new=0, autoraise=Kweli):
    ikiwa _tryorder ni Tupu:
        ukijumuisha _lock:
            ikiwa _tryorder ni Tupu:
                register_standard_browsers()
    kila name kwenye _tryorder:
        browser = get(name)
        ikiwa browser.open(url, new, autoraise):
            rudisha Kweli
    rudisha Uongo

eleza open_new(url):
    rudisha open(url, 1)

eleza open_new_tab(url):
    rudisha open(url, 2)


eleza _synthesize(browser, *, preferred=Uongo):
    """Attempt to synthesize a controller base on existing controllers.

    This ni useful to create a controller when a user specifies a path to
    an entry kwenye the BROWSER environment variable -- we can copy a general
    controller to operate using a specific installation of the desired
    browser kwenye this way.

    If we can't create a controller kwenye this way, ama ikiwa there ni no
    executable kila the requested browser, rudisha [Tupu, Tupu].

    """
    cmd = browser.split()[0]
    ikiwa sio shutil.which(cmd):
        rudisha [Tupu, Tupu]
    name = os.path.basename(cmd)
    jaribu:
        command = _browsers[name.lower()]
    tatizo KeyError:
        rudisha [Tupu, Tupu]
    # now attempt to clone to fit the new name:
    controller = command[1]
    ikiwa controller na name.lower() == controller.basename:
        agiza copy
        controller = copy.copy(controller)
        controller.name = browser
        controller.basename = os.path.basename(browser)
        register(browser, Tupu, instance=controller, preferred=preferred)
        rudisha [Tupu, controller]
    rudisha [Tupu, Tupu]


# General parent classes

kundi BaseBrowser(object):
    """Parent kundi kila all browsers. Do sio use directly."""

    args = ['%s']

    eleza __init__(self, name=""):
        self.name = name
        self.basename = name

    eleza open(self, url, new=0, autoraise=Kweli):
        ashiria NotImplementedError

    eleza open_new(self, url):
        rudisha self.open(url, 1)

    eleza open_new_tab(self, url):
        rudisha self.open(url, 2)


kundi GenericBrowser(BaseBrowser):
    """Class kila all browsers started ukijumuisha a command
       na without remote functionality."""

    eleza __init__(self, name):
        ikiwa isinstance(name, str):
            self.name = name
            self.args = ["%s"]
        isipokua:
            # name should be a list ukijumuisha arguments
            self.name = name[0]
            self.args = name[1:]
        self.basename = os.path.basename(self.name)

    eleza open(self, url, new=0, autoraise=Kweli):
        sys.audit("webbrowser.open", url)
        cmdline = [self.name] + [arg.replace("%s", url)
                                 kila arg kwenye self.args]
        jaribu:
            ikiwa sys.platform[:3] == 'win':
                p = subprocess.Popen(cmdline)
            isipokua:
                p = subprocess.Popen(cmdline, close_fds=Kweli)
            rudisha sio p.wait()
        tatizo OSError:
            rudisha Uongo


kundi BackgroundBrowser(GenericBrowser):
    """Class kila all browsers which are to be started kwenye the
       background."""

    eleza open(self, url, new=0, autoraise=Kweli):
        cmdline = [self.name] + [arg.replace("%s", url)
                                 kila arg kwenye self.args]
        sys.audit("webbrowser.open", url)
        jaribu:
            ikiwa sys.platform[:3] == 'win':
                p = subprocess.Popen(cmdline)
            isipokua:
                p = subprocess.Popen(cmdline, close_fds=Kweli,
                                     start_new_session=Kweli)
            rudisha (p.poll() ni Tupu)
        tatizo OSError:
            rudisha Uongo


kundi UnixBrowser(BaseBrowser):
    """Parent kundi kila all Unix browsers ukijumuisha remote functionality."""

    raise_opts = Tupu
    background = Uongo
    redirect_stdout = Kweli
    # In remote_args, %s will be replaced ukijumuisha the requested URL.  %action will
    # be replaced depending on the value of 'new' pitaed to open.
    # remote_action ni used kila new=0 (open).  If newwin ni sio Tupu, it is
    # used kila new=1 (open_new).  If newtab ni sio Tupu, it ni used for
    # new=3 (open_new_tab).  After both substitutions are made, any empty
    # strings kwenye the transformed remote_args list will be removed.
    remote_args = ['%action', '%s']
    remote_action = Tupu
    remote_action_newwin = Tupu
    remote_action_newtab = Tupu

    eleza _invoke(self, args, remote, autoraise, url=Tupu):
        raise_opt = []
        ikiwa remote na self.raise_opts:
            # use autoashiria argument only kila remote invocation
            autoashiria = int(autoraise)
            opt = self.raise_opts[autoraise]
            ikiwa opt: raise_opt = [opt]

        cmdline = [self.name] + raise_opt + args

        ikiwa remote ama self.background:
            inout = subprocess.DEVNULL
        isipokua:
            # kila TTY browsers, we need stdin/out
            inout = Tupu
        p = subprocess.Popen(cmdline, close_fds=Kweli, stdin=inout,
                             stdout=(self.redirect_stdout na inout ama Tupu),
                             stderr=inout, start_new_session=Kweli)
        ikiwa remote:
            # wait at most five seconds. If the subprocess ni sio finished, the
            # remote invocation has (hopefully) started a new instance.
            jaribu:
                rc = p.wait(5)
                # ikiwa remote call failed, open() will try direct invocation
                rudisha sio rc
            tatizo subprocess.TimeoutExpired:
                rudisha Kweli
        lasivyo self.background:
            ikiwa p.poll() ni Tupu:
                rudisha Kweli
            isipokua:
                rudisha Uongo
        isipokua:
            rudisha sio p.wait()

    eleza open(self, url, new=0, autoraise=Kweli):
        sys.audit("webbrowser.open", url)
        ikiwa new == 0:
            action = self.remote_action
        lasivyo new == 1:
            action = self.remote_action_newwin
        lasivyo new == 2:
            ikiwa self.remote_action_newtab ni Tupu:
                action = self.remote_action_newwin
            isipokua:
                action = self.remote_action_newtab
        isipokua:
            ashiria Error("Bad 'new' parameter to open(); " +
                        "expected 0, 1, ama 2, got %s" % new)

        args = [arg.replace("%s", url).replace("%action", action)
                kila arg kwenye self.remote_args]
        args = [arg kila arg kwenye args ikiwa arg]
        success = self._invoke(args, Kweli, autoraise, url)
        ikiwa sio success:
            # remote invocation failed, try straight way
            args = [arg.replace("%s", url) kila arg kwenye self.args]
            rudisha self._invoke(args, Uongo, Uongo)
        isipokua:
            rudisha Kweli


kundi Mozilla(UnixBrowser):
    """Launcher kundi kila Mozilla browsers."""

    remote_args = ['%action', '%s']
    remote_action = ""
    remote_action_newwin = "-new-window"
    remote_action_newtab = "-new-tab"
    background = Kweli


kundi Netscape(UnixBrowser):
    """Launcher kundi kila Netscape browser."""

    raise_opts = ["-noraise", "-raise"]
    remote_args = ['-remote', 'openURL(%s%action)']
    remote_action = ""
    remote_action_newwin = ",new-window"
    remote_action_newtab = ",new-tab"
    background = Kweli


kundi Galeon(UnixBrowser):
    """Launcher kundi kila Galeon/Epiphany browsers."""

    raise_opts = ["-noraise", ""]
    remote_args = ['%action', '%s']
    remote_action = "-n"
    remote_action_newwin = "-w"
    background = Kweli


kundi Chrome(UnixBrowser):
    "Launcher kundi kila Google Chrome browser."

    remote_args = ['%action', '%s']
    remote_action = ""
    remote_action_newwin = "--new-window"
    remote_action_newtab = ""
    background = Kweli

Chromium = Chrome


kundi Opera(UnixBrowser):
    "Launcher kundi kila Opera browser."

    remote_args = ['%action', '%s']
    remote_action = ""
    remote_action_newwin = "--new-window"
    remote_action_newtab = ""
    background = Kweli


kundi Elinks(UnixBrowser):
    "Launcher kundi kila Elinks browsers."

    remote_args = ['-remote', 'openURL(%s%action)']
    remote_action = ""
    remote_action_newwin = ",new-window"
    remote_action_newtab = ",new-tab"
    background = Uongo

    # elinks doesn't like its stdout to be redirected -
    # it uses redirected stdout kama a signal to do -dump
    redirect_stdout = Uongo


kundi Konqueror(BaseBrowser):
    """Controller kila the KDE File Manager (kfm, ama Konqueror).

    See the output of ``kfmclient --commands``
    kila more information on the Konqueror remote-control interface.
    """

    eleza open(self, url, new=0, autoraise=Kweli):
        sys.audit("webbrowser.open", url)
        # XXX Currently I know no way to prevent KFM kutoka opening a new win.
        ikiwa new == 2:
            action = "newTab"
        isipokua:
            action = "openURL"

        devnull = subprocess.DEVNULL

        jaribu:
            p = subprocess.Popen(["kfmclient", action, url],
                                 close_fds=Kweli, stdin=devnull,
                                 stdout=devnull, stderr=devnull)
        tatizo OSError:
            # fall through to next variant
            pita
        isipokua:
            p.wait()
            # kfmclient's rudisha code unfortunately has no meaning kama it seems
            rudisha Kweli

        jaribu:
            p = subprocess.Popen(["konqueror", "--silent", url],
                                 close_fds=Kweli, stdin=devnull,
                                 stdout=devnull, stderr=devnull,
                                 start_new_session=Kweli)
        tatizo OSError:
            # fall through to next variant
            pita
        isipokua:
            ikiwa p.poll() ni Tupu:
                # Should be running now.
                rudisha Kweli

        jaribu:
            p = subprocess.Popen(["kfm", "-d", url],
                                 close_fds=Kweli, stdin=devnull,
                                 stdout=devnull, stderr=devnull,
                                 start_new_session=Kweli)
        tatizo OSError:
            rudisha Uongo
        isipokua:
            rudisha (p.poll() ni Tupu)


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
        ikiwa sio maybes:
            rudisha Tupu
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        kila fn kwenye maybes:
            # need to PING each one until we find one that's live
            jaribu:
                s.connect(fn)
            tatizo OSError:
                # no good; attempt to clean it out, but don't fail:
                jaribu:
                    os.unlink(fn)
                tatizo OSError:
                    pita
            isipokua:
                rudisha s

    eleza _remote(self, action):
        s = self._find_grail_rc()
        ikiwa sio s:
            rudisha 0
        s.send(action)
        s.close()
        rudisha 1

    eleza open(self, url, new=0, autoraise=Kweli):
        sys.audit("webbrowser.open", url)
        ikiwa new:
            ok = self._remote("LOADNEW " + url)
        isipokua:
            ok = self._remote("LOAD " + url)
        rudisha ok


#
# Platform support kila Unix
#

# These are the right tests because all these Unix browsers require either
# a console terminal ama an X display to run.

eleza register_X_browsers():

    # use xdg-open ikiwa around
    ikiwa shutil.which("xdg-open"):
        register("xdg-open", Tupu, BackgroundBrowser("xdg-open"))

    # The default GNOME3 browser
    ikiwa "GNOME_DESKTOP_SESSION_ID" kwenye os.environ na shutil.which("gvfs-open"):
        register("gvfs-open", Tupu, BackgroundBrowser("gvfs-open"))

    # The default GNOME browser
    ikiwa "GNOME_DESKTOP_SESSION_ID" kwenye os.environ na shutil.which("gnome-open"):
        register("gnome-open", Tupu, BackgroundBrowser("gnome-open"))

    # The default KDE browser
    ikiwa "KDE_FULL_SESSION" kwenye os.environ na shutil.which("kfmclient"):
        register("kfmclient", Konqueror, Konqueror("kfmclient"))

    ikiwa shutil.which("x-www-browser"):
        register("x-www-browser", Tupu, BackgroundBrowser("x-www-browser"))

    # The Mozilla browsers
    kila browser kwenye ("firefox", "iceweasel", "iceape", "seamonkey"):
        ikiwa shutil.which(browser):
            register(browser, Tupu, Mozilla(browser))

    # The Netscape na old Mozilla browsers
    kila browser kwenye ("mozilla-firefox",
                    "mozilla-firebird", "firebird",
                    "mozilla", "netscape"):
        ikiwa shutil.which(browser):
            register(browser, Tupu, Netscape(browser))

    # Konqueror/kfm, the KDE browser.
    ikiwa shutil.which("kfm"):
        register("kfm", Konqueror, Konqueror("kfm"))
    lasivyo shutil.which("konqueror"):
        register("konqueror", Konqueror, Konqueror("konqueror"))

    # Gnome's Galeon na Epiphany
    kila browser kwenye ("galeon", "epiphany"):
        ikiwa shutil.which(browser):
            register(browser, Tupu, Galeon(browser))

    # Skipstone, another Gtk/Mozilla based browser
    ikiwa shutil.which("skipstone"):
        register("skipstone", Tupu, BackgroundBrowser("skipstone"))

    # Google Chrome/Chromium browsers
    kila browser kwenye ("google-chrome", "chrome", "chromium", "chromium-browser"):
        ikiwa shutil.which(browser):
            register(browser, Tupu, Chrome(browser))

    # Opera, quite popular
    ikiwa shutil.which("opera"):
        register("opera", Tupu, Opera("opera"))

    # Next, Mosaic -- old but still kwenye use.
    ikiwa shutil.which("mosaic"):
        register("mosaic", Tupu, BackgroundBrowser("mosaic"))

    # Grail, the Python browser. Does anybody still use it?
    ikiwa shutil.which("grail"):
        register("grail", Grail, Tupu)

eleza register_standard_browsers():
    global _tryorder
    _tryorder = []

    ikiwa sys.platform == 'darwin':
        register("MacOSX", Tupu, MacOSXOSAScript('default'))
        register("chrome", Tupu, MacOSXOSAScript('chrome'))
        register("firefox", Tupu, MacOSXOSAScript('firefox'))
        register("safari", Tupu, MacOSXOSAScript('safari'))
        # OS X can use below Unix support (but we prefer using the OS X
        # specific stuff)

    ikiwa sys.platform[:3] == "win":
        # First try to use the default Windows browser
        register("windows-default", WindowsDefault)

        # Detect some common Windows browsers, fallback to IE
        iexplore = os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"),
                                "Internet Explorer\\IEXPLORE.EXE")
        kila browser kwenye ("firefox", "firebird", "seamonkey", "mozilla",
                        "netscape", "opera", iexplore):
            ikiwa shutil.which(browser):
                register(browser, Tupu, BackgroundBrowser(browser))
    isipokua:
        # Prefer X browsers ikiwa present
        ikiwa os.environ.get("DISPLAY"):
            jaribu:
                cmd = "xdg-settings get default-web-browser".split()
                raw_result = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
                result = raw_result.decode().strip()
            tatizo (FileNotFoundError, subprocess.CalledProcessError):
                pita
            isipokua:
                global _os_preferred_browser
                _os_preferred_browser = result

            register_X_browsers()

        # Also try console browsers
        ikiwa os.environ.get("TERM"):
            ikiwa shutil.which("www-browser"):
                register("www-browser", Tupu, GenericBrowser("www-browser"))
            # The Links/elinks browsers <http://artax.karlin.mff.cuni.cz/~mikulas/links/>
            ikiwa shutil.which("links"):
                register("links", Tupu, GenericBrowser("links"))
            ikiwa shutil.which("elinks"):
                register("elinks", Tupu, Elinks("elinks"))
            # The Lynx browser <http://lynx.isc.org/>, <http://lynx.browser.org/>
            ikiwa shutil.which("lynx"):
                register("lynx", Tupu, GenericBrowser("lynx"))
            # The w3m browser <http://w3m.sourceforge.net/>
            ikiwa shutil.which("w3m"):
                register("w3m", Tupu, GenericBrowser("w3m"))

    # OK, now that we know what the default preference orders kila each
    # platform are, allow user to override them ukijumuisha the BROWSER variable.
    ikiwa "BROWSER" kwenye os.environ:
        userchoices = os.environ["BROWSER"].split(os.pathsep)
        userchoices.reverse()

        # Treat choices kwenye same way kama ikiwa pitaed into get() but do register
        # na prepend to _tryorder
        kila cmdline kwenye userchoices:
            ikiwa cmdline != '':
                cmd = _synthesize(cmdline, preferred=Kweli)
                ikiwa cmd[1] ni Tupu:
                    register(cmdline, Tupu, GenericBrowser(cmdline), preferred=Kweli)

    # what to do ikiwa _tryorder ni now empty?


#
# Platform support kila Windows
#

ikiwa sys.platform[:3] == "win":
    kundi WindowsDefault(BaseBrowser):
        eleza open(self, url, new=0, autoraise=Kweli):
            sys.audit("webbrowser.open", url)
            jaribu:
                os.startfile(url)
            tatizo OSError:
                # [Error 22] No application ni associated ukijumuisha the specified
                # file kila this operation: '<URL>'
                rudisha Uongo
            isipokua:
                rudisha Kweli

#
# Platform support kila MacOS
#

ikiwa sys.platform == 'darwin':
    # Adapted kutoka patch submitted to SourceForge by Steven J. Burr
    kundi MacOSX(BaseBrowser):
        """Launcher kundi kila Aqua browsers on Mac OS X

        Optionally specify a browser name on instantiation.  Note that this
        will sio work kila Aqua browsers ikiwa the user has moved the application
        package after installation.

        If no browser ni specified, the default browser, kama specified kwenye the
        Internet System Preferences panel, will be used.
        """
        eleza __init__(self, name):
            self.name = name

        eleza open(self, url, new=0, autoraise=Kweli):
            sys.audit("webbrowser.open", url)
            assert "'" haiko kwenye url
            # hack kila local urls
            ikiwa sio ':' kwenye url:
                url = 'file:'+url

            # new must be 0 ama 1
            new = int(bool(new))
            ikiwa self.name == "default":
                # User called open, open_new ama get without a browser parameter
                script = 'open location "%s"' % url.replace('"', '%22') # opens kwenye default browser
            isipokua:
                # User called get na chose a browser
                ikiwa self.name == "OmniWeb":
                    toWindow = ""
                isipokua:
                    # Include toWindow parameter of OpenURL command kila browsers
                    # that support it.  0 == new window; -1 == existing
                    toWindow = "toWindow %d" % (new - 1)
                cmd = 'OpenURL "%s"' % url.replace('"', '%22')
                script = '''tell application "%s"
                                activate
                                %s %s
                            end tell''' % (self.name, cmd, toWindow)
            # Open pipe to AppleScript through osascript command
            osapipe = os.popen("osascript", "w")
            ikiwa osapipe ni Tupu:
                rudisha Uongo
            # Write script to osascript's stdin
            osapipe.write(script)
            rc = osapipe.close()
            rudisha sio rc

    kundi MacOSXOSAScript(BaseBrowser):
        eleza __init__(self, name):
            self._name = name

        eleza open(self, url, new=0, autoraise=Kweli):
            ikiwa self._name == 'default':
                script = 'open location "%s"' % url.replace('"', '%22') # opens kwenye default browser
            isipokua:
                script = '''
                   tell application "%s"
                       activate
                       open location "%s"
                   end
                   '''%(self._name, url.replace('"', '%22'))

            osapipe = os.popen("osascript", "w")
            ikiwa osapipe ni Tupu:
                rudisha Uongo

            osapipe.write(script)
            rc = osapipe.close()
            rudisha sio rc


eleza main():
    agiza getopt
    usage = """Usage: %s [-n | -t] url
    -n: open new window
    -t: open new tab""" % sys.argv[0]
    jaribu:
        opts, args = getopt.getopt(sys.argv[1:], 'ntd')
    tatizo getopt.error kama msg:
        andika(msg, file=sys.stderr)
        andika(usage, file=sys.stderr)
        sys.exit(1)
    new_win = 0
    kila o, a kwenye opts:
        ikiwa o == '-n': new_win = 1
        lasivyo o == '-t': new_win = 2
    ikiwa len(args) != 1:
        andika(usage, file=sys.stderr)
        sys.exit(1)

    url = args[0]
    open(url, new_win)

    andika("\a")

ikiwa __name__ == "__main__":
    main()
