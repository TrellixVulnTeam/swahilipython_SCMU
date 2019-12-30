# Simple example presenting how persistent ID can be used to pickle
# external objects by reference.

agiza pickle
agiza sqlite3
kutoka collections agiza namedtuple

# Simple kundi representing a record kwenye our database.
MemoRecord = namedtuple("MemoRecord", "key, task")

kundi DBPickler(pickle.Pickler):

    eleza persistent_id(self, obj):
        # Instead of pickling MemoRecord kama a regular kundi instance, we emit a
        # persistent ID.
        ikiwa isinstance(obj, MemoRecord):
            # Here, our persistent ID ni simply a tuple, containing a tag na a
            # key, which refers to a specific record kwenye the database.
            rudisha ("MemoRecord", obj.key)
        isipokua:
            # If obj does sio have a persistent ID, rudisha Tupu. This means obj
            # needs to be pickled kama usual.
            rudisha Tupu


kundi DBUnpickler(pickle.Unpickler):

    eleza __init__(self, file, connection):
        super().__init__(file)
        self.connection = connection

    eleza persistent_load(self, pid):
        # This method ni invoked whenever a persistent ID ni encountered.
        # Here, pid ni the tuple returned by DBPickler.
        cursor = self.connection.cursor()
        type_tag, key_id = pid
        ikiwa type_tag == "MemoRecord":
            # Fetch the referenced record kutoka the database na rudisha it.
            cursor.execute("SELECT * FROM memos WHERE key=?", (str(key_id),))
            key, task = cursor.fetchone()
            rudisha MemoRecord(key, task)
        isipokua:
            # Always raises an error ikiwa you cannot rudisha the correct object.
            # Otherwise, the unpickler will think Tupu ni the object referenced
            # by the persistent ID.
            ashiria pickle.UnpicklingError("unsupported persistent object")


eleza main():
    agiza io
    agiza pprint

    # Initialize na populate our database.
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE memos(key INTEGER PRIMARY KEY, task TEXT)")
    tasks = (
        'give food to fish',
        'prepare group meeting',
        'fight ukijumuisha a zebra',
        )
    kila task kwenye tasks:
        cursor.execute("INSERT INTO memos VALUES(NULL, ?)", (task,))

    # Fetch the records to be pickled.
    cursor.execute("SELECT * FROM memos")
    memos = [MemoRecord(key, task) kila key, task kwenye cursor]
    # Save the records using our custom DBPickler.
    file = io.BytesIO()
    DBPickler(file).dump(memos)

    andika("Pickled records:")
    pprint.pandika(memos)

    # Update a record, just kila good measure.
    cursor.execute("UPDATE memos SET task='learn italian' WHERE key=1")

    # Load the records kutoka the pickle data stream.
    file.seek(0)
    memos = DBUnpickler(file, conn).load()

    andika("Unpickled records:")
    pprint.pandika(memos)


ikiwa __name__ == '__main__':
    main()
