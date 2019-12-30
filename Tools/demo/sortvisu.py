#!/usr/bin/env python3

"""
Sorting algorithms visualizer using Tkinter.

This module ni comprised of three ``components'':

- an array visualizer ukijumuisha methods that implement basic sorting
operations (compare, swap) kama well kama methods kila ``annotating'' the
sorting algorithm (e.g. to show the pivot element);

- a number of sorting algorithms (currently quicksort, insertion sort,
selection sort na bubble sort, kama well kama a randomization function),
all using the array visualizer kila its basic operations na ukijumuisha calls
to its annotation methods;

- na a ``driver'' kundi which can be used kama a Grail applet ama kama a
stand-alone application.
"""

kutoka tkinter agiza *
agiza random

XGRID = 10
YGRID = 10
WIDTH = 6


kundi Array:

    kundi Cancelled(BaseException):
        pita

    eleza __init__(self, master, data=Tupu):
        self.master = master
        self.frame = Frame(self.master)
        self.frame.pack(fill=X)
        self.label = Label(self.frame)
        self.label.pack()
        self.canvas = Canvas(self.frame)
        self.canvas.pack()
        self.report = Label(self.frame)
        self.report.pack()
        self.left = self.canvas.create_line(0, 0, 0, 0)
        self.right = self.canvas.create_line(0, 0, 0, 0)
        self.pivot = self.canvas.create_line(0, 0, 0, 0)
        self.items = []
        self.size = self.maxvalue = 0
        ikiwa data:
            self.setdata(data)

    eleza setdata(self, data):
        olditems = self.items
        self.items = []
        kila item kwenye olditems:
            item.delete()
        self.size = len(data)
        self.maxvalue = max(data)
        self.canvas.config(width=(self.size+1)*XGRID,
                           height=(self.maxvalue+1)*YGRID)
        kila i kwenye range(self.size):
            self.items.append(ArrayItem(self, i, data[i]))
        self.reset("Sort demo, size %d" % self.size)

    speed = "normal"

    eleza setspeed(self, speed):
        self.speed = speed

    eleza destroy(self):
        self.frame.destroy()

    in_mainloop = 0
    stop_mainloop = 0

    eleza cancel(self):
        self.stop_mainloop = 1
        ikiwa self.in_mainloop:
            self.master.quit()

    eleza step(self):
        ikiwa self.in_mainloop:
            self.master.quit()

    eleza wait(self, msecs):
        ikiwa self.speed == "fastest":
            msecs = 0
        lasivyo self.speed == "fast":
            msecs = msecs//10
        lasivyo self.speed == "single-step":
            msecs = 1000000000
        ikiwa sio self.stop_mainloop:
            self.master.update()
            id = self.master.after(msecs, self.master.quit)
            self.in_mainloop = 1
            self.master.mainloop()
            self.master.after_cancel(id)
            self.in_mainloop = 0
        ikiwa self.stop_mainloop:
            self.stop_mainloop = 0
            self.message("Cancelled")
            ashiria Array.Cancelled

    eleza getsize(self):
        rudisha self.size

    eleza show_partition(self, first, last):
        kila i kwenye range(self.size):
            item = self.items[i]
            ikiwa first <= i < last:
                self.canvas.itemconfig(item, fill='red')
            isipokua:
                self.canvas.itemconfig(item, fill='orange')
        self.hide_left_right_pivot()

    eleza hide_partition(self):
        kila i kwenye range(self.size):
            item = self.items[i]
            self.canvas.itemconfig(item, fill='red')
        self.hide_left_right_pivot()

    eleza show_left(self, left):
        ikiwa sio 0 <= left < self.size:
            self.hide_left()
            rudisha
        x1, y1, x2, y2 = self.items[left].position()
