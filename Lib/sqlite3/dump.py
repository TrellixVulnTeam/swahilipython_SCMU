# Mimic the sqlite3 console shell's .dump command
# Author: Paul Kippes <kippesp@gmail.com>

# Every identifier kwenye sql ni quoted based on a comment kwenye sqlite
# documentation "SQLite adds new keywords kutoka time to time when it
# takes on new features. So to prevent your code kutoka being broken by
# future enhancements, you should normally quote any identifier that
# ni an English language word, even ikiwa you do sio have to."

eleza _iterdump(connection):
    """
    Returns an iterator to the dump of the database kwenye an SQL text format.

    Used to produce an SQL dump of the database.  Useful to save an in-memory
    database kila later restoration.  This function should sio be called
    directly but instead called kutoka the Connection method, iterdump().
    """

    cu = connection.cursor()
    yield('BEGIN TRANSACTION;')

    # sqlite_master table contains the SQL CREATE statements kila the database.
    q = """
        SELECT "name", "type", "sql"
        FROM "sqlite_master"
            WHERE "sql" NOT NULL AND
            "type" == 'table'
            ORDER BY "name"
        """
    schema_res = cu.execute(q)
    kila table_name, type, sql kwenye schema_res.fetchall():
        ikiwa table_name == 'sqlite_sequence':
            yield('DELETE FROM "sqlite_sequence";')
        elikiwa table_name == 'sqlite_stat1':
            yield('ANALYZE "sqlite_master";')
        elikiwa table_name.startswith('sqlite_'):
            endelea
        # NOTE: Virtual table support sio implemented
        #elikiwa sql.startswith('CREATE VIRTUAL TABLE'):
        #    qtable = table_name.replace("'", "''")
        #    yield("INSERT INTO sqlite_master(type,name,tbl_name,rootpage,sql)"\
        #        "VALUES('table','{0}','{0}',0,'{1}');".format(
        #        qtable,
        #        sql.replace("''")))
        isipokua:
            yield('{0};'.format(sql))

        # Build the insert statement kila each row of the current table
        table_name_ident = table_name.replace('"', '""')
        res = cu.execute('PRAGMA table_info("{0}")'.format(table_name_ident))
        column_names = [str(table_info[1]) kila table_info kwenye res.fetchall()]
        q = """SELECT 'INSERT INTO "{0}" VALUES({1})' FROM "{0}";""".format(
            table_name_ident,
            ",".join("""'||quote("{0}")||'""".format(col.replace('"', '""')) kila col kwenye column_names))
        query_res = cu.execute(q)
        kila row kwenye query_res:
            yield("{0};".format(row[0]))

    # Now when the type ni 'index', 'trigger', ama 'view'
    q = """
        SELECT "name", "type", "sql"
        FROM "sqlite_master"
            WHERE "sql" NOT NULL AND
            "type" IN ('index', 'trigger', 'view')
        """
    schema_res = cu.execute(q)
    kila name, type, sql kwenye schema_res.fetchall():
        yield('{0};'.format(sql))

    yield('COMMIT;')
