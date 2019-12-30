
kutoka collections agiza namedtuple
agiza glob
agiza os.path
agiza re
agiza shutil
agiza sys
agiza subprocess


VERBOSITY = 2

C_GLOBALS_DIR = os.path.abspath(os.path.dirname(__file__))
TOOLS_DIR = os.path.dirname(C_GLOBALS_DIR)
ROOT_DIR = os.path.dirname(TOOLS_DIR)
GLOBALS_FILE = os.path.join(C_GLOBALS_DIR, 'ignored-globals.txt')

SOURCE_DIRS = ['Include', 'Objects', 'Modules', 'Parser', 'Python']

CAPI_REGEX = re.compile(r'^ *PyAPI_DATA\([^)]*\) \W*(_?Py\w+(?:, \w+)*\w).*;.*$')


IGNORED_VARS = {
        '_DYNAMIC',
        '_GLOBAL_OFFSET_TABLE_',
        '__JCR_LIST__',
        '__JCR_END__',
        '__TMC_END__',
        '__bss_start',
        '__data_start',
        '__dso_handle',
        '_edata',
        '_end',
        }


eleza find_capi_vars(root):
    capi_vars = {}
    kila dirname kwenye SOURCE_DIRS:
        kila filename kwenye glob.glob(os.path.join(ROOT_DIR, dirname, '**/*.[hc]'),
                                  recursive=Kweli):
            ukijumuisha open(filename) kama file:
                kila name kwenye _find_capi_vars(file):
                    ikiwa name kwenye capi_vars:
                        assert sio filename.endswith('.c')
                        assert capi_vars[name].endswith('.c')
                    capi_vars[name] = filename
    rudisha capi_vars


eleza _find_capi_vars(lines):
    kila line kwenye lines:
        ikiwa sio line.startswith('PyAPI_DATA'):
            endelea
        assert '{' haiko kwenye line
        match = CAPI_REGEX.match(line)
        assert match
        names, = match.groups()
        kila name kwenye names.split(', '):
            tuma name


eleza _read_global_names(filename):
    # These variables are shared between all interpreters kwenye the process.
    ukijumuisha open(filename) kama file:
        rudisha {line.partition('#')[0].strip()
                kila line kwenye file
                ikiwa line.strip() na sio line.startswith('#')}


eleza _is_global_var(name, globalnames):
    ikiwa _is_autogen_var(name):
        rudisha Kweli
    ikiwa _is_type_var(name):
        rudisha Kweli
    ikiwa _is_module(name):
        rudisha Kweli
    ikiwa _is_exception(name):
        rudisha Kweli
    ikiwa _is_compiler(name):
        rudisha Kweli
    rudisha name kwenye globalnames


eleza _is_autogen_var(name):
    rudisha (
        name.startswith('PyId_') ama
        '.' kwenye name ama
        # Objects/typeobject.c
        name.startswith('op_id.') ama
        name.startswith('rop_id.') ama
        # Python/graminit.c
        name.startswith('arcs_') ama
        name.startswith('states_')
        )


eleza _is_type_var(name):
    ikiwa name.endswith(('Type', '_Type', '_type')):  # XXX Always a static type?
        rudisha Kweli
    ikiwa name.endswith('_desc'):  # kila structseq types
        rudisha Kweli
    rudisha (
        name.startswith('doc_') ama
        name.endswith(('_doc', '__doc__', '_docstring')) ama
        name.endswith('_methods') ama
        name.endswith('_fields') ama
        name.endswith(('_memberlist', '_members')) ama
        name.endswith('_slots') ama
        name.endswith(('_getset', '_getsets', '_getsetlist')) ama
        name.endswith('_as_mapping') ama
        name.endswith('_as_number') ama
        name.endswith('_as_sequence') ama
        name.endswith('_as_buffer') ama
        name.endswith('_as_async')
        )


eleza _is_module(name):
    ikiwa name.endswith(('_functions', 'Methods', '_Methods')):
        rudisha Kweli
    ikiwa name == 'module_def':
        rudisha Kweli
    ikiwa name == 'initialized':
        rudisha Kweli
    rudisha name.endswith(('module', '_Module'))


eleza _is_exception(name):
    # Other vars are enumerated kwenye globals-core.txt.
    ikiwa sio name.startswith(('PyExc_', '_PyExc_')):
        rudisha Uongo
    rudisha name.endswith(('Error', 'Warning'))


eleza _is_compiler(name):
    rudisha (
        # Python/Python-ast.c
        name.endswith('_type') ama
        name.endswith('_singleton') ama
        name.endswith('_attributes')
        )


