#!/usr/bin/env python3
"""
GUI framework na application kila use ukijumuisha Python unit testing framework.
Execute tests written using the framework provided by the 'unittest' module.

Updated kila unittest test discovery by Mark Roddy na Python 3
support by Brian Curtin.

Based on the original by Steve Purcell, from:

  http://pyunit.sourceforge.net/

Copyright (c) 1999, 2000, 2001 Steve Purcell
This module ni free software, na you may redistribute it and/or modify
it under the same terms kama Python itself, so long kama this copyright message
and disclaimer are retained kwenye their original form.

IN NO EVENT SHALL THE AUTHOR BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT,
SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OF
THIS CODE, EVEN IF THE AUTHOR HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
DAMAGE.

THE AUTHOR SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE.  THE CODE PROVIDED HEREUNDER IS ON AN "AS IS" BASIS,
AND THERE IS NO OBLIGATION WHATSOEVER TO PROVIDE MAINTENANCE,
SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
"""

__author__ = "Steve Purcell (stephen_purcell@yahoo.com)"

agiza sys
agiza traceback
agiza unittest

agiza tkinter kama tk
kutoka tkinter agiza messagebox
kutoka tkinter agiza filedialog
kutoka tkinter agiza simpledialog




##############################################################################
# GUI framework classes
##############################################################################

kundi BaseGUITestRunner(object):
    """Subkundi this kundi to create a GUI TestRunner that uses a specific
    windowing toolkit. The kundi takes care of running tests kwenye the correct
    manner, na making callbacks to the derived kundi to obtain information
    ama signal that events have occurred.
    """
    eleza __init__(self, *args, **kwargs):
        self.currentResult = Tupu
        self.running = 0
        self.__rollbackImporter = Tupu
        self.__rollbackImporter = RollbackImporter()
        self.test_suite = Tupu

        #test discovery variables
        self.directory_to_read = ''
        self.top_level_dir = ''
        self.test_file_glob_pattern = 'test*.py'

        self.initGUI(*args, **kwargs)

    eleza errorDialog(self, title, message):
        "Override to display an error arising kutoka GUI usage"
        pita

    eleza getDirectoryToDiscover(self):
        "Override to prompt user kila directory to perform test discovery"
        pita

    eleza runClicked(self):
        "To be called kwenye response to user choosing to run a test"
        ikiwa self.running: rudisha
        ikiwa sio self.test_suite:
            self.errorDialog("Test Discovery", "You discover some tests first!")
            rudisha
        self.currentResult = GUITestResult(self)
        self.totalTests = self.test_suite.countTestCases()
        self.running = 1
        self.notifyRunning()
        self.test_suite.run(self.currentResult)
        self.running = 0
        self.notifyStopped()

    eleza stopClicked(self):
        "To be called kwenye response to user stopping the running of a test"
        ikiwa self.currentResult:
            self.currentResult.stop()

    eleza discoverClicked(self):
        self.__rollbackImporter.rollbackImports()
        directory = self.getDirectoryToDiscover()
        ikiwa sio directory:
            rudisha
        self.directory_to_read = directory
        jaribu:
            # Explicitly use 'Tupu' value ikiwa no top level directory is
            # specified (indicated by empty string) kama discover() explicitly
            # checks kila a 'Tupu' to determine ikiwa no tld has been specified
            top_level_dir = self.top_level_dir ama Tupu
            tests = unittest.defaultTestLoader.discover(directory, self.test_file_glob_pattern, top_level_dir)
            self.test_suite = tests
        tatizo:
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(*sys.exc_info())
            self.errorDialog("Unable to run test '%s'" % directory,
                             "Error loading specified test: %s, %s" % (exc_type, exc_value))
            rudisha
        self.notifyTestsDiscovered(self.test_suite)

    # Required callbacks

    eleza notifyTestsDiscovered(self, test_suite):
        "Override to display information about the suite of discovered tests"
        pita

    eleza notifyRunning(self):
        "Override to set GUI kwenye 'running' mode, enabling 'stop' button etc."
        pita

    eleza notifyStopped(self):
        "Override to set GUI kwenye 'stopped' mode, enabling 'run' button etc."
        pita

    eleza notifyTestFailed(self, test, err):
        "Override to indicate that a test has just failed"
        pita

    eleza notifyTestErrored(self, test, err):
        "Override to indicate that a test has just errored"
        pita

    eleza notifyTestSkipped(self, test, reason):
        "Override to indicate that test was skipped"
        pita

    eleza notifyTestFailedExpectedly(self, test, err):
        "Override to indicate that test has just failed expectedly"
        pita

    eleza notifyTestStarted(self, test):
        "Override to indicate that a test ni about to run"
        pita

    eleza notifyTestFinished(self, test):
        """Override to indicate that a test has finished (it may already have
           failed ama errored)"""
        pita


