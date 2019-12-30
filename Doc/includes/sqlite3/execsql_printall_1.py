agiza sqlite3

# Create a connection to the database file "mydb":
con = sqlite3.connect("mydb")

# Get a Cursor object that operates kwenye the context of Connection con:
cur = con.cursor()

# Execute the SELECT statement:
cur.execute("select * kutoka people order by age")

# Retrieve all rows kama a sequence na andika that sequence:
andika(cur.fetchall())

con.close()