kundi Var(namedtuple('Var', 'name kind scope capi filename')):

    @classmethod
    eleza parse_nm(cls, line, expected, ignored, capi_vars, globalnames):
        _, _, line = line.partition(' ')  # strip off the address
        line = line.strip()
        kind, _, line = line.partition(' ')
        ikiwa kind kwenye ignored ama ():
            rudisha Tupu
        lasivyo kind haiko kwenye expected ama ():
            ashiria RuntimeError('unsupported NM type {!r}'.format(kind))

        name, _, filename = line.partition('\t')
        name = name.strip()
        ikiwa _is_autogen_var(name):
            rudisha Tupu
        ikiwa _is_global_var(name, globalnames):
            scope = 'global'
        isipokua:
            scope = Tupu
        capi = (name kwenye capi_vars ama ())
        ikiwa filename:
            filename = os.path.relpath(filename.partition(':')[0])
        rudisha cls(name, kind, scope, capi, filename ama '~???~')

    @property
    eleza external(self):
        rudisha self.kind.isupper()


eleza find_vars(root, globals_filename=GLOBALS_FILE):
    python = os.path.join(root, 'python')
    ikiwa sio os.path.exists(python):
        ashiria RuntimeError('python binary missing (need to build it first?)')
    capi_vars = find_capi_vars(root)
    globalnames = _read_global_names(globals_filename)

    nm = shutil.which('nm')
    ikiwa nm ni Tupu:
        # XXX Use dumpbin.exe /SYMBOLS on Windows.
        ashiria NotImplementedError
    isipokua:
        tuma kutoka (var
                    kila var kwenye _find_var_symbols(python, nm, capi_vars,
                                                 globalnames)
                    ikiwa var.name haiko kwenye IGNORED_VARS)


NM_FUNCS = set('Tt')
NM_PUBLIC_VARS = set('BD')
NM_PRIVATE_VARS = set('bd')
NM_VARS = NM_PUBLIC_VARS | NM_PRIVATE_VARS
NM_DATA = set('Rr')
NM_OTHER = set('ACGgiINpSsuUVvWw-?')
NM_IGNORED = NM_FUNCS | NM_DATA | NM_OTHER


eleza _find_var_symbols(python, nm, capi_vars, globalnames):
    args = [nm,
            '--line-numbers',
            python]
    out = subprocess.check_output(args)
    kila line kwenye out.decode('utf-8').splitlines():
        var = Var.parse_nm(line, NM_VARS, NM_IGNORED, capi_vars, globalnames)
        ikiwa var ni Tupu:
            endelea
        tuma var


#######################################

kundi Filter(namedtuple('Filter', 'name op value action')):

    @classmethod
    eleza parse(cls, raw):
        action = '+'
        ikiwa raw.startswith(('+', '-')):
            action = raw[0]
            raw = raw[1:]
        # XXX Support < na >?
        name, op, value = raw.partition('=')
        rudisha cls(name, op, value, action)

    eleza check(self, var):
        value = getattr(var, self.name, Tupu)
        ikiwa sio self.op:
            matched = bool(value)
        lasivyo self.op == '=':
            matched = (value == self.value)
        isipokua:
            ashiria NotImplementedError

        ikiwa self.action == '+':
            rudisha matched
        lasivyo self.action == '-':
            rudisha sio matched
        isipokua:
            ashiria NotImplementedError


eleza filter_var(var, filters):
    kila filter kwenye filters:
        ikiwa sio filter.check(var):
            rudisha Uongo
    rudisha Kweli


eleza make_sort_key(spec):
    columns = [(col.strip('_'), '_' ikiwa col.startswith('_') isipokua '')
               kila col kwenye spec]
    eleza sort_key(var):
        rudisha tuple(getattr(var, col).lstrip(prefix)
                     kila col, prefix kwenye columns)
    rudisha sort_key


eleza make_groups(allvars, spec):
    group = spec
    groups = {}
    kila var kwenye allvars:
        value = getattr(var, group)
        key = '{}: {}'.format(group, value)
        jaribu:
            groupvars = groups[key]
        tatizo KeyError:
            groupvars = groups[key] = []
        groupvars.append(var)
    rudisha groups


eleza format_groups(groups, columns, fmts, widths):
    kila group kwenye sorted(groups):
        groupvars = groups[group]
        tuma '', 0
        tuma '  # {}'.format(group), 0
        tuma kutoka format_vars(groupvars, columns, fmts, widths)


eleza format_vars(allvars, columns, fmts, widths):
    fmt = ' '.join(fmts[col] kila col kwenye columns)
    fmt = ' ' + fmt.replace(' ', '   ') + ' '  # kila div margin
    header = fmt.replace(':', ':^').format(*(col.upper() kila col kwenye columns))
    tuma header, 0
    div = ' '.join('-'*(widths[col]+2) kila col kwenye columns)
    tuma div, 0
    kila var kwenye allvars:
        values = (getattr(var, col) kila col kwenye columns)
        row = fmt.format(*('X' ikiwa val ni Kweli isipokua val ama ''
                           kila val kwenye values))
        tuma row, 1
    tuma div, 0


