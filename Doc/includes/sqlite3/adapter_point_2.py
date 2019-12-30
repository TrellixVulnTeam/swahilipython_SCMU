agiza sqlite3

kundi Point:
    eleza __init__(self, x, y):
        self.x, self.y = x, y

eleza adapt_point(point):
    rudisha "%f;%f" % (point.x, point.y)

sqlite3.register_adapter(Point, adapt_point)

con = sqlite3.connect(":memory:")
cur = con.cursor()

p = Point(4.0, -3.2)
cur.execute("select ?", (p,))
andika(cur.fetchone()[0])

con.close()
