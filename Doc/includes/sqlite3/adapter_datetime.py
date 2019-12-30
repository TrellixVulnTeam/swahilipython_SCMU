agiza sqlite3
agiza datetime
agiza time

eleza adapt_datetime(ts):
    rudisha time.mktime(ts.timetuple())

sqlite3.register_adapter(datetime.datetime, adapt_datetime)

con = sqlite3.connect(":memory:")
cur = con.cursor()

now = datetime.datetime.now()
cur.execute("select ?", (now,))
andika(cur.fetchone()[0])

con.close()