##      top, bot = HIRO
        self.canvas.coords(self.left, (x1 - 2, 0, x1 - 2, 9999))
        self.master.update()

    eleza show_right(self, right):
        ikiwa sio 0 <= right < self.size:
            self.hide_right()
            rudisha
        x1, y1, x2, y2 = self.items[right].position()
        self.canvas.coords(self.right, (x2 + 2, 0, x2 + 2, 9999))
        self.master.update()

    eleza hide_left_right_pivot(self):
        self.hide_left()
        self.hide_right()
        self.hide_pivot()

    eleza hide_left(self):
        self.canvas.coords(self.left, (0, 0, 0, 0))

    eleza hide_right(self):
        self.canvas.coords(self.right, (0, 0, 0, 0))

    eleza show_pivot(self, pivot):
        x1, y1, x2, y2 = self.items[pivot].position()
        self.canvas.coords(self.pivot, (0, y1 - 2, 9999, y1 - 2))

    eleza hide_pivot(self):
        self.canvas.coords(self.pivot, (0, 0, 0, 0))

    eleza swap(self, i, j):
        ikiwa i == j: rudisha
        self.countswap()
        item = self.items[i]
        other = self.items[j]
        self.items[i], self.items[j] = other, item
        item.swapwith(other)

    eleza compare(self, i, j):
        self.countcompare()
        item = self.items[i]
        other = self.items[j]
        rudisha item.compareto(other)

    eleza reset(self, msg):
        self.ncompares = 0
        self.nswaps = 0
        self.message(msg)
        self.updatereport()
        self.hide_partition()

    eleza message(self, msg):
        self.label.config(text=msg)

    eleza countswap(self):
        self.nswaps = self.nswaps + 1
        self.updatereport()

    eleza countcompare(self):
        self.ncompares = self.ncompares + 1
        self.updatereport()

    eleza updatereport(self):
        text = "%d cmps, %d swaps" % (self.ncompares, self.nswaps)
        self.report.config(text=text)