kundi GUITestResult(unittest.TestResult):
    """A TestResult that makes callbacks to its associated GUI TestRunner.
    Used by BaseGUITestRunner. Need sio be created directly.
    """
    eleza __init__(self, callback):
        unittest.TestResult.__init__(self)
        self.callback = callback

    eleza addError(self, test, err):
        unittest.TestResult.addError(self, test, err)
        self.callback.notifyTestErrored(test, err)

    eleza addFailure(self, test, err):
        unittest.TestResult.addFailure(self, test, err)
        self.callback.notifyTestFailed(test, err)

    eleza addSkip(self, test, reason):
        super(GUITestResult,self).addSkip(test, reason)
        self.callback.notifyTestSkipped(test, reason)

    eleza addExpectedFailure(self, test, err):
        super(GUITestResult,self).addExpectedFailure(test, err)
        self.callback.notifyTestFailedExpectedly(test, err)

    eleza stopTest(self, test):
        unittest.TestResult.stopTest(self, test)
        self.callback.notifyTestFinished(test)

    eleza startTest(self, test):
        unittest.TestResult.startTest(self, test)
        self.callback.notifyTestStarted(test)


kundi RollbackImporter:
    """This tricky little kundi ni used to make sure that modules under test
    will be reloaded the next time they are imported.
    """
    eleza __init__(self):
        self.previousModules = sys.modules.copy()

    eleza rollbackImports(self):
        kila modname kwenye sys.modules.copy().keys():
            ikiwa sio modname kwenye self.previousModules:
                # Force reload when modname next imported
                del(sys.modules[modname])


##############################################################################
# Tkinter GUI
##############################################################################

kundi DiscoverSettingsDialog(simpledialog.Dialog):
    """
    Dialog box kila prompting test discovery settings
    """

    eleza __init__(self, master, top_level_dir, test_file_glob_pattern, *args, **kwargs):
        self.top_level_dir = top_level_dir
        self.dirVar = tk.StringVar()
        self.dirVar.set(top_level_dir)

        self.test_file_glob_pattern = test_file_glob_pattern
        self.testPatternVar = tk.StringVar()
        self.testPatternVar.set(test_file_glob_pattern)

        simpledialog.Dialog.__init__(self, master, title="Discover Settings",
                                     *args, **kwargs)

    eleza body(self, master):
        tk.Label(master, text="Top Level Directory").grid(row=0)
        self.e1 = tk.Entry(master, textvariable=self.dirVar)
        self.e1.grid(row = 0, column=1)
        tk.Button(master, text="...",
                  command=lambda: self.selectDirClicked(master)).grid(row=0,column=3)

        tk.Label(master, text="Test File Pattern").grid(row=1)
        self.e2 = tk.Entry(master, textvariable = self.testPatternVar)
        self.e2.grid(row = 1, column=1)
        rudisha Tupu

    eleza selectDirClicked(self, master):
        dir_path = filedialog.askdirectory(parent=master)
        ikiwa dir_path:
            self.dirVar.set(dir_path)

    eleza apply(self):
        self.top_level_dir = self.dirVar.get()
        self.test_file_glob_pattern = self.testPatternVar.get()

