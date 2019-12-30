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
        jaribu:
            toa self.dict[str(window)]
        tatizo KeyError:
            # Sometimes, destroy() ni called twice
            pita
        self.call_callbacks()

    eleza add_windows_to_menu(self,  menu):
        list = []
        kila key kwenye self.dict:
            window = self.dict[key]
            jaribu:
                title = window.get_title()
            tatizo TclError:
                endelea
            list.append((title, key, window))
        list.sort()
        kila title, key, window kwenye list:
            menu.add_command(label=title, command=window.wakeup)

    eleza register_callback(self, callback):
        self.callbacks.append(callback)

    eleza unregister_callback(self, callback):
        jaribu:
            self.callbacks.remove(callback)
        tatizo ValueError:
            pita

    eleza call_callbacks(self):
        kila callback kwenye self.callbacks:
            jaribu:
                callback()
            tatizo:
                t, v, tb = sys.exc_info()
                andika("warning: callback failed kwenye WindowList", t, ":", v)


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
        # If this ni Idle's last window then quit the mainloop
        # (Needed kila clean exit on Windows 98)
        ikiwa sio registry.dict:
            self.quit()

    eleza update_windowlist_registry(self, window):
        registry.call_callbacks()

    eleza get_title(self):
        # Subkundi can override
        rudisha self.wm_title()

    eleza wakeup(self):
        jaribu:
            ikiwa self.wm_state() == "iconic":
                self.wm_withdraw()
                self.wm_deiconify()
            self.tkashiria()
            self.focused_widget.focus_set()
        tatizo TclError:
            # This can happen when the Window menu was torn off.
            # Simply ignore it.
            pita


ikiwa __name__ == "__main__":
    kutoka unittest agiza main
    main('idlelib.idle_test.test_window', verbosity=2)
