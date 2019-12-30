agiza sqlite3
agiza datetime

con = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
cur = con.cursor()
cur.execute("create table test(d date, ts timestamp)")

today = datetime.date.today()
now = datetime.datetime.now()

cur.execute("insert into test(d, ts) values (?, ?)", (today, now))
cur.execute("select d, ts kutoka test")
row = cur.fetchone()
andika(today, "=>", row[0], type(row[0]))
andika(now, "=>", row[1], type(row[1]))

cur.execute('select current_date kama "d [date]", current_timestamp kama "ts [timestamp]"')
row = cur.fetchone()
andika("current_date", row[0], type(row[0]))
andika("current_timestamp", row[1], type(row[1]))

con.close()
