agiza sqlite3
agiza string

eleza char_generator():
    kila c kwenye string.ascii_lowercase:
        tuma (c,)

con = sqlite3.connect(":memory:")
cur = con.cursor()
cur.execute("create table characters(c)")

cur.executemany("insert into characters(c) values (?)", char_generator())

cur.execute("select c kutoka characters")
andika(cur.fetchall())

con.close()
