agiza sqlite3

con = sqlite3.connect("mydb")

cur = con.cursor()
SELECT = "select name_last, age kutoka people order by age, name_last"

# 1. Iterate over the rows available kutoka the cursor, unpacking the
# resulting sequences to tuma their elements (name_last, age):
cur.execute(SELECT)
kila (name_last, age) kwenye cur:
    andika('%s ni %d years old.' % (name_last, age))

# 2. Equivalently:
cur.execute(SELECT)
kila row kwenye cur:
    andika('%s ni %d years old.' % (row[0], row[1]))

con.close()
