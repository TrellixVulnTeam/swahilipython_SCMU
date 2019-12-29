#!/usr/bin/env python3
"""

         sorting_animation.py

A minimal sorting algorithm animation:
Sorts a shelf of 10 blocks using insertion
sort, selection sort na quicksort.

Shelfs are implemented using builtin lists.

Blocks are turtles with shape "square", but
stretched to rectangles by shapesize()
 ---------------------------------------
       To exit press space button
 ---------------------------------------
"""
kutoka turtle agiza *
agiza random


kundi Block(Turtle):

    eleza __init__(self, size):
        self.size = size
        Turtle.__init__(self, shape="square", visible=Uongo)
        self.pu()
        self.shapesize(size * 1.5, 1.5, 2) # square-->rectangle
        self.fillcolor("black")
        self.st()

    eleza glow(self):
        self.fillcolor("red")

    eleza unglow(self):
        self.fillcolor("black")

    eleza __repr__(self):
        rudisha "Block size: {0}".format(self.size)


kundi Shelf(list):

    eleza __init__(self, y):
        "create a shelf. y ni y-position of first block"
        self.y = y
        self.x = -150

    eleza push(self, d):
        width, _, _ = d.shapesize()
        # align blocks by the bottom edge
        y_offset = width / 2 * 20
        d.sety(self.y + y_offset)
        d.setx(self.x + 34 * len(self))
        self.append(d)

    eleza _close_gap_kutoka_i(self, i):
        kila b kwenye self[i:]:
            xpos, _ = b.pos()
            b.setx(xpos - 34)

    eleza _open_gap_kutoka_i(self, i):
        kila b kwenye self[i:]:
            xpos, _ = b.pos()
            b.setx(xpos + 34)

    eleza pop(self, key):
        b = list.pop(self, key)
        b.glow()
        b.sety(200)
        self._close_gap_kutoka_i(key)
        rudisha b

    eleza insert(self, key, b):
        self._open_gap_kutoka_i(key)
        list.insert(self, key, b)
        b.setx(self.x + 34 * key)
        width, _, _ = b.shapesize()
        # align blocks by the bottom edge
        y_offset = width / 2 * 20
        b.sety(self.y + y_offset)
        b.unglow()

eleza isort(shelf):
    length = len(shelf)
    kila i kwenye range(1, length):
        hole = i
        wakati hole > 0 na shelf[i].size < shelf[hole - 1].size:
            hole = hole - 1
        shelf.insert(hole, shelf.pop(i))
    rudisha

eleza ssort(shelf):
    length = len(shelf)
    kila j kwenye range(0, length - 1):
        imin = j
        kila i kwenye range(j + 1, length):
            ikiwa shelf[i].size < shelf[imin].size:
                imin = i
        ikiwa imin != j:
            shelf.insert(j, shelf.pop(imin))

eleza partition(shelf, left, right, pivot_index):
    pivot = shelf[pivot_index]
    shelf.insert(right, shelf.pop(pivot_index))
    store_index = left
    kila i kwenye range(left, right): # range ni non-inclusive of ending value
        ikiwa shelf[i].size < pivot.size:
            shelf.insert(store_index, shelf.pop(i))
            store_index = store_index + 1
    shelf.insert(store_index, shelf.pop(right)) # move pivot to correct position
    rudisha store_index

eleza qsort(shelf, left, right):
    ikiwa left < right:
        pivot_index = left
        pivot_new_index = partition(shelf, left, right, pivot_index)
        qsort(shelf, left, pivot_new_index - 1)
        qsort(shelf, pivot_new_index + 1, right)

eleza randomize():
    disable_keys()
    clear()
    target = list(range(10))
    random.shuffle(target)
    kila i, t kwenye enumerate(target):
        kila j kwenye range(i, len(s)):
            ikiwa s[j].size == t + 1:
                s.insert(i, s.pop(j))
    show_text(instructions1)
    show_text(instructions2, line=1)
    enable_keys()

eleza show_text(text, line=0):
    line = 20 * line
    goto(0,-250 - line)
    write(text, align="center", font=("Courier", 16, "bold"))

eleza start_ssort():
    disable_keys()
    clear()
    show_text("Selection Sort")
    ssort(s)
    clear()
    show_text(instructions1)
    show_text(instructions2, line=1)
    enable_keys()

eleza start_isort():
    disable_keys()
    clear()
    show_text("Insertion Sort")
    isort(s)
    clear()
    show_text(instructions1)
    show_text(instructions2, line=1)
    enable_keys()

eleza start_qsort():
    disable_keys()
    clear()
    show_text("Quicksort")
    qsort(s, 0, len(s) - 1)
    clear()
    show_text(instructions1)
    show_text(instructions2, line=1)
    enable_keys()

eleza init_shelf():
    global s
    s = Shelf(-200)
    vals = (4, 2, 8, 9, 1, 5, 10, 3, 7, 6)
    kila i kwenye vals:
        s.push(Block(i))

eleza disable_keys():
    onkey(Tupu, "s")
    onkey(Tupu, "i")
    onkey(Tupu, "q")
    onkey(Tupu, "r")

eleza enable_keys():
    onkey(start_isort, "i")
    onkey(start_ssort, "s")
    onkey(start_qsort, "q")
    onkey(randomize, "r")
    onkey(bye, "space")

eleza main():
    getscreen().clearscreen()
    ht(); penup()
    init_shelf()
    show_text(instructions1)
    show_text(instructions2, line=1)
    enable_keys()
    listen()
    rudisha "EVENTLOOP"

instructions1 = "press i kila insertion sort, s kila selection sort, q kila quicksort"
instructions2 = "spacebar to quit, r to randomize"

ikiwa __name__=="__main__":
    msg = main()
    mainloop()