kundi TkTestRunner(BaseGUITestRunner):
    """An implementation of BaseGUITestRunner using Tkinter.
    """
    eleza initGUI(self, root, initialTestName):
        """Set up the GUI inside the given root window. The test name entry
        field will be pre-filled ukijumuisha the given initialTestName.
        """
        self.root = root

        self.statusVar = tk.StringVar()
        self.statusVar.set("Idle")

        #tk vars kila tracking counts of test result types
        self.runCountVar = tk.IntVar()
        self.failCountVar = tk.IntVar()
        self.errorCountVar = tk.IntVar()
        self.skipCountVar = tk.IntVar()
        self.expectFailCountVar = tk.IntVar()
        self.remainingCountVar = tk.IntVar()

        self.top = tk.Frame()
        self.top.pack(fill=tk.BOTH, expand=1)
        self.createWidgets()

    eleza getDirectoryToDiscover(self):
        rudisha filedialog.askdirectory()

    eleza settingsClicked(self):
        d = DiscoverSettingsDialog(self.top, self.top_level_dir, self.test_file_glob_pattern)
        self.top_level_dir = d.top_level_dir
        self.test_file_glob_pattern = d.test_file_glob_pattern

    eleza notifyTestsDiscovered(self, test_suite):
        discovered = test_suite.countTestCases()
        self.runCountVar.set(0)
        self.failCountVar.set(0)
        self.errorCountVar.set(0)
        self.remainingCountVar.set(discovered)
        self.progressBar.setProgressFraction(0.0)
        self.errorListbox.delete(0, tk.END)
        self.statusVar.set("Discovering tests kutoka %s. Found: %s" %
            (self.directory_to_read, discovered))
        self.stopGoButton['state'] = tk.NORMAL

    eleza createWidgets(self):
        """Creates na packs the various widgets.

        Why ni it that GUI code always ends up looking a mess, despite all the
        best intentions to keep it tidy? Answers on a postcard, please.
        """
        # Status bar
        statusFrame = tk.Frame(self.top, relief=tk.SUNKEN, borderwidth=2)
        statusFrame.pack(anchor=tk.SW, fill=tk.X, side=tk.BOTTOM)
        tk.Label(statusFrame, width=1, textvariable=self.statusVar).pack(side=tk.TOP, fill=tk.X)

        # Area to enter name of test to run
        leftFrame = tk.Frame(self.top, borderwidth=3)
        leftFrame.pack(fill=tk.BOTH, side=tk.LEFT, anchor=tk.NW, expand=1)
        suiteNameFrame = tk.Frame(leftFrame, borderwidth=3)
        suiteNameFrame.pack(fill=tk.X)

        # Progress bar
        progressFrame = tk.Frame(leftFrame, relief=tk.GROOVE, borderwidth=2)
        progressFrame.pack(fill=tk.X, expand=0, anchor=tk.NW)
        tk.Label(progressFrame, text="Progress:").pack(anchor=tk.W)
        self.progressBar = ProgressBar(progressFrame, relief=tk.SUNKEN,
                                       borderwidth=2)
        self.progressBar.pack(fill=tk.X, expand=1)


        # Area ukijumuisha buttons to start/stop tests na quit
        buttonFrame = tk.Frame(self.top, borderwidth=3)
        buttonFrame.pack(side=tk.LEFT, anchor=tk.NW, fill=tk.Y)

        tk.Button(buttonFrame, text="Discover Tests",
                  command=self.discoverClicked).pack(fill=tk.X)


        self.stopGoButton = tk.Button(buttonFrame, text="Start",
                                      command=self.runClicked, state=tk.DISABLED)
        self.stopGoButton.pack(fill=tk.X)

        tk.Button(buttonFrame, text="Close",
                  command=self.top.quit).pack(side=tk.BOTTOM, fill=tk.X)
        tk.Button(buttonFrame, text="Settings",
                  command=self.settingsClicked).pack(side=tk.BOTTOM, fill=tk.X)

        # Area ukijumuisha labels reporting results
        kila label, var kwenye (('Run:', self.runCountVar),
                           ('Failures:', self.failCountVar),
                           ('Errors:', self.errorCountVar),
                           ('Skipped:', self.skipCountVar),
                           ('Expected Failures:', self.expectFailCountVar),
                           ('Remaining:', self.remainingCountVar),
                           ):
            tk.Label(progressFrame, text=label).pack(side=tk.LEFT)
            tk.Label(progressFrame, textvariable=var,
                     foreground="blue").pack(side=tk.LEFT, fill=tk.X,
                                             expand=1, anchor=tk.W)

        # List box showing errors na failures
        tk.Label(leftFrame, text="Failures na errors:").pack(anchor=tk.W)
        listFrame = tk.Frame(leftFrame, relief=tk.SUNKEN, borderwidth=2)
        listFrame.pack(fill=tk.BOTH, anchor=tk.NW, expand=1)
        self.errorListbox = tk.Listbox(listFrame, foreground='red',
                                       selectmode=tk.SINGLE,
                                       selectborderwidth=0)
        self.errorListbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=1,
                               anchor=tk.NW)
        listScroll = tk.Scrollbar(listFrame, command=self.errorListbox.yview)
        listScroll.pack(side=tk.LEFT, fill=tk.Y, anchor=tk.N)
        self.errorListbox.bind("<Double-1>",
                               lambda e, self=self: self.showSelectedError())
        self.errorListbox.configure(yscrollcommand=listScroll.set)

    eleza errorDialog(self, title, message):
        messagebox.showerror(parent=self.root, title=title,
                             message=message)

    eleza notifyRunning(self):
        self.runCountVar.set(0)
        self.failCountVar.set(0)
        self.errorCountVar.set(0)
        self.remainingCountVar.set(self.totalTests)
        self.errorInfo = []
        wakati self.errorListbox.size():
            self.errorListbox.delete(0)
        #Stopping seems sio to work, so simply disable the start button
        #self.stopGoButton.config(command=self.stopClicked, text="Stop")
        self.stopGoButton.config(state=tk.DISABLED)
        self.progressBar.setProgressFraction(0.0)
        self.top.update_idletasks()

    eleza notifyStopped(self):
        self.stopGoButton.config(state=tk.DISABLED)
        #self.stopGoButton.config(command=self.runClicked, text="Start")
        self.statusVar.set("Idle")

    eleza notifyTestStarted(self, test):
        self.statusVar.set(str(test))
        self.top.update_idletasks()

    eleza notifyTestFailed(self, test, err):
        self.failCountVar.set(1 + self.failCountVar.get())
        self.errorListbox.insert(tk.END, "Failure: %s" % test)
        self.errorInfo.append((test,err))

    eleza notifyTestErrored(self, test, err):
        self.errorCountVar.set(1 + self.errorCountVar.get())
        self.errorListbox.insert(tk.END, "Error: %s" % test)
        self.errorInfo.append((test,err))

    eleza notifyTestSkipped(self, test, reason):
        super(TkTestRunner, self).notifyTestSkipped(test, reason)
        self.skipCountVar.set(1 + self.skipCountVar.get())

    eleza notifyTestFailedExpectedly(self, test, err):
        super(TkTestRunner, self).notifyTestFailedExpectedly(test, err)
        self.expectFailCountVar.set(1 + self.expectFailCountVar.get())


    eleza notifyTestFinished(self, test):
        self.remainingCountVar.set(self.remainingCountVar.get() - 1)
        self.runCountVar.set(1 + self.runCountVar.get())
        fractionDone = float(self.runCountVar.get())/float(self.totalTests)
        fillColor = len(self.errorInfo) na "red" ama "green"
        self.progressBar.setProgressFraction(fractionDone, fillColor)

    eleza showSelectedError(self):
        selection = self.errorListbox.curselection()
        ikiwa sio selection: rudisha
        selected = int(selection[0])
        txt = self.errorListbox.get(selected)
        window = tk.Toplevel(self.root)
        window.title(txt)
        window.protocol('WM_DELETE_WINDOW', window.quit)
        test, error = self.errorInfo[selected]
        tk.Label(window, text=str(test),
                 foreground="red", justify=tk.LEFT).pack(anchor=tk.W)
        tracebackLines =  traceback.format_exception(*error)
        tracebackText = "".join(tracebackLines)
        tk.Label(window, text=tracebackText, justify=tk.LEFT).pack()
        tk.Button(window, text="Close",
                  command=window.quit).pack(side=tk.BOTTOM)
        window.bind('<Key-Return>', lambda e, w=window: w.quit())
        window.mainloop()
        window.destroy()


