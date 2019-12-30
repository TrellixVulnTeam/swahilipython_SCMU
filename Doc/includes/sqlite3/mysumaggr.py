agiza sqlite3

kundi MySum:
    eleza __init__(self):
        self.count = 0

    eleza step(self, value):
        self.count += value

    eleza finalize(self):
        rudisha self.count

con = sqlite3.connect(":memory:")
con.create_aggregate("mysum", 1, MySum)
cur = con.cursor()
cur.execute("create table test(i)")
cur.execute("insert into test(i) values (1)")
cur.execute("insert into test(i) values (2)")
cur.execute("select mysum(i) kutoka test")
andika(cur.fetchone()[0])

con.close()
