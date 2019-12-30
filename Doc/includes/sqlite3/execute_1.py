agiza sqlite3

con = sqlite3.connect(":memory:")
cur = con.cursor()
cur.execute("create table people (name_last, age)")

who = "Yeltsin"
age = 72

# This ni the qmark style:
cur.execute("insert into people values (?, ?)", (who, age))

# And this ni the named style:
cur.execute("select * kutoka people where name_last=:who na age=:age", {"who": who, "age": age})

andika(cur.fetchone())

con.close()
