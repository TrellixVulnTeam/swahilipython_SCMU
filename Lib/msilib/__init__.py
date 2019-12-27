# Copyright (C) 2005 Martin v. Löwis
# Licensed to PSF under a Contributor Agreement.
kutoka _msi agiza *
agiza fnmatch
agiza os
agiza re
agiza string
agiza sys

AMD64 = "AMD64" in sys.version
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
        fields = [None]*len(self.fields)
        for index, name, type in self.fields:
            index -= 1
            unk = type & ~knownbits
            ikiwa unk:
                andika("%s.%s unknown bits %x" % (self.name, name, unk))
            size = type & datasizemask
            dtype = type & typemask
            ikiwa dtype == type_string:
                ikiwa size:
                    tname="CHAR(%d)" % size
                else:
                    tname="CHAR"
            elikiwa dtype == type_short:
                assert size==2
                tname = "SHORT"
            elikiwa dtype == type_long:
                assert size==4
                tname="LONG"
            elikiwa dtype == type_binary:
                assert size==0
                tname="OBJECT"
            else:
                tname="unknown"
                andika("%s.%sunknown integer type %d" % (self.name, name, size))
            ikiwa type & type_nullable:
                flags = ""
            else:
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
        v.Execute(None)
        v.Close()

kundi _Unspecified:pass
eleza change_sequence(seq, action, seqno=_Unspecified, cond = _Unspecified):
    "Change the sequence number of an action in a sequence list"
    for i in range(len(seq)):
        ikiwa seq[i][0] == action:
            ikiwa cond is _Unspecified:
                cond = seq[i][1]
            ikiwa seqno is _Unspecified:
                seqno = seq[i][2]
            seq[i] = (action, cond, seqno)
            return
    raise ValueError("Action not found in sequence")

eleza add_data(db, table, values):
    v = db.OpenView("SELECT * FROM `%s`" % table)
    count = v.GetColumnInfo(MSICOLINFO_NAMES).GetFieldCount()
    r = CreateRecord(count)
    for value in values:
        assert len(value) == count, value
        for i in range(count):
            field = value[i]
            ikiwa isinstance(field, int):
                r.SetInteger(i+1,field)
            elikiwa isinstance(field, str):
                r.SetString(i+1,field)
            elikiwa field is None:
                pass
            elikiwa isinstance(field, Binary):
                r.SetStream(i+1, field.name)
            else:
                raise TypeError("Unsupported type %s" % field.__class__.__name__)
        try:
            v.Modify(MSIMODIFY_INSERT, r)
        except Exception as e:
            raise MSIError("Could not insert "+repr(values)+" into "+table)

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
    try:
        os.unlink(name)
    except OSError:
        pass
    ProductCode = ProductCode.upper()
    # Create the database
    db = OpenDatabase(name, MSIDBOPEN_CREATE)
    # Create the tables
    for t in schema.tables:
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
    else:
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
    for table in module.tables:
        add_data(db, table, getattr(module, table))

eleza make_id(str):
    identifier_chars = string.ascii_letters + string.digits + "._"
    str = "".join([c ikiwa c in identifier_chars else "_" for c in str])
    ikiwa str[0] in (string.digits + "."):
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
        while logical in self.filenames:
            logical = "%s.%d" % (_logical, pos)
            pos += 1
        self.filenames.add(logical)
        rudisha logical

    eleza append(self, full, file, logical):
        ikiwa os.path.isdir(full):
            return
        ikiwa not logical:
            logical = self.gen_id(file)
        self.index += 1
        self.files.append((full, logical))
        rudisha self.index, logical

    eleza commit(self, db):
        kutoka tempfile agiza mktemp
        filename = mktemp()
        FCICreate(filename, self.files)
        add_data(db, "Media",
                [(1, self.index, None, "#"+self.name, None, None)])
        add_stream(db, self.name, filename)
        os.unlink(filename)
        db.Commit()

