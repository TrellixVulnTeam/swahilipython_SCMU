agiza sqlite3
agiza hashlib

eleza md5sum(t):
    rudisha hashlib.md5(t).hexdigest()

con = sqlite3.connect(":memory:")
con.create_function("md5", 1, md5sum)
cur = con.cursor()
cur.execute("select md5(?)", (b"foo",))
andika(cur.fetchone()[0])

con.close()