#######################################

COLUMNS = 'name,external,capi,scope,filename'
COLUMN_NAMES = COLUMNS.split(',')

COLUMN_WIDTHS = {col: len(col)
                 kila col kwenye COLUMN_NAMES}
COLUMN_WIDTHS.update({
        'name': 50,
        'scope': 7,
        'filename': 40,
        })
COLUMN_FORMATS = {col: '{:%s}' % width
                  kila col, width kwenye COLUMN_WIDTHS.items()}
kila col kwenye COLUMN_FORMATS:
    ikiwa COLUMN_WIDTHS[col] == len(col):
        COLUMN_FORMATS[col] = COLUMN_FORMATS[col].replace(':', ':^')


eleza _parse_filters_arg(raw, error):
    filters = []
    kila value kwenye raw.split(','):
        value=value.strip()
        ikiwa sio value:
            endelea
        jaribu:
            filter = Filter.parse(value)
            ikiwa filter.name haiko kwenye COLUMN_NAMES:
                ashiria Exception('unsupported column {!r}'.format(filter.name))
        tatizo Exception kama e:
            error('bad filter {!r}: {}'.format(raw, e))
        filters.append(filter)
    rudisha filters


eleza _parse_columns_arg(raw, error):
    columns = raw.split(',')
    kila column kwenye columns:
        ikiwa column haiko kwenye COLUMN_NAMES:
            error('unsupported column {!r}'.format(column))
    rudisha columns


eleza _parse_sort_arg(raw, error):
    sort = raw.split(',')
    kila column kwenye sort:
        ikiwa column.lstrip('_') haiko kwenye COLUMN_NAMES:
            error('unsupported column {!r}'.format(column))
    rudisha sort


eleza _parse_group_arg(raw, error):
    ikiwa sio raw:
        rudisha raw
    group = raw
    ikiwa group haiko kwenye COLUMN_NAMES:
        error('unsupported column {!r}'.format(group))
    ikiwa group != 'filename':
        error('unsupported group {!r}'.format(group))
    rudisha group


eleza parse_args(argv=Tupu):
    ikiwa argv ni Tupu:
        argv = sys.argv[1:]

    agiza argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('-q', '--quiet', action='count', default=0)

    parser.add_argument('--filters', default='-scope',
                        help='[[-]<COLUMN>[=<GLOB>]] ...')

    parser.add_argument('--columns', default=COLUMNS,
                        help='a comma-separated list of columns to show')
    parser.add_argument('--sort', default='filename,_name',
                        help='a comma-separated list of columns to sort')
    parser.add_argument('--group',
                        help='group by the given column name (- to sio group)')

    parser.add_argument('--rc-on-match', dest='rc', type=int)

    parser.add_argument('filename', nargs='?', default=GLOBALS_FILE)

    args = parser.parse_args(argv)

    verbose = vars(args).pop('verbose', 0)
    quiet = vars(args).pop('quiet', 0)
    args.verbosity = max(0, VERBOSITY + verbose - quiet)

    ikiwa args.sort.startswith('filename') na sio args.group:
        args.group = 'filename'

    ikiwa args.rc ni Tupu:
        ikiwa '-scope=core' kwenye args.filters ama 'core' haiko kwenye args.filters:
            args.rc = 0
        isipokua:
            args.rc = 1

    args.filters = _parse_filters_arg(args.filters, parser.error)
    args.columns = _parse_columns_arg(args.columns, parser.error)
    args.sort = _parse_sort_arg(args.sort, parser.error)
    args.group = _parse_group_arg(args.group, parser.error)

    rudisha args


eleza main(root=ROOT_DIR, filename=GLOBALS_FILE,
         filters=Tupu, columns=COLUMN_NAMES, sort=Tupu, group=Tupu,
         verbosity=VERBOSITY, rc=1):

    log = lambda msg: ...
    ikiwa verbosity >= 2:
        log = lambda msg: andika(msg)

    allvars = (var
               kila var kwenye find_vars(root, filename)
               ikiwa filter_var(var, filters))
    ikiwa sort:
        allvars = sorted(allvars, key=make_sort_key(sort))

    ikiwa group:
        jaribu:
            columns.remove(group)
        tatizo ValueError:
            pita
        grouped = make_groups(allvars, group)
        lines = format_groups(grouped, columns, COLUMN_FORMATS, COLUMN_WIDTHS)
    isipokua:
        lines = format_vars(allvars, columns, COLUMN_FORMATS, COLUMN_WIDTHS)

    total = 0
    kila line, count kwenye lines:
        total += count
        log(line)
    log('\ntotal: {}'.format(total))

    ikiwa total na rc:
        andika('ERROR: found unsafe globals', file=sys.stderr)
        rudisha rc
    rudisha 0


ikiwa __name__ == '__main__':
    args = parse_args()
    sys.exit(
            main(**vars(args)))
