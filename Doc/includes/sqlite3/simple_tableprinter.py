agiza sqlite3

FIELD_MAX_WIDTH = 20
TABLE_NAME = 'people'
SELECT = 'select * kutoka %s order by age, name_last' % TABLE_NAME

con = sqlite3.connect("mydb")

cur = con.cursor()
cur.execute(SELECT)

# Print a header.
kila fieldDesc kwenye cur.description:
    andika(fieldDesc[0].ljust(FIELD_MAX_WIDTH), end=' ')
andika() # Finish the header ukijumuisha a newline.
andika('-' * 78)

# For each row, andika the value of each field left-justified within
# the maximum possible width of that field.
fieldIndices = range(len(cur.description))
kila row kwenye cur:
    kila fieldIndex kwenye fieldIndices:
        fieldValue = str(row[fieldIndex])
        andika(fieldValue.ljust(FIELD_MAX_WIDTH), end=' ')

    andika() # Finish the row ukijumuisha a newline.

con.close()
