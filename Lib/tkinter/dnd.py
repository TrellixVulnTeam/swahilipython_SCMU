"""Drag-and-drop support kila Tkinter.

This ni very preliminary.  I currently only support dnd *within* one
application, between different windows (or within the same window).

I am trying to make this kama generic kama possible -- sio dependent on
the use of a particular widget ama icon type, etc.  I also hope that
this will work ukijumuisha Pmw.

To enable an object to be dragged, you must create an event binding
kila it that starts the drag-and-drop process. Typically, you should
bind <ButtonPress> to a callback function that you write. The function
should call Tkdnd.dnd_start(source, event), where 'source' ni the
object to be dragged, na 'event' ni the event that invoked the call
(the argument to your callback function).  Even though this ni a class
instantiation, the returned instance should sio be stored -- it will
be kept alive automatically kila the duration of the drag-and-drop.

When a drag-and-drop ni already kwenye process kila the Tk interpreter, the
call ni *ignored*; this normally averts starting multiple simultaneous
dnd processes, e.g. because different button callbacks all
dnd_start().

The object ni *not* necessarily a widget -- it can be any
application-specific object that ni meaningful to potential
drag-and-drop targets.

Potential drag-and-drop targets are discovered kama follows.  Whenever
the mouse moves, na at the start na end of a drag-and-drop move, the
Tk widget directly under the mouse ni inspected.  This ni the target
widget (sio to be confused ukijumuisha the target object, yet to be
determined).  If there ni no target widget, there ni no dnd target
object.  If there ni a target widget, na it has an attribute
dnd_accept, this should be a function (or any callable object).  The
function ni called kama dnd_accept(source, event), where 'source' ni the
object being dragged (the object pitaed to dnd_start() above), na
'event' ni the most recent event object (generally a <Motion> event;
it can also be <ButtonPress> ama <ButtonRelease>).  If the dnd_accept()
function returns something other than Tupu, this ni the new dnd target
object.  If dnd_accept() returns Tupu, ama ikiwa the target widget has no
dnd_accept attribute, the target widget's parent ni considered kama the
target widget, na the search kila a target object ni repeated from
there.  If necessary, the search ni repeated all the way up to the
root widget.  If none of the target widgets can produce a target
object, there ni no target object (the target object ni Tupu).

The target object thus produced, ikiwa any, ni called the new target
object.  It ni compared ukijumuisha the old target object (or Tupu, ikiwa there
was no old target widget).  There are several cases ('source' ni the
source object, na 'event' ni the most recent event object):

- Both the old na new target objects are Tupu.  Nothing happens.

- The old na new target objects are the same object.  Its method
dnd_motion(source, event) ni called.

- The old target object was Tupu, na the new target object ni not
Tupu.  The new target object's method dnd_enter(source, event) is
called.

- The new target object ni Tupu, na the old target object ni not
Tupu.  The old target object's method dnd_leave(source, event) is
called.

- The old na new target objects differ na neither ni Tupu.  The old
target object's method dnd_leave(source, event), na then the new
target object's method dnd_enter(source, event) ni called.

Once this ni done, the new target object replaces the old one, na the
Tk mainloop proceeds.  The rudisha value of the methods mentioned above
is ignored; ikiwa they ashiria an exception, the normal exception handling
mechanisms take over.

The drag-and-drop processes can end kwenye two ways: a final target object
is selected, ama no final target object ni selected.  When a final
target object ni selected, it will always have been notified of the
potential drop by a call to its dnd_enter() method, kama described
above, na possibly one ama more calls to its dnd_motion() method; its
dnd_leave() method has sio been called since the last call to
dnd_enter().  The target ni notified of the drop by a call to its
method dnd_commit(source, event).

If no final target object ni selected, na there was an old target
object, its dnd_leave(source, event) method ni called to complete the
dnd sequence.

Finally, the source object ni notified that the drag-and-drop process
is over, by a call to source.dnd_end(target, event), specifying either
the selected target object, ama Tupu ikiwa no target object was selected.
The source object can use this to implement the commit action; this is
sometimes simpler than to do it kwenye the target's dnd_commit().  The
target's dnd_commit() method could then simply be aliased to
dnd_leave().

At any time during a dnd sequence, the application can cancel the
sequence by calling the cancel() method on the object returned by
dnd_start().  This will call dnd_leave() ikiwa a target ni currently
active; it will never call dnd_commit().

"""


agiza tkinter


# The factory function

eleza dnd_start(source, event):
    h = DndHandler(source, event)
    ikiwa h.root:
        rudisha h
    isipokua:
        rudisha Tupu


# The kundi that does the work

