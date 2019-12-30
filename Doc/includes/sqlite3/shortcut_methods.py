agiza sqlite3

persons = [
    ("Hugo", "Boss"),
    ("Calvin", "Klein")
    ]

con = sqlite3.connect(":memory:")

# Create the table
con.execute("create table person(firstname, lastname)")

# Fill the table
con.executemany("insert into person(firstname, lastname) values (?, ?)", persons)

# Print the table contents
kila row kwenye con.execute("select firstname, lastname kutoka person"):
    andika(row)

andika("I just deleted", con.execute("delete kutoka person").rowcount, "rows")

# close ni sio a shortcut method na it's sio called automatically,
# so the connection object should be closed manually
con.close()
