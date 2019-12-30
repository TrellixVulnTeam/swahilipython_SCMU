agiza sqlite3

con = sqlite3.connect("mydb")

cur = con.cursor()

newPeople = (
    ('Lebed'       , 53),
    ('Zhirinovsky' , 57),
  )

kila person kwenye newPeople:
    cur.execute("insert into people (name_last, age) values (?, ?)", person)

# The changes will sio be saved unless the transaction ni committed explicitly:
con.commit()

con.close()
