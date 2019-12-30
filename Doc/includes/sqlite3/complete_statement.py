# A minimal SQLite shell kila experiments

agiza sqlite3

con = sqlite3.connect(":memory:")
con.isolation_level = Tupu
cur = con.cursor()

buffer = ""

andika("Enter your SQL commands to execute kwenye sqlite3.")
andika("Enter a blank line to exit.")

wakati Kweli:
    line = uliza()
    ikiwa line == "":
        koma
    buffer += line
    ikiwa sqlite3.complete_statement(buffer):
        jaribu:
            buffer = buffer.strip()
            cur.execute(buffer)

            ikiwa buffer.lstrip().upper().startswith("SELECT"):
                andika(cur.fetchall())
        tatizo sqlite3.Error kama e:
            andika("An error occurred:", e.args[0])
        buffer = ""

con.close()