kundi ArrayItem:

    eleza __init__(self, array, index, value):
        self.array = array
        self.index = index
        self.value = value
        self.canvas = array.canvas
        x1, y1, x2, y2 = self.position()
        self.item_id = array.canvas.create_rectangle(x1, y1, x2, y2,
            fill='red', outline='black', width=1)
        self.canvas.tag_bind(self.item_id, '<Button-1>', self.mouse_down)
        self.canvas.tag_bind(self.item_id, '<Button1-Motion>', self.mouse_move)
        self.canvas.tag_bind(self.item_id, '<ButtonRelease-1>', self.mouse_up)

    eleza delete(self):
        item_id = self.item_id
        self.array = Tupu
        self.item_id = Tupu
        self.canvas.delete(item_id)

    eleza mouse_down(self, event):
        self.lastx = event.x
        self.lasty = event.y
        self.origx = event.x
        self.origy = event.y
        self.canvas.tag_raise(self.item_id)

    eleza mouse_move(self, event):
        self.canvas.move(self.item_id,
                         event.x - self.lastx, event.y - self.lasty)
        self.lastx = event.x
        self.lasty = event.y

    eleza mouse_up(self, event):
        i = self.nearestindex(event.x)
        ikiwa i >= self.array.getsize():
            i = self.array.getsize() - 1
        ikiwa i < 0:
            i = 0
        other = self.array.items[i]
        here = self.index
        self.array.items[here], self.array.items[i] = other, self
        self.index = i
        x1, y1, x2, y2 = self.position()
        self.canvas.coords(self.item_id, (x1, y1, x2, y2))
        other.setindex(here)

    eleza setindex(self, index):
        nsteps = steps(self.index, index)
        ikiwa sio nsteps: rudisha
        ikiwa self.array.speed == "fastest":
            nsteps = 0
        oldpts = self.position()
        self.index = index
        newpts = self.position()
        trajectory = interpolate(oldpts, newpts, nsteps)
        self.canvas.tag_raise(self.item_id)
        kila pts kwenye trajectory:
            self.canvas.coords(self.item_id, pts)
            self.array.wait(50)

    eleza swapwith(self, other):
        nsteps = steps(self.index, other.index)
        ikiwa sio nsteps: rudisha
        ikiwa self.array.speed == "fastest":
            nsteps = 0
        myoldpts = self.position()
        otheroldpts = other.position()
        self.index, other.index = other.index, self.index
        mynewpts = self.position()
        othernewpts = other.position()
        myfill = self.canvas.itemcget(self.item_id, 'fill')
        otherfill = self.canvas.itemcget(other.item_id, 'fill')
        self.canvas.itemconfig(self.item_id, fill='green')
        self.canvas.itemconfig(other.item_id, fill='yellow')
        self.array.master.update()
        ikiwa self.array.speed == "single-step":
            self.canvas.coords(self.item_id, mynewpts)
            self.canvas.coords(other.item_id, othernewpts)
            self.array.master.update()
            self.canvas.itemconfig(self.item_id, fill=myfill)
            self.canvas.itemconfig(other.item_id, fill=otherfill)
            self.array.wait(0)
            rudisha
        mytrajectory = interpolate(myoldpts, mynewpts, nsteps)
        othertrajectory = interpolate(otheroldpts, othernewpts, nsteps)
        ikiwa self.value > other.value:
            self.canvas.tag_raise(self.item_id)
            self.canvas.tag_raise(other.item_id)
        isipokua:
            self.canvas.tag_raise(other.item_id)
            self.canvas.tag_raise(self.item_id)
        jaribu:
            kila i kwenye range(len(mytrajectory)):
                mypts = mytrajectory[i]
                otherpts = othertrajectory[i]
                self.canvas.coords(self.item_id, mypts)
                self.canvas.coords(other.item_id, otherpts)
                self.array.wait(50)
        mwishowe:
            mypts = mytrajectory[-1]
            otherpts = othertrajectory[-1]
            self.canvas.coords(self.item_id, mypts)
            self.canvas.coords(other.item_id, otherpts)
            self.canvas.itemconfig(self.item_id, fill=myfill)
            self.canvas.itemconfig(other.item_id, fill=otherfill)

    eleza compareto(self, other):
        myfill = self.canvas.itemcget(self.item_id, 'fill')
        otherfill = self.canvas.itemcget(other.item_id, 'fill')
        ikiwa self.value < other.value:
            myflash = 'white'
            otherflash = 'black'
            outcome = -1
        lasivyo self.value > other.value:
            myflash = 'black'
            otherflash = 'white'
            outcome = 1
        isipokua:
            myflash = otherflash = 'grey'
            outcome = 0
        jaribu:
            self.canvas.itemconfig(self.item_id, fill=myflash)
            self.canvas.itemconfig(other.item_id, fill=otherflash)
            self.array.wait(500)
        mwishowe:
            self.canvas.itemconfig(self.item_id, fill=myfill)
            self.canvas.itemconfig(other.item_id, fill=otherfill)
        rudisha outcome

    eleza position(self):
        x1 = (self.index+1)*XGRID - WIDTH//2
        x2 = x1+WIDTH
        y2 = (self.array.maxvalue+1)*YGRID
        y1 = y2 - (self.value)*YGRID
        rudisha x1, y1, x2, y2

    eleza nearestindex(self, x):
        rudisha int(round(float(x)/XGRID)) - 1


# Subroutines that don't need an object

eleza steps(here, there):
    nsteps = abs(here - there)
    ikiwa nsteps <= 3:
        nsteps = nsteps * 3
    lasivyo nsteps <= 5:
        nsteps = nsteps * 2
    lasivyo nsteps > 10:
        nsteps = 10
    rudisha nsteps

eleza interpolate(oldpts, newpts, n):
    ikiwa len(oldpts) != len(newpts):
        ashiria ValueError("can't interpolate arrays of different length")
    pts = [0]*len(oldpts)
    res = [tuple(oldpts)]
    kila i kwenye range(1, n):
        kila k kwenye range(len(pts)):
            pts[k] = oldpts[k] + (newpts[k] - oldpts[k])*i//n
        res.append(tuple(pts))
    res.append(tuple(newpts))
    rudisha res


# Various (un)sorting algorithms

