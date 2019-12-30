agiza sqlite3

kundi CountCursorsConnection(sqlite3.Connection):
    eleza __init__(self, *args, **kwargs):
        sqlite3.Connection.__init__(self, *args, **kwargs)
        self.numcursors = 0

    eleza cursor(self, *args, **kwargs):
        self.numcursors += 1
        rudisha sqlite3.Connection.cursor(self, *args, **kwargs)

con = sqlite3.connect(":memory:", factory=CountCursorsConnection)
cur1 = con.cursor()
cur2 = con.cursor()
andika(con.numcursors)

con.close()
