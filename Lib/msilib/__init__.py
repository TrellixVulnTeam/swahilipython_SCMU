# Copyright (C) 2005 Martin v. Löwis
# Licensed to PSF under a Contributor Agreement.
kutoka _msi agiza *
agiza fnmatch
agiza os
agiza re
agiza string
agiza sys

AMD64 = "AMD64" kwenye sys.version
# Keep msilib.Win64 around to preserve backwards compatibility.
Win64 = AMD64

# Partially taken kutoka Wine
datasizemask=      0x00ff
type_valid=        0x0100
type_localizable=  0x0200

typemask=          0x0c00
type_long=         0x0000
type_short=        0x0400
type_string=       0x0c00
type_binary=       0x0800

type_nullable=     0x1000
type_key=          0x2000
# XXX temporary, localizable?
knownbits = datasizemask | type_valid | type_localizable | \
            typemask | type_nullable | type_key

kundi Table:
    eleza __init__(self, name):
        self.name = name
        self.fields = []

    eleza add_field(self, index, name, type):
        self.fields.append((index,name,type))

    eleza sql(self):
        fields = []
        keys = []
        self.fields.sort()
        fields = [Tupu]*len(self.fields)
        kila index, name, type kwenye self.fields:
            index -= 1
            unk = type & ~knownbits
            ikiwa unk:
                andika("%s.%s unknown bits %x" % (self.name, name, unk))
            size = type & datasizemask
            dtype = type & typemask
            ikiwa dtype == type_string:
                ikiwa size:
                    tname="CHAR(%d)" % size
                isipokua:
                    tname="CHAR"
            lasivyo dtype == type_short:
                assert size==2
                tname = "SHORT"
            lasivyo dtype == type_long:
                assert size==4
                tname="LONG"
            lasivyo dtype == type_binary:
                assert size==0
                tname="OBJECT"
            isipokua:
                tname="unknown"
                andika("%s.%sunknown integer type %d" % (self.name, name, size))
            ikiwa type & type_nullable:
                flags = ""
            isipokua:
                flags = " NOT NULL"
            ikiwa type & type_localizable:
                flags += " LOCALIZABLE"
            fields[index] = "`%s` %s%s" % (name, tname, flags)
            ikiwa type & type_key:
                keys.append("`%s`" % name)
        fields = ", ".join(fields)
        keys = ", ".join(keys)
        rudisha "CREATE TABLE %s (%s PRIMARY KEY %s)" % (self.name, fields, keys)

    eleza create(self, db):
        v = db.OpenView(self.sql())
        v.Execute(Tupu)
        v.Close()

kundi _Unspecified:pita
eleza change_sequence(seq, action, seqno=_Unspecified, cond = _Unspecified):
    "Change the sequence number of an action kwenye a sequence list"
    kila i kwenye range(len(seq)):
        ikiwa seq[i][0] == action:
            ikiwa cond ni _Unspecified:
                cond = seq[i][1]
            ikiwa seqno ni _Unspecified:
                seqno = seq[i][2]
            seq[i] = (action, cond, seqno)
            rudisha
    ashiria ValueError("Action sio found kwenye sequence")

eleza add_data(db, table, values):
    v = db.OpenView("SELECT * FROM `%s`" % table)
    count = v.GetColumnInfo(MSICOLINFO_NAMES).GetFieldCount()
    r = CreateRecord(count)
    kila value kwenye values:
        assert len(value) == count, value
        kila i kwenye range(count):
            field = value[i]
            ikiwa isinstance(field, int):
                r.SetInteger(i+1,field)
            lasivyo isinstance(field, str):
                r.SetString(i+1,field)
            lasivyo field ni Tupu:
                pita
            lasivyo isinstance(field, Binary):
                r.SetStream(i+1, field.name)
            isipokua:
                ashiria TypeError("Unsupported type %s" % field.__class__.__name__)
        jaribu:
            v.Modify(MSIMODIFY_INSERT, r)
        tatizo Exception kama e:
            ashiria MSIError("Could sio inert "+repr(values)+" into "+table)

        r.ClearData()
    v.Close()


eleza add_stream(db, name, path):
    v = db.OpenView("INSERT INTO _Streams (Name, Data) VALUES ('%s', ?)" % name)
    r = CreateRecord(1)
    r.SetStream(1, path)
    v.Execute(r)
    v.Close()