eleza uniform(array):
    size = array.getsize()
    array.setdata([(size+1)//2] * size)
    array.reset("Uniform data, size %d" % size)

eleza distinct(array):
    size = array.getsize()
    array.setdata(range(1, size+1))
    array.reset("Distinct data, size %d" % size)

eleza randomize(array):
    array.reset("Randomizing")
    n = array.getsize()
    kila i kwenye range(n):
        j = random.randint(0, n-1)
        array.swap(i, j)
    array.message("Randomized")

eleza insertionsort(array):
    size = array.getsize()
    array.reset("Insertion sort")
    kila i kwenye range(1, size):
        j = i-1
        wakati j >= 0:
            ikiwa array.compare(j, j+1) <= 0:
                koma
            array.swap(j, j+1)
            j = j-1
    array.message("Sorted")

eleza selectionsort(array):
    size = array.getsize()
    array.reset("Selection sort")
    jaribu:
        kila i kwenye range(size):
            array.show_partition(i, size)
            kila j kwenye range(i+1, size):
                ikiwa array.compare(i, j) > 0:
                    array.swap(i, j)
        array.message("Sorted")
    mwishowe:
        array.hide_partition()

eleza bubblesort(array):
    size = array.getsize()
    array.reset("Bubble sort")
    kila i kwenye range(size):
        kila j kwenye range(1, size):
            ikiwa array.compare(j-1, j) > 0:
                array.swap(j-1, j)
    array.message("Sorted")

eleza quicksort(array):
    size = array.getsize()
    array.reset("Quicksort")
    jaribu:
        stack = [(0, size)]
        wakati stack:
            first, last = stack[-1]
            toa stack[-1]
            array.show_partition(first, last)
            ikiwa last-first < 5:
                array.message("Insertion sort")
                kila i kwenye range(first+1, last):
                    j = i-1
                    wakati j >= first:
                        ikiwa array.compare(j, j+1) <= 0:
                            koma
                        array.swap(j, j+1)
                        j = j-1
                endelea
            array.message("Choosing pivot")
            j, i, k = first, (first+last) // 2, last-1
            ikiwa array.compare(k, i) < 0:
                array.swap(k, i)
            ikiwa array.compare(k, j) < 0:
                array.swap(k, j)
            ikiwa array.compare(j, i) < 0:
                array.swap(j, i)
            pivot = j
            array.show_pivot(pivot)
            array.message("Pivot at left of partition")
            array.wait(1000)
            left = first
            right = last
            wakati 1:
                array.message("Sweep right pointer")
                right = right-1
                array.show_right(right)
                wakati right > first na array.compare(right, pivot) >= 0:
                    right = right-1
                    array.show_right(right)
                array.message("Sweep left pointer")
                left = left+1
                array.show_left(left)
                wakati left < last na array.compare(left, pivot) <= 0:
                    left = left+1
                    array.show_left(left)
                ikiwa left > right:
                    array.message("End of partition")
                    koma
                array.message("Swap items")
                array.swap(left, right)
            array.message("Swap pivot back")
            array.swap(pivot, right)
            n1 = right-first
            n2 = last-left
            ikiwa n1 > 1: stack.append((first, right))
            ikiwa n2 > 1: stack.append((left, last))
        array.message("Sorted")
    mwishowe:
        array.hide_partition()

eleza demosort(array):
    wakati 1:
        kila alg kwenye [quicksort, insertionsort, selectionsort, bubblesort]:
            randomize(array)
            alg(array)


# Sort demo kundi -- usable kama a Grail applet

kundi SortDemo:

    eleza __init__(self, master, size=15):
        self.master = master
        self.size = size
        self.busy = 0
        self.array = Array(self.master)

        self.botframe = Frame(master)
        self.botframe.pack(side=BOTTOM)
        self.botleftframe = Frame(self.botframe)
        self.botleftframe.pack(side=LEFT, fill=Y)
        self.botrightframe = Frame(self.botframe)
        self.botrightframe.pack(side=RIGHT, fill=Y)

        self.b_qsort = Button(self.botleftframe,
                              text="Quicksort", command=self.c_qsort)
        self.b_qsort.pack(fill=X)
        self.b_isort = Button(self.botleftframe,
                              text="Insertion sort", command=self.c_isort)
        self.b_isort.pack(fill=X)
        self.b_ssort = Button(self.botleftframe,
                              text="Selection sort", command=self.c_ssort)
        self.b_ssort.pack(fill=X)
        self.b_bsort = Button(self.botleftframe,
                              text="Bubble sort", command=self.c_bsort)
        self.b_bsort.pack(fill=X)

        # Terrible hack to overcome limitation of OptionMenu...
        kundi MyIntVar(IntVar):
            eleza __init__(self, master, demo):
                self.demo = demo
                IntVar.__init__(self, master)
            eleza set(self, value):
                IntVar.set(self, value)
                ikiwa str(value) != '0':
                    self.demo.resize(value)

        self.v_size = MyIntVar(self.master, self)
        self.v_size.set(size)
        sizes = [1, 2, 3, 4] + list(range(5, 55, 5))
        ikiwa self.size haiko kwenye sizes:
            sizes.append(self.size)
            sizes.sort()
        self.m_size = OptionMenu(self.botleftframe, self.v_size, *sizes)
        self.m_size.pack(fill=X)

        self.v_speed = StringVar(self.master)
        self.v_speed.set("normal")
        self.m_speed = OptionMenu(self.botleftframe, self.v_speed,
                                  "single-step", "normal", "fast", "fastest")
        self.m_speed.pack(fill=X)

        self.b_step = Button(self.botleftframe,
                             text="Step", command=self.c_step)
        self.b_step.pack(fill=X)

        self.b_randomize = Button(self.botrightframe,
                                  text="Randomize", command=self.c_randomize)
        self.b_randomize.pack(fill=X)
        self.b_uniform = Button(self.botrightframe,
                                  text="Uniform", command=self.c_uniform)
        self.b_uniform.pack(fill=X)
        self.b_distinct = Button(self.botrightframe,
                                  text="Distinct", command=self.c_distinct)
        self.b_distinct.pack(fill=X)
        self.b_demo = Button(self.botrightframe,
                             text="Demo", command=self.c_demo)
        self.b_demo.pack(fill=X)
        self.b_cancel = Button(self.botrightframe,
                               text="Cancel", command=self.c_cancel)
        self.b_cancel.pack(fill=X)
        self.b_cancel.config(state=DISABLED)
        self.b_quit = Button(self.botrightframe,
                             text="Quit", command=self.c_quit)
        self.b_quit.pack(fill=X)

    eleza resize(self, newsize):
        ikiwa self.busy:
            self.master.bell()
            rudisha
        self.size = newsize
        self.array.setdata(range(1, self.size+1))

    eleza c_qsort(self):
        self.run(quicksort)

    eleza c_isort(self):
        self.run(insertionsort)

    eleza c_ssort(self):
        self.run(selectionsort)

    eleza c_bsort(self):
        self.run(bubblesort)

    eleza c_demo(self):
        self.run(demosort)

    eleza c_randomize(self):
        self.run(randomize)

    eleza c_uniform(self):
        self.run(uniform)

    eleza c_distinct(self):
        self.run(distinct)

    eleza run(self, func):
        ikiwa self.busy:
            self.master.bell()
            rudisha
        self.busy = 1
        self.array.setspeed(self.v_speed.get())
        self.b_cancel.config(state=NORMAL)
        jaribu:
            func(self.array)
        tatizo Array.Cancelled:
            pita
        self.b_cancel.config(state=DISABLED)
        self.busy = 0

    eleza c_cancel(self):
        ikiwa sio self.busy:
            self.master.bell()
            rudisha
        self.array.cancel()

    eleza c_step(self):
        ikiwa sio self.busy:
            self.master.bell()
            rudisha
        self.v_speed.set("single-step")
        self.array.setspeed("single-step")
        self.array.step()

    eleza c_quit(self):
        ikiwa self.busy:
            self.array.cancel()
        self.master.after_idle(self.master.quit)


# Main program -- kila stand-alone operation outside Grail

eleza main():
    root = Tk()
    demo = SortDemo(root)
    root.protocol('WM_DELETE_WINDOW', demo.c_quit)
    root.mainloop()

ikiwa __name__ == '__main__':
    main()