kundi ProgressBar(tk.Frame):
    """A simple progress bar that shows a percentage progress in
    the given colour."""

    eleza __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.canvas = tk.Canvas(self, height='20', width='60',
                                background='white', borderwidth=3)
        self.canvas.pack(fill=tk.X, expand=1)
        self.rect = self.text = Tupu
        self.canvas.bind('<Configure>', self.paint)
        self.setProgressFraction(0.0)

    eleza setProgressFraction(self, fraction, color='blue'):
        self.fraction = fraction
        self.color = color
        self.paint()
        self.canvas.update_idletasks()

    eleza paint(self, *args):
        totalWidth = self.canvas.winfo_width()
        width = int(self.fraction * float(totalWidth))
        height = self.canvas.winfo_height()
        ikiwa self.rect ni sio Tupu: self.canvas.delete(self.rect)
        ikiwa self.text ni sio Tupu: self.canvas.delete(self.text)
        self.rect = self.canvas.create_rectangle(0, 0, width, height,
                                                 fill=self.color)
        percentString = "%3.0f%%" % (100.0 * self.fraction)
        self.text = self.canvas.create_text(totalWidth/2, height/2,
                                            anchor=tk.CENTER,
                                            text=percentString)

eleza main(initialTestName=""):
    root = tk.Tk()
    root.title("PyUnit")
    runner = TkTestRunner(root, initialTestName)
    root.protocol('WM_DELETE_WINDOW', root.quit)
    root.mainloop()


ikiwa __name__ == '__main__':
    ikiwa len(sys.argv) == 2:
        main(sys.argv[1])
    isipokua:
        main()