eleza init_database(name, schema,
                  ProductName, ProductCode, ProductVersion,
                  Manufacturer):
    jaribu:
        os.unlink(name)
    tatizo OSError:
        pita
    ProductCode = ProductCode.upper()
    # Create the database
    db = OpenDatabase(name, MSIDBOPEN_CREATE)
    # Create the tables
    kila t kwenye schema.tables:
        t.create(db)
    # Fill the validation table
    add_data(db, "_Validation", schema._Validation_records)
    # Initialize the summary information, allowing atmost 20 properties
    si = db.GetSummaryInformation(20)
    si.SetProperty(PID_TITLE, "Installation Database")
    si.SetProperty(PID_SUBJECT, ProductName)
    si.SetProperty(PID_AUTHOR, Manufacturer)
    ikiwa AMD64:
        si.SetProperty(PID_TEMPLATE, "x64;1033")
    isipokua:
        si.SetProperty(PID_TEMPLATE, "Intel;1033")
    si.SetProperty(PID_REVNUMBER, gen_uuid())
    si.SetProperty(PID_WORDCOUNT, 2) # long file names, compressed, original media
    si.SetProperty(PID_PAGECOUNT, 200)
    si.SetProperty(PID_APPNAME, "Python MSI Library")
    # XXX more properties
    si.Persist()
    add_data(db, "Property", [
        ("ProductName", ProductName),
        ("ProductCode", ProductCode),
        ("ProductVersion", ProductVersion),
        ("Manufacturer", Manufacturer),
        ("ProductLanguage", "1033")])
    db.Commit()
    rudisha db

eleza add_tables(db, module):
    kila table kwenye module.tables:
        add_data(db, table, getattr(module, table))

eleza make_id(str):
    identifier_chars = string.ascii_letters + string.digits + "._"
    str = "".join([c ikiwa c kwenye identifier_chars isipokua "_" kila c kwenye str])
    ikiwa str[0] kwenye (string.digits + "."):
        str = "_" + str
    assert re.match("^[A-Za-z_][A-Za-z0-9_.]*$", str), "FILE"+str
    rudisha str

eleza gen_uuid():
    rudisha "{"+UuidCreate().upper()+"}"

kundi CAB:
    eleza __init__(self, name):
        self.name = name
        self.files = []
        self.filenames = set()
        self.index = 0

    eleza gen_id(self, file):
        logical = _logical = make_id(file)
        pos = 1
        wakati logical kwenye self.filenames:
            logical = "%s.%d" % (_logical, pos)
            pos += 1
        self.filenames.add(logical)
        rudisha logical

    eleza append(self, full, file, logical):
        ikiwa os.path.isdir(full):
            rudisha
        ikiwa sio logical:
            logical = self.gen_id(file)
        self.index += 1
        self.files.append((full, logical))
        rudisha self.index, logical

    eleza commit(self, db):
        kutoka tempfile agiza mktemp
        filename = mktemp()
        FCICreate(filename, self.files)
        add_data(db, "Media",
                [(1, self.index, Tupu, "#"+self.name, Tupu, Tupu)])
        add_stream(db, self.name, filename)
        os.unlink(filename)
        db.Commit()

