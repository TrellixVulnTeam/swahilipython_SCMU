agiza sqlite3

eleza collate_reverse(string1, string2):
    ikiwa string1 == string2:
        rudisha 0
    lasivyo string1 < string2:
        rudisha 1
    isipokua:
        rudisha -1

con = sqlite3.connect(":memory:")
con.create_collation("reverse", collate_reverse)

cur = con.cursor()
cur.execute("create table test(x)")
cur.executemany("insert into test(x) values (?)", [("a",), ("b",)])
cur.execute("select x kutoka test order by x collate reverse")
kila row kwenye cur:
    andika(row)
con.close()
