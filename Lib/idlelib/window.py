kutoka tkinter agiza Toplevel, TclError
agiza sys


kundi WindowList:

    eleza __init__(self):
        self.dict = {}
        self.callbacks = []

    eleza add(self, window):
        window.after_idle(self.call_callbacks)
        self.dict[str(window)] = window

    eleza delete(self, window):
        try:
            del self.dict[str(window)]
        except KeyError:
            # Sometimes, destroy() is called twice
            pass
        self.call_callbacks()

    eleza add_windows_to_menu(self,  menu):
        list = []
        for key in self.dict:
            window = self.dict[key]
            try:
                title = window.get_title()
            except TclError:
                continue
            list.append((title, key, window))
        list.sort()
        for title, key, window in list:
            menu.add_command(label=title, command=window.wakeup)

    eleza register_callback(self, callback):
        self.callbacks.append(callback)

    eleza unregister_callback(self, callback):
        try:
            self.callbacks.remove(callback)
        except ValueError:
            pass

    eleza call_callbacks(self):
        for callback in self.callbacks:
            try:
                callback()
            except:
                t, v, tb = sys.exc_info()
                andika("warning: callback failed in WindowList", t, ":", v)


registry = WindowList()

add_windows_to_menu = registry.add_windows_to_menu
register_callback = registry.register_callback
unregister_callback = registry.unregister_callback


kundi ListedToplevel(Toplevel):

    eleza __init__(self, master, **kw):
        Toplevel.__init__(self, master, kw)
        registry.add(self)
        self.focused_widget = self

    eleza destroy(self):
        registry.delete(self)
        Toplevel.destroy(self)
        # If this is Idle's last window then quit the mainloop
        # (Needed for clean exit on Windows 98)
        ikiwa not registry.dict:
            self.quit()

    eleza update_windowlist_registry(self, window):
        registry.call_callbacks()

    eleza get_title(self):
        # Subkundi can override
        rudisha self.wm_title()

    eleza wakeup(self):
        try:
            ikiwa self.wm_state() == "iconic":
                self.wm_withdraw()
                self.wm_deiconify()
            self.tkraise()
            self.focused_widget.focus_set()
        except TclError:
            # This can happen when the Window menu was torn off.
            # Simply ignore it.
            pass


ikiwa __name__ == "__main__":
    kutoka unittest agiza main
    main('idlelib.idle_test.test_window', verbosity=2)