_directories = set()
kundi Directory:
    eleza __init__(self, db, cab, basedir, physical, _logical, default, componentflags=Tupu):
        """Create a new directory kwenye the Directory table. There ni a current component
        at each point kwenye time kila the directory, which ni either explicitly created
        through start_component, ama implicitly when files are added kila the first
        time. Files are added into the current component, na into the cab file.
        To create a directory, a base directory object needs to be specified (can be
        Tupu), the path to the physical directory, na a logical directory name.
        Default specifies the DefaultDir slot kwenye the directory table. componentflags
        specifies the default flags that new components get."""
        index = 1
        _logical = make_id(_logical)
        logical = _logical
        wakati logical kwenye _directories:
            logical = "%s%d" % (_logical, index)
            index += 1
        _directories.add(logical)
        self.db = db
        self.cab = cab
        self.basedir = basedir
        self.physical = physical
        self.logical = logical
        self.component = Tupu
        self.short_names = set()
        self.ids = set()
        self.keyfiles = {}
        self.componentflags = componentflags
        ikiwa basedir:
            self.absolute = os.path.join(basedir.absolute, physical)
            blogical = basedir.logical
        isipokua:
            self.absolute = physical
            blogical = Tupu
        add_data(db, "Directory", [(logical, blogical, default)])

    eleza start_component(self, component = Tupu, feature = Tupu, flags = Tupu, keyfile = Tupu, uuid=Tupu):
        """Add an entry to the Component table, na make this component the current kila this
        directory. If no component name ni given, the directory name ni used. If no feature
        ni given, the current feature ni used. If no flags are given, the directory's default
        flags are used. If no keyfile ni given, the KeyPath ni left null kwenye the Component
        table."""
        ikiwa flags ni Tupu:
            flags = self.componentflags
        ikiwa uuid ni Tupu:
            uuid = gen_uuid()
        isipokua:
            uuid = uuid.upper()
        ikiwa component ni Tupu:
            component = self.logical
        self.component = component
        ikiwa AMD64:
            flags |= 256
        ikiwa keyfile:
            keyid = self.cab.gen_id(keyfile)
            self.keyfiles[keyfile] = keyid
        isipokua:
            keyid = Tupu
        add_data(self.db, "Component",
                        [(component, uuid, self.logical, flags, Tupu, keyid)])
        ikiwa feature ni Tupu:
            feature = current_feature
        add_data(self.db, "FeatureComponents",
                        [(feature.id, component)])

    eleza make_short(self, file):
        oldfile = file
        file = file.replace('+', '_')
        file = ''.join(c kila c kwenye file ikiwa sio c kwenye r' "/\[]:;=,')
        parts = file.split(".")
        ikiwa len(parts) > 1:
            prefix = "".join(parts[:-1]).upper()
            suffix = parts[-1].upper()
            ikiwa sio prefix:
                prefix = suffix
                suffix = Tupu
        isipokua:
            prefix = file.upper()
            suffix = Tupu
        ikiwa len(parts) < 3 na len(prefix) <= 8 na file == oldfile na (
                                                sio suffix ama len(suffix) <= 3):
            ikiwa suffix:
                file = prefix+"."+suffix
            isipokua:
                file = prefix
        isipokua:
            file = Tupu
        ikiwa file ni Tupu ama file kwenye self.short_names:
            prefix = prefix[:6]
            ikiwa suffix:
                suffix = suffix[:3]
            pos = 1
            wakati 1:
                ikiwa suffix:
                    file = "%s~%d.%s" % (prefix, pos, suffix)
                isipokua:
                    file = "%s~%d" % (prefix, pos)
                ikiwa file haiko kwenye self.short_names: koma
                pos += 1
                assert pos < 10000
                ikiwa pos kwenye (10, 100, 1000):
                    prefix = prefix[:-1]
        self.short_names.add(file)
        assert sio re.search(r'[\?|><:/*"+,;=\[\]]', file) # restrictions on short names
        rudisha file

    eleza add_file(self, file, src=Tupu, version=Tupu, language=Tupu):
        """Add a file to the current component of the directory, starting a new one
        ikiwa there ni no current component. By default, the file name kwenye the source
        na the file table will be identical. If the src file ni specified, it is
        interpreted relative to the current directory. Optionally, a version na a
        language can be specified kila the entry kwenye the File table."""
        ikiwa sio self.component:
            self.start_component(self.logical, current_feature, 0)
        ikiwa sio src:
            # Allow relative paths kila file ikiwa src ni sio specified
            src = file
            file = os.path.basename(file)
        absolute = os.path.join(self.absolute, src)
        assert sio re.search(r'[\?|><:/*]"', file) # restrictions on long names
        ikiwa file kwenye self.keyfiles:
            logical = self.keyfiles[file]
        isipokua:
            logical = Tupu
        sequence, logical = self.cab.append(absolute, file, logical)
        assert logical haiko kwenye self.ids
        self.ids.add(logical)
        short = self.make_short(file)
        full = "%s|%s" % (short, file)
        filesize = os.stat(absolute).st_size
        # constants.msidbFileAttributesVital
        # Compressed omitted, since it ni the database default
        # could add r/o, system, hidden
        attributes = 512
        add_data(self.db, "File",
                        [(logical, self.component, full, filesize, version,
                         language, attributes, sequence)])
        #ikiwa sio version:
        #    # Add hash ikiwa the file ni sio versioned
        #    filehash = FileHash(absolute, 0)
        #    add_data(self.db, "MsiFileHash",
        #             [(logical, 0, filehash.IntegerData(1),
        #               filehash.IntegerData(2), filehash.IntegerData(3),
        #               filehash.IntegerData(4))])
        # Automatically remove .pyc files on uninstall (2)
        # XXX: adding so many RemoveFile entries makes installer unbelievably
        # slow. So instead, we have to use wildcard remove entries
        ikiwa file.endswith(".py"):
            add_data(self.db, "RemoveFile",
                      [(logical+"c", self.component, "%sC|%sc" % (short, file),
                        self.logical, 2),
                       (logical+"o", self.component, "%sO|%so" % (short, file),
                        self.logical, 2)])
        rudisha logical

    eleza glob(self, pattern, exclude = Tupu):
        """Add a list of files to the current component kama specified kwenye the
        glob pattern. Individual files can be excluded kwenye the exclude list."""
        jaribu:
            files = os.listdir(self.absolute)
        tatizo OSError:
            rudisha []
        ikiwa pattern[:1] != '.':
            files = (f kila f kwenye files ikiwa f[0] != '.')
        files = fnmatch.filter(files, pattern)
        kila f kwenye files:
            ikiwa exclude na f kwenye exclude: endelea
            self.add_file(f)
        rudisha files

    eleza remove_pyc(self):
        "Remove .pyc files on uninstall"
        add_data(self.db, "RemoveFile",
                 [(self.component+"c", self.component, "*.pyc", self.logical, 2)])

