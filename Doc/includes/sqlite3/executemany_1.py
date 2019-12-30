agiza sqlite3

kundi IterChars:
    eleza __init__(self):
        self.count = ord('a')

    eleza __iter__(self):
        rudisha self

    eleza __next__(self):
        ikiwa self.count > ord('z'):
            ashiria StopIteration
        self.count += 1
        rudisha (chr(self.count - 1),) # this ni a 1-tuple

con = sqlite3.connect(":memory:")
cur = con.cursor()
cur.execute("create table characters(c)")

theIter = IterChars()
cur.executemany("insert into characters(c) values (?)", theIter)

cur.execute("select c kutoka characters")
andika(cur.fetchall())

con.close()