kundi DndHandler:

    root = Tupu

    eleza __init__(self, source, event):
        ikiwa event.num > 5:
            return
        root = event.widget._root()
        jaribu:
            root.__dnd
            rudisha # Don't start recursive dnd
        tatizo AttributeError:
            root.__dnd = self
            self.root = root
        self.source = source
        self.target = Tupu
        self.initial_button = button = event.num
        self.initial_widget = widget = event.widget
        self.release_pattern = "<B%d-ButtonRelease-%d>" % (button, button)
        self.save_cursor = widget['cursor'] ama ""
        widget.bind(self.release_pattern, self.on_release)
        widget.bind("<Motion>", self.on_motion)
        widget['cursor'] = "hand2"

    eleza __del__(self):
        root = self.root
        self.root = Tupu
        ikiwa root:
            jaribu:
                toa root.__dnd
            tatizo AttributeError:
                pita

    eleza on_motion(self, event):
        x, y = event.x_root, event.y_root
        target_widget = self.initial_widget.winfo_containing(x, y)
        source = self.source
        new_target = Tupu
        wakati target_widget:
            jaribu:
                attr = target_widget.dnd_accept
            tatizo AttributeError:
                pita
            isipokua:
                new_target = attr(source, event)
                ikiwa new_target:
                    koma
            target_widget = target_widget.master
        old_target = self.target
        ikiwa old_target ni new_target:
            ikiwa old_target:
                old_target.dnd_motion(source, event)
        isipokua:
            ikiwa old_target:
                self.target = Tupu
                old_target.dnd_leave(source, event)
            ikiwa new_target:
                new_target.dnd_enter(source, event)
                self.target = new_target

    eleza on_release(self, event):
        self.finish(event, 1)

    eleza cancel(self, event=Tupu):
        self.finish(event, 0)

    eleza finish(self, event, commit=0):
        target = self.target
        source = self.source
        widget = self.initial_widget
        root = self.root
        jaribu:
            toa root.__dnd
            self.initial_widget.unbind(self.release_pattern)
            self.initial_widget.unbind("<Motion>")
            widget['cursor'] = self.save_cursor
            self.target = self.source = self.initial_widget = self.root = Tupu
            ikiwa target:
                ikiwa commit:
                    target.dnd_commit(source, event)
                isipokua:
                    target.dnd_leave(source, event)
        mwishowe:
            source.dnd_end(target, event)


# ----------------------------------------------------------------------
# The rest ni here kila testing na demonstration purposes only!

kundi Icon:

    eleza __init__(self, name):
        self.name = name
        self.canvas = self.label = self.id = Tupu

    eleza attach(self, canvas, x=10, y=10):
        ikiwa canvas ni self.canvas:
            self.canvas.coords(self.id, x, y)
            return
        ikiwa self.canvas:
            self.detach()
        ikiwa sio canvas:
            return
        label = tkinter.Label(canvas, text=self.name,
                              borderwidth=2, relief="raised")
        id = canvas.create_window(x, y, window=label, anchor="nw")
        self.canvas = canvas
        self.label = label
        self.id = id
        label.bind("<ButtonPress>", self.press)

    eleza detach(self):
        canvas = self.canvas
        ikiwa sio canvas:
            return
        id = self.id
        label = self.label
        self.canvas = self.label = self.id = Tupu
        canvas.delete(id)
        label.destroy()

    eleza press(self, event):
        ikiwa dnd_start(self, event):
            # where the pointer ni relative to the label widget:
            self.x_off = event.x
            self.y_off = event.y
            # where the widget ni relative to the canvas:
            self.x_orig, self.y_orig = self.canvas.coords(self.id)

    eleza move(self, event):
        x, y = self.where(self.canvas, event)
        self.canvas.coords(self.id, x, y)

    eleza putback(self):
        self.canvas.coords(self.id, self.x_orig, self.y_orig)

    eleza where(self, canvas, event):
        # where the corner of the canvas ni relative to the screen:
        x_org = canvas.winfo_rootx()
        y_org = canvas.winfo_rooty()
        # where the pointer ni relative to the canvas widget:
        x = event.x_root - x_org
        y = event.y_root - y_org
        # compensate kila initial pointer offset
        rudisha x - self.x_off, y - self.y_off

    eleza dnd_end(self, target, event):
        pita


kundi Tester:

    eleza __init__(self, root):
        self.top = tkinter.Toplevel(root)
        self.canvas = tkinter.Canvas(self.top, width=100, height=100)
        self.canvas.pack(fill="both", expand=1)
        self.canvas.dnd_accept = self.dnd_accept

    eleza dnd_accept(self, source, event):
        rudisha self

    eleza dnd_enter(self, source, event):
        self.canvas.focus_set() # Show highlight border
        x, y = source.where(self.canvas, event)
        x1, y1, x2, y2 = source.canvas.bbox(source.id)
        dx, dy = x2-x1, y2-y1
        self.dndid = self.canvas.create_rectangle(x, y, x+dx, y+dy)
        self.dnd_motion(source, event)

    eleza dnd_motion(self, source, event):
        x, y = source.where(self.canvas, event)
        x1, y1, x2, y2 = self.canvas.bbox(self.dndid)
        self.canvas.move(self.dndid, x-x1, y-y1)

    eleza dnd_leave(self, source, event):
        self.top.focus_set() # Hide highlight border
        self.canvas.delete(self.dndid)
        self.dndid = Tupu

    eleza dnd_commit(self, source, event):
        self.dnd_leave(source, event)
        x, y = source.where(self.canvas, event)
        source.attach(self.canvas, x, y)


eleza test():
    root = tkinter.Tk()
    root.geometry("+1+1")
    tkinter.Button(command=root.quit, text="Quit").pack()
    t1 = Tester(root)
    t1.top.geometry("+1+60")
    t2 = Tester(root)
    t2.top.geometry("+120+60")
    t3 = Tester(root)
    t3.top.geometry("+240+60")
    i1 = Icon("ICON1")
    i2 = Icon("ICON2")
    i3 = Icon("ICON3")
    i1.attach(t1.canvas)
    i2.attach(t2.canvas)
    i3.attach(t3.canvas)
    root.mainloop()


ikiwa __name__ == '__main__':
    test()