kundi Binary:
    eleza __init__(self, fname):
        self.name = fname
    eleza __repr__(self):
        rudisha 'msilib.Binary(os.path.join(dirname,"%s"))' % self.name

kundi Feature:
    eleza __init__(self, db, id, title, desc, display, level = 1,
                 parent=Tupu, directory = Tupu, attributes=0):
        self.id = id
        ikiwa parent:
            parent = parent.id
        add_data(db, "Feature",
                        [(id, parent, title, desc, display,
                          level, directory, attributes)])
    eleza set_current(self):
        global current_feature
        current_feature = self

kundi Control:
    eleza __init__(self, dlg, name):
        self.dlg = dlg
        self.name = name

    eleza event(self, event, argument, condition = "1", ordering = Tupu):
        add_data(self.dlg.db, "ControlEvent",
                 [(self.dlg.name, self.name, event, argument,
                   condition, ordering)])

    eleza mapping(self, event, attribute):
        add_data(self.dlg.db, "EventMapping",
                 [(self.dlg.name, self.name, event, attribute)])

    eleza condition(self, action, condition):
        add_data(self.dlg.db, "ControlCondition",
                 [(self.dlg.name, self.name, action, condition)])

kundi RadioButtonGroup(Control):
    eleza __init__(self, dlg, name, property):
        self.dlg = dlg
        self.name = name
        self.property = property
        self.index = 1

    eleza add(self, name, x, y, w, h, text, value = Tupu):
        ikiwa value ni Tupu:
            value = name
        add_data(self.dlg.db, "RadioButton",
                 [(self.property, self.index, value,
                   x, y, w, h, text, Tupu)])
        self.index += 1

kundi Dialog:
    eleza __init__(self, db, name, x, y, w, h, attr, title, first, default, cancel):
        self.db = db
        self.name = name
        self.x, self.y, self.w, self.h = x,y,w,h
        add_data(db, "Dialog", [(name, x,y,w,h,attr,title,first,default,cancel)])

    eleza control(self, name, type, x, y, w, h, attr, prop, text, next, help):
        add_data(self.db, "Control",
                 [(self.name, name, type, x, y, w, h, attr, prop, text, next, help)])
        rudisha Control(self, name)

    eleza text(self, name, x, y, w, h, attr, text):
        rudisha self.control(name, "Text", x, y, w, h, attr, Tupu,
                     text, Tupu, Tupu)

    eleza bitmap(self, name, x, y, w, h, text):
        rudisha self.control(name, "Bitmap", x, y, w, h, 1, Tupu, text, Tupu, Tupu)

    eleza line(self, name, x, y, w, h):
        rudisha self.control(name, "Line", x, y, w, h, 1, Tupu, Tupu, Tupu, Tupu)

    eleza pushbutton(self, name, x, y, w, h, attr, text, next):
        rudisha self.control(name, "PushButton", x, y, w, h, attr, Tupu, text, next, Tupu)

    eleza radiogroup(self, name, x, y, w, h, attr, prop, text, next):
        add_data(self.db, "Control",
                 [(self.name, name, "RadioButtonGroup",
                   x, y, w, h, attr, prop, text, next, Tupu)])
        rudisha RadioButtonGroup(self, name, prop)

    eleza checkbox(self, name, x, y, w, h, attr, prop, text, next):
        rudisha self.control(name, "CheckBox", x, y, w, h, attr, prop, text, next, Tupu)
