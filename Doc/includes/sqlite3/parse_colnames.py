agiza sqlite3
agiza datetime

con = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_COLNAMES)
cur = con.cursor()
cur.execute('select ? kama "x [timestamp]"', (datetime.datetime.now(),))
dt = cur.fetchone()[0]
andika(dt, type(dt))

con.close()