_directories = set()
kundi Directory:
    eleza __init__(self, db, cab, basedir, physical, _logical, default, componentflags=None):
        """Create a new directory in the Directory table. There is a current component
        at each point in time for the directory, which is either explicitly created
        through start_component, or implicitly when files are added for the first
        time. Files are added into the current component, and into the cab file.
        To create a directory, a base directory object needs to be specified (can be
        None), the path to the physical directory, and a logical directory name.
        Default specifies the DefaultDir slot in the directory table. componentflags
        specifies the default flags that new components get."""
        index = 1
        _logical = make_id(_logical)
        logical = _logical
        while logical in _directories:
            logical = "%s%d" % (_logical, index)
            index += 1
        _directories.add(logical)
        self.db = db
        self.cab = cab
        self.basedir = basedir
        self.physical = physical
        self.logical = logical
        self.component = None
        self.short_names = set()
        self.ids = set()
        self.keyfiles = {}
        self.componentflags = componentflags
        ikiwa basedir:
            self.absolute = os.path.join(basedir.absolute, physical)
            blogical = basedir.logical
        else:
            self.absolute = physical
            blogical = None
        add_data(db, "Directory", [(logical, blogical, default)])

    eleza start_component(self, component = None, feature = None, flags = None, keyfile = None, uuid=None):
        """Add an entry to the Component table, and make this component the current for this
        directory. If no component name is given, the directory name is used. If no feature
        is given, the current feature is used. If no flags are given, the directory's default
        flags are used. If no keyfile is given, the KeyPath is left null in the Component
        table."""
        ikiwa flags is None:
            flags = self.componentflags
        ikiwa uuid is None:
            uuid = gen_uuid()
        else:
            uuid = uuid.upper()
        ikiwa component is None:
            component = self.logical
        self.component = component
        ikiwa AMD64:
            flags |= 256
        ikiwa keyfile:
            keyid = self.cab.gen_id(keyfile)
            self.keyfiles[keyfile] = keyid
        else:
            keyid = None
        add_data(self.db, "Component",
                        [(component, uuid, self.logical, flags, None, keyid)])
        ikiwa feature is None:
            feature = current_feature
        add_data(self.db, "FeatureComponents",
                        [(feature.id, component)])

    eleza make_short(self, file):
        oldfile = file
        file = file.replace('+', '_')
        file = ''.join(c for c in file ikiwa not c in r' "/\[]:;=,')
        parts = file.split(".")
        ikiwa len(parts) > 1:
            prefix = "".join(parts[:-1]).upper()
            suffix = parts[-1].upper()
            ikiwa not prefix:
                prefix = suffix
                suffix = None
        else:
            prefix = file.upper()
            suffix = None
        ikiwa len(parts) < 3 and len(prefix) <= 8 and file == oldfile and (
                                                not suffix or len(suffix) <= 3):
            ikiwa suffix:
                file = prefix+"."+suffix
            else:
                file = prefix
        else:
            file = None
        ikiwa file is None or file in self.short_names:
            prefix = prefix[:6]
            ikiwa suffix:
                suffix = suffix[:3]
            pos = 1
            while 1:
                ikiwa suffix:
                    file = "%s~%d.%s" % (prefix, pos, suffix)
                else:
                    file = "%s~%d" % (prefix, pos)
                ikiwa file not in self.short_names: break
                pos += 1
                assert pos < 10000
                ikiwa pos in (10, 100, 1000):
                    prefix = prefix[:-1]
        self.short_names.add(file)
        assert not re.search(r'[\?|><:/*"+,;=\[\]]', file) # restrictions on short names
        rudisha file

    eleza add_file(self, file, src=None, version=None, language=None):
        """Add a file to the current component of the directory, starting a new one
        ikiwa there is no current component. By default, the file name in the source
        and the file table will be identical. If the src file is specified, it is
        interpreted relative to the current directory. Optionally, a version and a
        language can be specified for the entry in the File table."""
        ikiwa not self.component:
            self.start_component(self.logical, current_feature, 0)
        ikiwa not src:
            # Allow relative paths for file ikiwa src is not specified
            src = file
            file = os.path.basename(file)
        absolute = os.path.join(self.absolute, src)
        assert not re.search(r'[\?|><:/*]"', file) # restrictions on long names
        ikiwa file in self.keyfiles:
            logical = self.keyfiles[file]
        else:
            logical = None
        sequence, logical = self.cab.append(absolute, file, logical)
        assert logical not in self.ids
        self.ids.add(logical)
        short = self.make_short(file)
        full = "%s|%s" % (short, file)
        filesize = os.stat(absolute).st_size
        # constants.msidbFileAttributesVital
        # Compressed omitted, since it is the database default
        # could add r/o, system, hidden
        attributes = 512
        add_data(self.db, "File",
                        [(logical, self.component, full, filesize, version,
                         language, attributes, sequence)])
        #ikiwa not version:
        #    # Add hash ikiwa the file is not versioned
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

    eleza glob(self, pattern, exclude = None):
        """Add a list of files to the current component as specified in the
        glob pattern. Individual files can be excluded in the exclude list."""
        try:
            files = os.listdir(self.absolute)
        except OSError:
            rudisha []
        ikiwa pattern[:1] != '.':
            files = (f for f in files ikiwa f[0] != '.')
        files = fnmatch.filter(files, pattern)
        for f in files:
            ikiwa exclude and f in exclude: continue
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
                 parent=None, directory = None, attributes=0):
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

    eleza event(self, event, argument, condition = "1", ordering = None):
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

    eleza add(self, name, x, y, w, h, text, value = None):
        ikiwa value is None:
            value = name
        add_data(self.dlg.db, "RadioButton",
                 [(self.property, self.index, value,
                   x, y, w, h, text, None)])
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
        rudisha self.control(name, "Text", x, y, w, h, attr, None,
                     text, None, None)

    eleza bitmap(self, name, x, y, w, h, text):
        rudisha self.control(name, "Bitmap", x, y, w, h, 1, None, text, None, None)

    eleza line(self, name, x, y, w, h):
        rudisha self.control(name, "Line", x, y, w, h, 1, None, None, None, None)

    eleza pushbutton(self, name, x, y, w, h, attr, text, next):
        rudisha self.control(name, "PushButton", x, y, w, h, attr, None, text, next, None)

    eleza radiogroup(self, name, x, y, w, h, attr, prop, text, next):
        add_data(self.db, "Control",
                 [(self.name, name, "RadioButtonGroup",
                   x, y, w, h, attr, prop, text, next, None)])
        rudisha RadioButtonGroup(self, name, prop)

    eleza checkbox(self, name, x, y, w, h, attr, prop, text, next):
        rudisha self.control(name, "CheckBox", x, y, w, h, attr, prop, text, next, None)
