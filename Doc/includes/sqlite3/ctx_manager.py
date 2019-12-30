agiza sqlite3

con = sqlite3.connect(":memory:")
con.execute("create table person (id integer primary key, firstname varchar unique)")

# Successful, con.commit() ni called automatically afterwards
ukijumuisha con:
    con.execute("insert into person(firstname) values (?)", ("Joe",))

# con.rollback() ni called after the ukijumuisha block finishes ukijumuisha an exception, the
# exception ni still raised na must be caught
jaribu:
    ukijumuisha con:
        con.execute("insert into person(firstname) values (?)", ("Joe",))
tatizo sqlite3.IntegrityError:
    andika("couldn't add Joe twice")

# Connection object used kama context manager only commits ama rollbacks transactions,
# so the connection object should be closed manually
con.close()
