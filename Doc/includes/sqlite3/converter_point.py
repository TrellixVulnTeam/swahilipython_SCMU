agiza sqlite3

kundi Point:
    eleza __init__(self, x, y):
        self.x, self.y = x, y

    eleza __repr__(self):
        rudisha "(%f;%f)" % (self.x, self.y)

eleza adapt_point(point):
    rudisha ("%f;%f" % (point.x, point.y)).encode('ascii')

eleza convert_point(s):
    x, y = list(map(float, s.split(b";")))
    rudisha Point(x, y)

# Register the adapter
sqlite3.register_adapter(Point, adapt_point)

# Register the converter
sqlite3.register_converter("point", convert_point)

p = Point(4.0, -3.2)

#########################
# 1) Using declared types
con = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
cur = con.cursor()
cur.execute("create table test(p point)")

cur.execute("insert into test(p) values (?)", (p,))
cur.execute("select p kutoka test")
andika("ukijumuisha declared types:", cur.fetchone()[0])
cur.close()
con.close()

#######################
# 1) Using column names
con = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_COLNAMES)
cur = con.cursor()
cur.execute("create table test(p)")

cur.execute("insert into test(p) values (?)", (p,))
cur.execute('select p kama "p [point]" kutoka test')
andika("ukijumuisha column names:", cur.fetchone()[0])
cur.close()
con.close()
