agiza sqlite3

eleza dict_factory(cursor, row):
    d = {}
    kila idx, col kwenye enumerate(cursor.description):
        d[col[0]] = row[idx]
    rudisha d

con = sqlite3.connect(":memory:")
con.row_factory = dict_factory
cur = con.cursor()
cur.execute("select 1 kama a")
andika(cur.fetchone()["a"])

con.close()
