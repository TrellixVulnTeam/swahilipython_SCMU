agiza enum
agiza inspect
agiza pydoc
agiza sys
agiza unittest
agiza threading
kutoka collections agiza OrderedDict
kutoka enum agiza Enum, IntEnum, EnumMeta, Flag, IntFlag, unique, auto
kutoka io agiza StringIO
kutoka pickle agiza dumps, loads, PicklingError, HIGHEST_PROTOCOL
kutoka test agiza support
kutoka datetime agiza timedelta


# kila pickle tests
jaribu:
    kundi Stooges(Enum):
        LARRY = 1
        CURLY = 2
        MOE = 3
tatizo Exception kama exc:
    Stooges = exc

jaribu:
    kundi IntStooges(int, Enum):
        LARRY = 1
        CURLY = 2
        MOE = 3
tatizo Exception kama exc:
    IntStooges = exc

jaribu:
    kundi FloatStooges(float, Enum):
        LARRY = 1.39
        CURLY = 2.72
        MOE = 3.142596
tatizo Exception kama exc:
    FloatStooges = exc

jaribu:
    kundi FlagStooges(Flag):
        LARRY = 1
        CURLY = 2
        MOE = 3
tatizo Exception kama exc:
    FlagStooges = exc

# kila pickle test na subkundi tests
jaribu:
    kundi StrEnum(str, Enum):
        'accepts only string values'
    kundi Name(StrEnum):
        BDFL = 'Guido van Rossum'
        FLUFL = 'Barry Warsaw'
tatizo Exception kama exc:
    Name = exc

jaribu:
    Question = Enum('Question', 'who what when where why', module=__name__)
tatizo Exception kama exc:
    Question = exc

jaribu:
    Answer = Enum('Answer', 'him this then there because')
tatizo Exception kama exc:
    Answer = exc

jaribu:
    Theory = Enum('Theory', 'rule law supposition', qualname='spanish_inquisition')
tatizo Exception kama exc:
    Theory = exc

# kila doctests
jaribu:
    kundi Fruit(Enum):
        TOMATO = 1
        BANANA = 2
        CHERRY = 3
tatizo Exception:
    pita

eleza test_pickle_dump_load(assertion, source, target=Tupu):
    ikiwa target ni Tupu:
        target = source
    kila protocol kwenye range(HIGHEST_PROTOCOL + 1):
        assertion(loads(dumps(source, protocol=protocol)), target)

eleza test_pickle_exception(assertion, exception, obj):
    kila protocol kwenye range(HIGHEST_PROTOCOL + 1):
        ukijumuisha assertion(exception):
            dumps(obj, protocol=protocol)

kundi TestHelpers(unittest.TestCase):
    # _is_descriptor, _is_sunder, _is_dunder

    eleza test_is_descriptor(self):
        kundi foo:
            pita
        kila attr kwenye ('__get__','__set__','__delete__'):
            obj = foo()
            self.assertUongo(enum._is_descriptor(obj))
            setattr(obj, attr, 1)
            self.assertKweli(enum._is_descriptor(obj))

    eleza test_is_sunder(self):
        kila s kwenye ('_a_', '_aa_'):
            self.assertKweli(enum._is_sunder(s))

        kila s kwenye ('a', 'a_', '_a', '__a', 'a__', '__a__', '_a__', '__a_', '_',
                '__', '___', '____', '_____',):
            self.assertUongo(enum._is_sunder(s))

    eleza test_is_dunder(self):
        kila s kwenye ('__a__', '__aa__'):
            self.assertKweli(enum._is_dunder(s))
        kila s kwenye ('a', 'a_', '_a', '__a', 'a__', '_a_', '_a__', '__a_', '_',
                '__', '___', '____', '_____',):
            self.assertUongo(enum._is_dunder(s))

# kila subclassing tests

kundi classproperty:

    eleza __init__(self, fget=Tupu, fset=Tupu, fdel=Tupu, doc=Tupu):
        self.fget = fget
        self.fset = fset
        self.ftoa = fdel
        ikiwa doc ni Tupu na fget ni sio Tupu:
            doc = fget.__doc__
        self.__doc__ = doc

    eleza __get__(self, instance, ownerclass):
        rudisha self.fget(ownerclass)


# tests

kundi TestEnum(unittest.TestCase):

    eleza setUp(self):
        kundi Season(Enum):
            SPRING = 1
            SUMMER = 2
            AUTUMN = 3
            WINTER = 4
        self.Season = Season

        kundi Konstants(float, Enum):
            E = 2.7182818
            PI = 3.1415926
            TAU = 2 * PI
        self.Konstants = Konstants

        kundi Grades(IntEnum):
            A = 5
            B = 4
            C = 3
            D = 2
            F = 0
        self.Grades = Grades

        kundi Directional(str, Enum):
            EAST = 'east'
            WEST = 'west'
            NORTH = 'north'
            SOUTH = 'south'
        self.Directional = Directional

        kutoka datetime agiza date
        kundi Holiday(date, Enum):
            NEW_YEAR = 2013, 1, 1
            IDES_OF_MARCH = 2013, 3, 15
        self.Holiday = Holiday

    eleza test_dir_on_class(self):
        Season = self.Season
        self.assertEqual(
            set(dir(Season)),
            set(['__class__', '__doc__', '__members__', '__module__',
                'SPRING', 'SUMMER', 'AUTUMN', 'WINTER']),
            )

    eleza test_dir_on_item(self):
        Season = self.Season
        self.assertEqual(
            set(dir(Season.WINTER)),
            set(['__class__', '__doc__', '__module__', 'name', 'value']),
            )

    eleza test_dir_with_added_behavior(self):
        kundi Test(Enum):
            this = 'that'
            these = 'those'
            eleza wowser(self):
                rudisha ("Wowser! I'm %s!" % self.name)
        self.assertEqual(
                set(dir(Test)),
                set(['__class__', '__doc__', '__members__', '__module__', 'this', 'these']),
                )
        self.assertEqual(
                set(dir(Test.this)),
                set(['__class__', '__doc__', '__module__', 'name', 'value', 'wowser']),
                )

    eleza test_dir_on_sub_with_behavior_on_super(self):
        # see issue22506
        kundi SuperEnum(Enum):
            eleza invisible(self):
                rudisha "did you see me?"
        kundi SubEnum(SuperEnum):
            sample = 5
        self.assertEqual(
                set(dir(SubEnum.sample)),
                set(['__class__', '__doc__', '__module__', 'name', 'value', 'invisible']),
                )

    eleza test_enum_in_enum_out(self):
        Season = self.Season
        self.assertIs(Season(Season.WINTER), Season.WINTER)

    eleza test_enum_value(self):
        Season = self.Season
        self.assertEqual(Season.SPRING.value, 1)

    eleza test_intenum_value(self):
        self.assertEqual(IntStooges.CURLY.value, 2)

    eleza test_enum(self):
        Season = self.Season
        lst = list(Season)
        self.assertEqual(len(lst), len(Season))
        self.assertEqual(len(Season), 4, Season)
        self.assertEqual(
            [Season.SPRING, Season.SUMMER, Season.AUTUMN, Season.WINTER], lst)

        kila i, season kwenye enumerate('SPRING SUMMER AUTUMN WINTER'.split(), 1):
            e = Season(i)
            self.assertEqual(e, getattr(Season, season))
            self.assertEqual(e.value, i)
            self.assertNotEqual(e, i)
            self.assertEqual(e.name, season)
            self.assertIn(e, Season)
            self.assertIs(type(e), Season)
            self.assertIsInstance(e, Season)
            self.assertEqual(str(e), 'Season.' + season)
            self.assertEqual(
                    repr(e),
                    '<Season.{0}: {1}>'.format(season, i),
                    )

    eleza test_value_name(self):
        Season = self.Season
        self.assertEqual(Season.SPRING.name, 'SPRING')
        self.assertEqual(Season.SPRING.value, 1)
        ukijumuisha self.assertRaises(AttributeError):
            Season.SPRING.name = 'invierno'
        ukijumuisha self.assertRaises(AttributeError):
            Season.SPRING.value = 2

    eleza test_changing_member(self):
        Season = self.Season
        ukijumuisha self.assertRaises(AttributeError):
            Season.WINTER = 'really cold'

    eleza test_attribute_deletion(self):
        kundi Season(Enum):
            SPRING = 1
            SUMMER = 2
            AUTUMN = 3
            WINTER = 4

            eleza spam(cls):
                pita

        self.assertKweli(hasattr(Season, 'spam'))
        toa Season.spam
        self.assertUongo(hasattr(Season, 'spam'))

        ukijumuisha self.assertRaises(AttributeError):
            toa Season.SPRING
        ukijumuisha self.assertRaises(AttributeError):
            toa Season.DRY
        ukijumuisha self.assertRaises(AttributeError):
            toa Season.SPRING.name

    eleza test_bool_of_class(self):
        kundi Empty(Enum):
            pita
        self.assertKweli(bool(Empty))

    eleza test_bool_of_member(self):
        kundi Count(Enum):
            zero = 0
            one = 1
            two = 2
        kila member kwenye Count:
            self.assertKweli(bool(member))

    eleza test_invalid_names(self):
        ukijumuisha self.assertRaises(ValueError):
            kundi Wrong(Enum):
                mro = 9
        ukijumuisha self.assertRaises(ValueError):
            kundi Wrong(Enum):
                _create_= 11
        ukijumuisha self.assertRaises(ValueError):
            kundi Wrong(Enum):
                _get_mixins_ = 9
        ukijumuisha self.assertRaises(ValueError):
            kundi Wrong(Enum):
                _find_new_ = 1
        ukijumuisha self.assertRaises(ValueError):
            kundi Wrong(Enum):
                _any_name_ = 9

    eleza test_bool(self):
        # plain Enum members are always Kweli
        kundi Logic(Enum):
            true = Kweli
            false = Uongo
        self.assertKweli(Logic.true)
        self.assertKweli(Logic.false)
        # unless overridden
        kundi RealLogic(Enum):
            true = Kweli
            false = Uongo
            eleza __bool__(self):
                rudisha bool(self._value_)
        self.assertKweli(RealLogic.true)
        self.assertUongo(RealLogic.false)
        # mixed Enums depend on mixed-in type
        kundi IntLogic(int, Enum):
            true = 1
            false = 0
        self.assertKweli(IntLogic.true)
        self.assertUongo(IntLogic.false)

    eleza test_contains(self):
        Season = self.Season
        self.assertIn(Season.AUTUMN, Season)
        ukijumuisha self.assertRaises(TypeError):
            3 kwenye Season
        ukijumuisha self.assertRaises(TypeError):
            'AUTUMN' kwenye Season

        val = Season(3)
        self.assertIn(val, Season)

        kundi OtherEnum(Enum):
            one = 1; two = 2
        self.assertNotIn(OtherEnum.two, Season)

    eleza test_comparisons(self):
        Season = self.Season
        ukijumuisha self.assertRaises(TypeError):
            Season.SPRING < Season.WINTER
        ukijumuisha self.assertRaises(TypeError):
            Season.SPRING > 4

        self.assertNotEqual(Season.SPRING, 1)

        kundi Part(Enum):
            SPRING = 1
            CLIP = 2
            BARREL = 3

        self.assertNotEqual(Season.SPRING, Part.SPRING)
        ukijumuisha self.assertRaises(TypeError):
            Season.SPRING < Part.CLIP

    eleza test_enum_duplicates(self):
        kundi Season(Enum):
            SPRING = 1
            SUMMER = 2
            AUTUMN = FALL = 3
            WINTER = 4
            ANOTHER_SPRING = 1
        lst = list(Season)
        self.assertEqual(
            lst,
            [Season.SPRING, Season.SUMMER,
             Season.AUTUMN, Season.WINTER,
            ])
        self.assertIs(Season.FALL, Season.AUTUMN)
        self.assertEqual(Season.FALL.value, 3)
        self.assertEqual(Season.AUTUMN.value, 3)
        self.assertIs(Season(3), Season.AUTUMN)
        self.assertIs(Season(1), Season.SPRING)
        self.assertEqual(Season.FALL.name, 'AUTUMN')
        self.assertEqual(
                [k kila k,v kwenye Season.__members__.items() ikiwa v.name != k],
                ['FALL', 'ANOTHER_SPRING'],
                )

    eleza test_duplicate_name(self):
        ukijumuisha self.assertRaises(TypeError):
            kundi Color(Enum):
                red = 1
                green = 2
                blue = 3
                red = 4

        ukijumuisha self.assertRaises(TypeError):
            kundi Color(Enum):
                red = 1
                green = 2
                blue = 3
                eleza red(self):
                    rudisha 'red'

        ukijumuisha self.assertRaises(TypeError):
            kundi Color(Enum):
                @property
                eleza red(self):
                    rudisha 'redder'
                red = 1
                green = 2
                blue = 3


    eleza test_enum_with_value_name(self):
        kundi Huh(Enum):
            name = 1
            value = 2
        self.assertEqual(
            list(Huh),
            [Huh.name, Huh.value],
            )
        self.assertIs(type(Huh.name), Huh)
        self.assertEqual(Huh.name.name, 'name')
        self.assertEqual(Huh.name.value, 1)

    eleza test_format_enum(self):
        Season = self.Season
        self.assertEqual('{}'.format(Season.SPRING),
                         '{}'.format(str(Season.SPRING)))
        self.assertEqual( '{:}'.format(Season.SPRING),
                          '{:}'.format(str(Season.SPRING)))
        self.assertEqual('{:20}'.format(Season.SPRING),
                         '{:20}'.format(str(Season.SPRING)))
        self.assertEqual('{:^20}'.format(Season.SPRING),
                         '{:^20}'.format(str(Season.SPRING)))
        self.assertEqual('{:>20}'.format(Season.SPRING),
                         '{:>20}'.format(str(Season.SPRING)))
        self.assertEqual('{:<20}'.format(Season.SPRING),
                         '{:<20}'.format(str(Season.SPRING)))

    eleza test_format_enum_custom(self):
        kundi TestFloat(float, Enum):
            one = 1.0
            two = 2.0
            eleza __format__(self, spec):
                rudisha 'TestFloat success!'
        self.assertEqual('{}'.format(TestFloat.one), 'TestFloat success!')

    eleza assertFormatIsValue(self, spec, member):
        self.assertEqual(spec.format(member), spec.format(member.value))

    eleza test_format_enum_date(self):
        Holiday = self.Holiday
        self.assertFormatIsValue('{}', Holiday.IDES_OF_MARCH)
        self.assertFormatIsValue('{:}', Holiday.IDES_OF_MARCH)
        self.assertFormatIsValue('{:20}', Holiday.IDES_OF_MARCH)
        self.assertFormatIsValue('{:^20}', Holiday.IDES_OF_MARCH)
        self.assertFormatIsValue('{:>20}', Holiday.IDES_OF_MARCH)
        self.assertFormatIsValue('{:<20}', Holiday.IDES_OF_MARCH)
        self.assertFormatIsValue('{:%Y %m}', Holiday.IDES_OF_MARCH)
        self.assertFormatIsValue('{:%Y %m %M:00}', Holiday.IDES_OF_MARCH)

    eleza test_format_enum_float(self):
        Konstants = self.Konstants
        self.assertFormatIsValue('{}', Konstants.TAU)
        self.assertFormatIsValue('{:}', Konstants.TAU)
        self.assertFormatIsValue('{:20}', Konstants.TAU)
        self.assertFormatIsValue('{:^20}', Konstants.TAU)
        self.assertFormatIsValue('{:>20}', Konstants.TAU)
        self.assertFormatIsValue('{:<20}', Konstants.TAU)
        self.assertFormatIsValue('{:n}', Konstants.TAU)
        self.assertFormatIsValue('{:5.2}', Konstants.TAU)
        self.assertFormatIsValue('{:f}', Konstants.TAU)

    eleza test_format_enum_int(self):
        Grades = self.Grades
        self.assertFormatIsValue('{}', Grades.C)
        self.assertFormatIsValue('{:}', Grades.C)
        self.assertFormatIsValue('{:20}', Grades.C)
        self.assertFormatIsValue('{:^20}', Grades.C)
        self.assertFormatIsValue('{:>20}', Grades.C)
        self.assertFormatIsValue('{:<20}', Grades.C)
        self.assertFormatIsValue('{:+}', Grades.C)
        self.assertFormatIsValue('{:08X}', Grades.C)
        self.assertFormatIsValue('{:b}', Grades.C)

    eleza test_format_enum_str(self):
        Directional = self.Directional
        self.assertFormatIsValue('{}', Directional.WEST)
        self.assertFormatIsValue('{:}', Directional.WEST)
        self.assertFormatIsValue('{:20}', Directional.WEST)
        self.assertFormatIsValue('{:^20}', Directional.WEST)
        self.assertFormatIsValue('{:>20}', Directional.WEST)
        self.assertFormatIsValue('{:<20}', Directional.WEST)

    eleza test_hash(self):
        Season = self.Season
        dates = {}
        dates[Season.WINTER] = '1225'
        dates[Season.SPRING] = '0315'
        dates[Season.SUMMER] = '0704'
        dates[Season.AUTUMN] = '1031'
        self.assertEqual(dates[Season.AUTUMN], '1031')

    eleza test_intenum_from_scratch(self):
        kundi phy(int, Enum):
            pi = 3
            tau = 2 * pi
        self.assertKweli(phy.pi < phy.tau)

    eleza test_intenum_inherited(self):
        kundi IntEnum(int, Enum):
            pita
        kundi phy(IntEnum):
            pi = 3
            tau = 2 * pi
        self.assertKweli(phy.pi < phy.tau)

    eleza test_floatenum_from_scratch(self):
        kundi phy(float, Enum):
            pi = 3.1415926
            tau = 2 * pi
        self.assertKweli(phy.pi < phy.tau)

    eleza test_floatenum_inherited(self):
        kundi FloatEnum(float, Enum):
            pita
        kundi phy(FloatEnum):
            pi = 3.1415926
            tau = 2 * pi
        self.assertKweli(phy.pi < phy.tau)

    eleza test_strenum_from_scratch(self):
        kundi phy(str, Enum):
            pi = 'Pi'
            tau = 'Tau'
        self.assertKweli(phy.pi < phy.tau)

    eleza test_strenum_inherited(self):
        kundi StrEnum(str, Enum):
            pita
        kundi phy(StrEnum):
            pi = 'Pi'
            tau = 'Tau'
        self.assertKweli(phy.pi < phy.tau)


    eleza test_intenum(self):
        kundi WeekDay(IntEnum):
            SUNDAY = 1
            MONDAY = 2
            TUESDAY = 3
            WEDNESDAY = 4
            THURSDAY = 5
            FRIDAY = 6
            SATURDAY = 7

        self.assertEqual(['a', 'b', 'c'][WeekDay.MONDAY], 'c')
        self.assertEqual([i kila i kwenye range(WeekDay.TUESDAY)], [0, 1, 2])

        lst = list(WeekDay)
        self.assertEqual(len(lst), len(WeekDay))
        self.assertEqual(len(WeekDay), 7)
        target = 'SUNDAY MONDAY TUESDAY WEDNESDAY THURSDAY FRIDAY SATURDAY'
        target = target.split()
        kila i, weekday kwenye enumerate(target, 1):
            e = WeekDay(i)
            self.assertEqual(e, i)
            self.assertEqual(int(e), i)
            self.assertEqual(e.name, weekday)
            self.assertIn(e, WeekDay)
            self.assertEqual(lst.index(e)+1, i)
            self.assertKweli(0 < e < 8)
            self.assertIs(type(e), WeekDay)
            self.assertIsInstance(e, int)
            self.assertIsInstance(e, Enum)

    eleza test_intenum_duplicates(self):
        kundi WeekDay(IntEnum):
            SUNDAY = 1
            MONDAY = 2
            TUESDAY = TEUSDAY = 3
            WEDNESDAY = 4
            THURSDAY = 5
            FRIDAY = 6
            SATURDAY = 7
        self.assertIs(WeekDay.TEUSDAY, WeekDay.TUESDAY)
        self.assertEqual(WeekDay(3).name, 'TUESDAY')
        self.assertEqual([k kila k,v kwenye WeekDay.__members__.items()
                ikiwa v.name != k], ['TEUSDAY', ])

    eleza test_intenum_from_bytes(self):
        self.assertIs(IntStooges.from_bytes(b'\x00\x03', 'big'), IntStooges.MOE)
        ukijumuisha self.assertRaises(ValueError):
            IntStooges.from_bytes(b'\x00\x05', 'big')

    eleza test_floatenum_fromhex(self):
        h = float.hex(FloatStooges.MOE.value)
        self.assertIs(FloatStooges.fromhex(h), FloatStooges.MOE)
        h = float.hex(FloatStooges.MOE.value + 0.01)
        ukijumuisha self.assertRaises(ValueError):
            FloatStooges.fromhex(h)

    eleza test_pickle_enum(self):
        ikiwa isinstance(Stooges, Exception):
            ashiria Stooges
        test_pickle_dump_load(self.assertIs, Stooges.CURLY)
        test_pickle_dump_load(self.assertIs, Stooges)

    eleza test_pickle_int(self):
        ikiwa isinstance(IntStooges, Exception):
            ashiria IntStooges
        test_pickle_dump_load(self.assertIs, IntStooges.CURLY)
        test_pickle_dump_load(self.assertIs, IntStooges)

    eleza test_pickle_float(self):
        ikiwa isinstance(FloatStooges, Exception):
            ashiria FloatStooges
        test_pickle_dump_load(self.assertIs, FloatStooges.CURLY)
        test_pickle_dump_load(self.assertIs, FloatStooges)

    eleza test_pickle_enum_function(self):
        ikiwa isinstance(Answer, Exception):
            ashiria Answer
        test_pickle_dump_load(self.assertIs, Answer.him)
        test_pickle_dump_load(self.assertIs, Answer)

    eleza test_pickle_enum_function_with_module(self):
        ikiwa isinstance(Question, Exception):
            ashiria Question
        test_pickle_dump_load(self.assertIs, Question.who)
        test_pickle_dump_load(self.assertIs, Question)

    eleza test_enum_function_with_qualname(self):
        ikiwa isinstance(Theory, Exception):
            ashiria Theory
        self.assertEqual(Theory.__qualname__, 'spanish_inquisition')

    eleza test_class_nested_enum_and_pickle_protocol_four(self):
        # would normally just have this directly kwenye the kundi namespace
        kundi NestedEnum(Enum):
            twigs = 'common'
            shiny = 'rare'

        self.__class__.NestedEnum = NestedEnum
        self.NestedEnum.__qualname__ = '%s.NestedEnum' % self.__class__.__name__
        test_pickle_dump_load(self.assertIs, self.NestedEnum.twigs)

    eleza test_pickle_by_name(self):
        kundi ReplaceGlobalInt(IntEnum):
            ONE = 1
            TWO = 2
        ReplaceGlobalInt.__reduce_ex__ = enum._reduce_ex_by_name
        kila proto kwenye range(HIGHEST_PROTOCOL):
            self.assertEqual(ReplaceGlobalInt.TWO.__reduce_ex__(proto), 'TWO')

    eleza test_exploding_pickle(self):
        BadPickle = Enum(
                'BadPickle', 'dill sweet bread-n-butter', module=__name__)
        globals()['BadPickle'] = BadPickle
        # now koma BadPickle to test exception raising
        enum._make_class_unpicklable(BadPickle)
        test_pickle_exception(self.assertRaises, TypeError, BadPickle.dill)
        test_pickle_exception(self.assertRaises, PicklingError, BadPickle)

    eleza test_string_enum(self):
        kundi SkillLevel(str, Enum):
            master = 'what ni the sound of one hand clapping?'
            journeyman = 'why did the chicken cross the road?'
            apprentice = 'knock, knock!'
        self.assertEqual(SkillLevel.apprentice, 'knock, knock!')

    eleza test_getattr_getitem(self):
        kundi Period(Enum):
            morning = 1
            noon = 2
            evening = 3
            night = 4
        self.assertIs(Period(2), Period.noon)
        self.assertIs(getattr(Period, 'night'), Period.night)
        self.assertIs(Period['morning'], Period.morning)

    eleza test_getattr_dunder(self):
        Season = self.Season
        self.assertKweli(getattr(Season, '__eq__'))

    eleza test_iteration_order(self):
        kundi Season(Enum):
            SUMMER = 2
            WINTER = 4
            AUTUMN = 3
            SPRING = 1
        self.assertEqual(
                list(Season),
                [Season.SUMMER, Season.WINTER, Season.AUTUMN, Season.SPRING],
                )

    eleza test_reversed_iteration_order(self):
        self.assertEqual(
                list(reversed(self.Season)),
                [self.Season.WINTER, self.Season.AUTUMN, self.Season.SUMMER,
                 self.Season.SPRING]
                )

    eleza test_programmatic_function_string(self):
        SummerMonth = Enum('SummerMonth', 'june july august')
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
                )
        kila i, month kwenye enumerate('june july august'.split(), 1):
            e = SummerMonth(i)
            self.assertEqual(int(e.value), i)
            self.assertNotEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    eleza test_programmatic_function_string_with_start(self):
        SummerMonth = Enum('SummerMonth', 'june july august', start=10)
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
                )
        kila i, month kwenye enumerate('june july august'.split(), 10):
            e = SummerMonth(i)
            self.assertEqual(int(e.value), i)
            self.assertNotEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    eleza test_programmatic_function_string_list(self):
        SummerMonth = Enum('SummerMonth', ['june', 'july', 'august'])
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
                )
        kila i, month kwenye enumerate('june july august'.split(), 1):
            e = SummerMonth(i)
            self.assertEqual(int(e.value), i)
            self.assertNotEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    eleza test_programmatic_function_string_list_with_start(self):
        SummerMonth = Enum('SummerMonth', ['june', 'july', 'august'], start=20)
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
                )
        kila i, month kwenye enumerate('june july august'.split(), 20):
            e = SummerMonth(i)
            self.assertEqual(int(e.value), i)
            self.assertNotEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    eleza test_programmatic_function_iterable(self):
        SummerMonth = Enum(
                'SummerMonth',
                (('june', 1), ('july', 2), ('august', 3))
                )
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
                )
        kila i, month kwenye enumerate('june july august'.split(), 1):
            e = SummerMonth(i)
            self.assertEqual(int(e.value), i)
            self.assertNotEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    eleza test_programmatic_function_from_dict(self):
        SummerMonth = Enum(
                'SummerMonth',
                OrderedDict((('june', 1), ('july', 2), ('august', 3)))
                )
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
                )
        kila i, month kwenye enumerate('june july august'.split(), 1):
            e = SummerMonth(i)
            self.assertEqual(int(e.value), i)
            self.assertNotEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    eleza test_programmatic_function_type(self):
        SummerMonth = Enum('SummerMonth', 'june july august', type=int)
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
                )
        kila i, month kwenye enumerate('june july august'.split(), 1):
            e = SummerMonth(i)
            self.assertEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    eleza test_programmatic_function_type_with_start(self):
        SummerMonth = Enum('SummerMonth', 'june july august', type=int, start=30)
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
                )
        kila i, month kwenye enumerate('june july august'.split(), 30):
            e = SummerMonth(i)
            self.assertEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    eleza test_programmatic_function_type_from_subclass(self):
        SummerMonth = IntEnum('SummerMonth', 'june july august')
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
                )
        kila i, month kwenye enumerate('june july august'.split(), 1):
            e = SummerMonth(i)
            self.assertEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    eleza test_programmatic_function_type_from_subclass_with_start(self):
        SummerMonth = IntEnum('SummerMonth', 'june july august', start=40)
        lst = list(SummerMonth)
        self.assertEqual(len(lst), len(SummerMonth))
        self.assertEqual(len(SummerMonth), 3, SummerMonth)
        self.assertEqual(
                [SummerMonth.june, SummerMonth.july, SummerMonth.august],
                lst,
                )
        kila i, month kwenye enumerate('june july august'.split(), 40):
            e = SummerMonth(i)
            self.assertEqual(e, i)
            self.assertEqual(e.name, month)
            self.assertIn(e, SummerMonth)
            self.assertIs(type(e), SummerMonth)

    eleza test_subclassing(self):
        ikiwa isinstance(Name, Exception):
            ashiria Name
        self.assertEqual(Name.BDFL, 'Guido van Rossum')
        self.assertKweli(Name.BDFL, Name('Guido van Rossum'))
        self.assertIs(Name.BDFL, getattr(Name, 'BDFL'))
        test_pickle_dump_load(self.assertIs, Name.BDFL)

    eleza test_extending(self):
        kundi Color(Enum):
            red = 1
            green = 2
            blue = 3
        ukijumuisha self.assertRaises(TypeError):
            kundi MoreColor(Color):
                cyan = 4
                magenta = 5
                yellow = 6

    eleza test_exclude_methods(self):
        kundi whatever(Enum):
            this = 'that'
            these = 'those'
            eleza really(self):
                rudisha 'no, sio %s' % self.value
        self.assertIsNot(type(whatever.really), whatever)
        self.assertEqual(whatever.this.really(), 'no, sio that')

    eleza test_wrong_inheritance_order(self):
        ukijumuisha self.assertRaises(TypeError):
            kundi Wrong(Enum, str):
                NotHere = 'error before this point'

    eleza test_intenum_transitivity(self):
        kundi number(IntEnum):
            one = 1
            two = 2
            three = 3
        kundi numero(IntEnum):
            uno = 1
            dos = 2
            tres = 3
        self.assertEqual(number.one, numero.uno)
        self.assertEqual(number.two, numero.dos)
        self.assertEqual(number.three, numero.tres)

    eleza test_wrong_enum_in_call(self):
        kundi Monochrome(Enum):
            black = 0
            white = 1
        kundi Gender(Enum):
            male = 0
            female = 1
        self.assertRaises(ValueError, Monochrome, Gender.male)

    eleza test_wrong_enum_in_mixed_call(self):
        kundi Monochrome(IntEnum):
            black = 0
            white = 1
        kundi Gender(Enum):
            male = 0
            female = 1
        self.assertRaises(ValueError, Monochrome, Gender.male)

    eleza test_mixed_enum_in_call_1(self):
        kundi Monochrome(IntEnum):
            black = 0
            white = 1
        kundi Gender(IntEnum):
            male = 0
            female = 1
        self.assertIs(Monochrome(Gender.female), Monochrome.white)

    eleza test_mixed_enum_in_call_2(self):
        kundi Monochrome(Enum):
            black = 0
            white = 1
        kundi Gender(IntEnum):
            male = 0
            female = 1
        self.assertIs(Monochrome(Gender.male), Monochrome.black)

    eleza test_flufl_enum(self):
        kundi Fluflnum(Enum):
            eleza __int__(self):
                rudisha int(self.value)
        kundi MailManOptions(Fluflnum):
            option1 = 1
            option2 = 2
            option3 = 3
        self.assertEqual(int(MailManOptions.option1), 1)

    eleza test_introspection(self):
        kundi Number(IntEnum):
            one = 100
            two = 200
        self.assertIs(Number.one._member_type_, int)
        self.assertIs(Number._member_type_, int)
        kundi String(str, Enum):
            yarn = 'soft'
            rope = 'rough'
            wire = 'hard'
        self.assertIs(String.yarn._member_type_, str)
        self.assertIs(String._member_type_, str)
        kundi Plain(Enum):
            vanilla = 'white'
            one = 1
        self.assertIs(Plain.vanilla._member_type_, object)
        self.assertIs(Plain._member_type_, object)

    eleza test_no_such_enum_member(self):
        kundi Color(Enum):
            red = 1
            green = 2
            blue = 3
        ukijumuisha self.assertRaises(ValueError):
            Color(4)
        ukijumuisha self.assertRaises(KeyError):
            Color['chartreuse']

    eleza test_new_repr(self):
        kundi Color(Enum):
            red = 1
            green = 2
            blue = 3
            eleza __repr__(self):
                rudisha "don't you just love shades of %s?" % self.name
        self.assertEqual(
                repr(Color.blue),
                "don't you just love shades of blue?",
                )

    eleza test_inherited_repr(self):
        kundi MyEnum(Enum):
            eleza __repr__(self):
                rudisha "My name ni %s." % self.name
        kundi MyIntEnum(int, MyEnum):
            this = 1
            that = 2
            theother = 3
        self.assertEqual(repr(MyIntEnum.that), "My name ni that.")

    eleza test_multiple_mixin_mro(self):
        kundi auto_enum(type(Enum)):
            eleza __new__(metacls, cls, bases, classdict):
                temp = type(classdict)()
                names = set(classdict._member_names)
                i = 0
                kila k kwenye classdict._member_names:
                    v = classdict[k]
                    ikiwa v ni Ellipsis:
                        v = i
                    isipokua:
                        i = v
                    i += 1
                    temp[k] = v
                kila k, v kwenye classdict.items():
                    ikiwa k haiko kwenye names:
                        temp[k] = v
                rudisha super(auto_enum, metacls).__new__(
                        metacls, cls, bases, temp)

        kundi AutoNumberedEnum(Enum, metaclass=auto_enum):
            pita

        kundi AutoIntEnum(IntEnum, metaclass=auto_enum):
            pita

        kundi TestAutoNumber(AutoNumberedEnum):
            a = ...
            b = 3
            c = ...

        kundi TestAutoInt(AutoIntEnum):
            a = ...
            b = 3
            c = ...

    eleza test_subclasses_with_getnewargs(self):
        kundi NamedInt(int):
            __qualname__ = 'NamedInt'       # needed kila pickle protocol 4
            eleza __new__(cls, *args):
                _args = args
                name, *args = args
                ikiwa len(args) == 0:
                    ashiria TypeError("name na value must be specified")
                self = int.__new__(cls, *args)
                self._intname = name
                self._args = _args
                rudisha self
            eleza __getnewargs__(self):
                rudisha self._args
            @property
            eleza __name__(self):
                rudisha self._intname
            eleza __repr__(self):
                # repr() ni updated to include the name na type info
                rudisha "{}({!r}, {})".format(type(self).__name__,
                                             self.__name__,
                                             int.__repr__(self))
            eleza __str__(self):
                # str() ni unchanged, even ikiwa it relies on the repr() fallback
                base = int
                base_str = base.__str__
                ikiwa base_str.__objclass__ ni object:
                    rudisha base.__repr__(self)
                rudisha base_str(self)
            # kila simplicity, we only define one operator that
            # propagates expressions
            eleza __add__(self, other):
                temp = int(self) + int( other)
                ikiwa isinstance(self, NamedInt) na isinstance(other, NamedInt):
                    rudisha NamedInt(
                        '({0} + {1})'.format(self.__name__, other.__name__),
                        temp )
                isipokua:
                    rudisha temp

        kundi NEI(NamedInt, Enum):
            __qualname__ = 'NEI'      # needed kila pickle protocol 4
            x = ('the-x', 1)
            y = ('the-y', 2)


        self.assertIs(NEI.__new__, Enum.__new__)
        self.assertEqual(repr(NEI.x + NEI.y), "NamedInt('(the-x + the-y)', 3)")
        globals()['NamedInt'] = NamedInt
        globals()['NEI'] = NEI
        NI5 = NamedInt('test', 5)
        self.assertEqual(NI5, 5)
        test_pickle_dump_load(self.assertEqual, NI5, 5)
        self.assertEqual(NEI.y.value, 2)
        test_pickle_dump_load(self.assertIs, NEI.y)
        test_pickle_dump_load(self.assertIs, NEI)

    eleza test_subclasses_with_getnewargs_ex(self):
        kundi NamedInt(int):
            __qualname__ = 'NamedInt'       # needed kila pickle protocol 4
            eleza __new__(cls, *args):
                _args = args
                name, *args = args
                ikiwa len(args) == 0:
                    ashiria TypeError("name na value must be specified")
                self = int.__new__(cls, *args)
                self._intname = name
                self._args = _args
                rudisha self
            eleza __getnewargs_ex__(self):
                rudisha self._args, {}
            @property
            eleza __name__(self):
                rudisha self._intname
            eleza __repr__(self):
                # repr() ni updated to include the name na type info
                rudisha "{}({!r}, {})".format(type(self).__name__,
                                             self.__name__,
                                             int.__repr__(self))
            eleza __str__(self):
                # str() ni unchanged, even ikiwa it relies on the repr() fallback
                base = int
                base_str = base.__str__
                ikiwa base_str.__objclass__ ni object:
                    rudisha base.__repr__(self)
                rudisha base_str(self)
            # kila simplicity, we only define one operator that
            # propagates expressions
            eleza __add__(self, other):
                temp = int(self) + int( other)
                ikiwa isinstance(self, NamedInt) na isinstance(other, NamedInt):
                    rudisha NamedInt(
                        '({0} + {1})'.format(self.__name__, other.__name__),
                        temp )
                isipokua:
                    rudisha temp

        kundi NEI(NamedInt, Enum):
            __qualname__ = 'NEI'      # needed kila pickle protocol 4
            x = ('the-x', 1)
            y = ('the-y', 2)


        self.assertIs(NEI.__new__, Enum.__new__)
        self.assertEqual(repr(NEI.x + NEI.y), "NamedInt('(the-x + the-y)', 3)")
        globals()['NamedInt'] = NamedInt
        globals()['NEI'] = NEI
        NI5 = NamedInt('test', 5)
        self.assertEqual(NI5, 5)
        test_pickle_dump_load(self.assertEqual, NI5, 5)
        self.assertEqual(NEI.y.value, 2)
        test_pickle_dump_load(self.assertIs, NEI.y)
        test_pickle_dump_load(self.assertIs, NEI)

    eleza test_subclasses_with_reduce(self):
        kundi NamedInt(int):
            __qualname__ = 'NamedInt'       # needed kila pickle protocol 4
            eleza __new__(cls, *args):
                _args = args
                name, *args = args
                ikiwa len(args) == 0:
                    ashiria TypeError("name na value must be specified")
                self = int.__new__(cls, *args)
                self._intname = name
                self._args = _args
                rudisha self
            eleza __reduce__(self):
                rudisha self.__class__, self._args
            @property
            eleza __name__(self):
                rudisha self._intname
            eleza __repr__(self):
                # repr() ni updated to include the name na type info
                rudisha "{}({!r}, {})".format(type(self).__name__,
                                             self.__name__,
                                             int.__repr__(self))
            eleza __str__(self):
                # str() ni unchanged, even ikiwa it relies on the repr() fallback
                base = int
                base_str = base.__str__
                ikiwa base_str.__objclass__ ni object:
                    rudisha base.__repr__(self)
                rudisha base_str(self)
            # kila simplicity, we only define one operator that
            # propagates expressions
            eleza __add__(self, other):
                temp = int(self) + int( other)
                ikiwa isinstance(self, NamedInt) na isinstance(other, NamedInt):
                    rudisha NamedInt(
                        '({0} + {1})'.format(self.__name__, other.__name__),
                        temp )
                isipokua:
                    rudisha temp

        kundi NEI(NamedInt, Enum):
            __qualname__ = 'NEI'      # needed kila pickle protocol 4
            x = ('the-x', 1)
            y = ('the-y', 2)


        self.assertIs(NEI.__new__, Enum.__new__)
        self.assertEqual(repr(NEI.x + NEI.y), "NamedInt('(the-x + the-y)', 3)")
        globals()['NamedInt'] = NamedInt
        globals()['NEI'] = NEI
        NI5 = NamedInt('test', 5)
        self.assertEqual(NI5, 5)
        test_pickle_dump_load(self.assertEqual, NI5, 5)
        self.assertEqual(NEI.y.value, 2)
        test_pickle_dump_load(self.assertIs, NEI.y)
        test_pickle_dump_load(self.assertIs, NEI)

    eleza test_subclasses_with_reduce_ex(self):
        kundi NamedInt(int):
            __qualname__ = 'NamedInt'       # needed kila pickle protocol 4
            eleza __new__(cls, *args):
                _args = args
                name, *args = args
                ikiwa len(args) == 0:
                    ashiria TypeError("name na value must be specified")
                self = int.__new__(cls, *args)
                self._intname = name
                self._args = _args
                rudisha self
            eleza __reduce_ex__(self, proto):
                rudisha self.__class__, self._args
            @property
            eleza __name__(self):
                rudisha self._intname
            eleza __repr__(self):
                # repr() ni updated to include the name na type info
                rudisha "{}({!r}, {})".format(type(self).__name__,
                                             self.__name__,
                                             int.__repr__(self))
            eleza __str__(self):
                # str() ni unchanged, even ikiwa it relies on the repr() fallback
                base = int
                base_str = base.__str__
                ikiwa base_str.__objclass__ ni object:
                    rudisha base.__repr__(self)
                rudisha base_str(self)
            # kila simplicity, we only define one operator that
            # propagates expressions
            eleza __add__(self, other):
                temp = int(self) + int( other)
                ikiwa isinstance(self, NamedInt) na isinstance(other, NamedInt):
                    rudisha NamedInt(
                        '({0} + {1})'.format(self.__name__, other.__name__),
                        temp )
                isipokua:
                    rudisha temp

        kundi NEI(NamedInt, Enum):
            __qualname__ = 'NEI'      # needed kila pickle protocol 4
            x = ('the-x', 1)
            y = ('the-y', 2)


        self.assertIs(NEI.__new__, Enum.__new__)
        self.assertEqual(repr(NEI.x + NEI.y), "NamedInt('(the-x + the-y)', 3)")
        globals()['NamedInt'] = NamedInt
        globals()['NEI'] = NEI
        NI5 = NamedInt('test', 5)
        self.assertEqual(NI5, 5)
        test_pickle_dump_load(self.assertEqual, NI5, 5)
        self.assertEqual(NEI.y.value, 2)
        test_pickle_dump_load(self.assertIs, NEI.y)
        test_pickle_dump_load(self.assertIs, NEI)

    eleza test_subclasses_without_direct_pickle_support(self):
        kundi NamedInt(int):
            __qualname__ = 'NamedInt'
            eleza __new__(cls, *args):
                _args = args
                name, *args = args
                ikiwa len(args) == 0:
                    ashiria TypeError("name na value must be specified")
                self = int.__new__(cls, *args)
                self._intname = name
                self._args = _args
                rudisha self
            @property
            eleza __name__(self):
                rudisha self._intname
            eleza __repr__(self):
                # repr() ni updated to include the name na type info
                rudisha "{}({!r}, {})".format(type(self).__name__,
                                             self.__name__,
                                             int.__repr__(self))
            eleza __str__(self):
                # str() ni unchanged, even ikiwa it relies on the repr() fallback
                base = int
                base_str = base.__str__
                ikiwa base_str.__objclass__ ni object:
                    rudisha base.__repr__(self)
                rudisha base_str(self)
            # kila simplicity, we only define one operator that
            # propagates expressions
            eleza __add__(self, other):
                temp = int(self) + int( other)
                ikiwa isinstance(self, NamedInt) na isinstance(other, NamedInt):
                    rudisha NamedInt(
                        '({0} + {1})'.format(self.__name__, other.__name__),
                        temp )
                isipokua:
                    rudisha temp

        kundi NEI(NamedInt, Enum):
            __qualname__ = 'NEI'
            x = ('the-x', 1)
            y = ('the-y', 2)

        self.assertIs(NEI.__new__, Enum.__new__)
        self.assertEqual(repr(NEI.x + NEI.y), "NamedInt('(the-x + the-y)', 3)")
        globals()['NamedInt'] = NamedInt
        globals()['NEI'] = NEI
        NI5 = NamedInt('test', 5)
        self.assertEqual(NI5, 5)
        self.assertEqual(NEI.y.value, 2)
        test_pickle_exception(self.assertRaises, TypeError, NEI.x)
        test_pickle_exception(self.assertRaises, PicklingError, NEI)

    eleza test_subclasses_without_direct_pickle_support_using_name(self):
        kundi NamedInt(int):
            __qualname__ = 'NamedInt'
            eleza __new__(cls, *args):
                _args = args
                name, *args = args
                ikiwa len(args) == 0:
                    ashiria TypeError("name na value must be specified")
                self = int.__new__(cls, *args)
                self._intname = name
                self._args = _args
                rudisha self
            @property
            eleza __name__(self):
                rudisha self._intname
            eleza __repr__(self):
                # repr() ni updated to include the name na type info
                rudisha "{}({!r}, {})".format(type(self).__name__,
                                             self.__name__,
                                             int.__repr__(self))
            eleza __str__(self):
                # str() ni unchanged, even ikiwa it relies on the repr() fallback
                base = int
                base_str = base.__str__
                ikiwa base_str.__objclass__ ni object:
                    rudisha base.__repr__(self)
                rudisha base_str(self)
            # kila simplicity, we only define one operator that
            # propagates expressions
            eleza __add__(self, other):
                temp = int(self) + int( other)
                ikiwa isinstance(self, NamedInt) na isinstance(other, NamedInt):
                    rudisha NamedInt(
                        '({0} + {1})'.format(self.__name__, other.__name__),
                        temp )
                isipokua:
                    rudisha temp

        kundi NEI(NamedInt, Enum):
            __qualname__ = 'NEI'
            x = ('the-x', 1)
            y = ('the-y', 2)
            eleza __reduce_ex__(self, proto):
                rudisha getattr, (self.__class__, self._name_)

        self.assertIs(NEI.__new__, Enum.__new__)
        self.assertEqual(repr(NEI.x + NEI.y), "NamedInt('(the-x + the-y)', 3)")
        globals()['NamedInt'] = NamedInt
        globals()['NEI'] = NEI
        NI5 = NamedInt('test', 5)
        self.assertEqual(NI5, 5)
        self.assertEqual(NEI.y.value, 2)
        test_pickle_dump_load(self.assertIs, NEI.y)
        test_pickle_dump_load(self.assertIs, NEI)

    eleza test_tuple_subclass(self):
        kundi SomeTuple(tuple, Enum):
            __qualname__ = 'SomeTuple'      # needed kila pickle protocol 4
            first = (1, 'kila the money')
            second = (2, 'kila the show')
            third = (3, 'kila the music')
        self.assertIs(type(SomeTuple.first), SomeTuple)
        self.assertIsInstance(SomeTuple.second, tuple)
        self.assertEqual(SomeTuple.third, (3, 'kila the music'))
        globals()['SomeTuple'] = SomeTuple
        test_pickle_dump_load(self.assertIs, SomeTuple.first)

    eleza test_duplicate_values_give_unique_enum_items(self):
        kundi AutoNumber(Enum):
            first = ()
            second = ()
            third = ()
            eleza __new__(cls):
                value = len(cls.__members__) + 1
                obj = object.__new__(cls)
                obj._value_ = value
                rudisha obj
            eleza __int__(self):
                rudisha int(self._value_)
        self.assertEqual(
                list(AutoNumber),
                [AutoNumber.first, AutoNumber.second, AutoNumber.third],
                )
        self.assertEqual(int(AutoNumber.second), 2)
        self.assertEqual(AutoNumber.third.value, 3)
        self.assertIs(AutoNumber(1), AutoNumber.first)

    eleza test_inherited_new_from_enhanced_enum(self):
        kundi AutoNumber(Enum):
            eleza __new__(cls):
                value = len(cls.__members__) + 1
                obj = object.__new__(cls)
                obj._value_ = value
                rudisha obj
            eleza __int__(self):
                rudisha int(self._value_)
        kundi Color(AutoNumber):
            red = ()
            green = ()
            blue = ()
        self.assertEqual(list(Color), [Color.red, Color.green, Color.blue])
        self.assertEqual(list(map(int, Color)), [1, 2, 3])

    eleza test_inherited_new_from_mixed_enum(self):
        kundi AutoNumber(IntEnum):
            eleza __new__(cls):
                value = len(cls.__members__) + 1
                obj = int.__new__(cls, value)
                obj._value_ = value
                rudisha obj
        kundi Color(AutoNumber):
            red = ()
            green = ()
            blue = ()
        self.assertEqual(list(Color), [Color.red, Color.green, Color.blue])
        self.assertEqual(list(map(int, Color)), [1, 2, 3])

    eleza test_equality(self):
        kundi AlwaysEqual:
            eleza __eq__(self, other):
                rudisha Kweli
        kundi OrdinaryEnum(Enum):
            a = 1
        self.assertEqual(AlwaysEqual(), OrdinaryEnum.a)
        self.assertEqual(OrdinaryEnum.a, AlwaysEqual())

    eleza test_ordered_mixin(self):
        kundi OrderedEnum(Enum):
            eleza __ge__(self, other):
                ikiwa self.__class__ ni other.__class__:
                    rudisha self._value_ >= other._value_
                rudisha NotImplemented
            eleza __gt__(self, other):
                ikiwa self.__class__ ni other.__class__:
                    rudisha self._value_ > other._value_
                rudisha NotImplemented
            eleza __le__(self, other):
                ikiwa self.__class__ ni other.__class__:
                    rudisha self._value_ <= other._value_
                rudisha NotImplemented
            eleza __lt__(self, other):
                ikiwa self.__class__ ni other.__class__:
                    rudisha self._value_ < other._value_
                rudisha NotImplemented
        kundi Grade(OrderedEnum):
            A = 5
            B = 4
            C = 3
            D = 2
            F = 1
        self.assertGreater(Grade.A, Grade.B)
        self.assertLessEqual(Grade.F, Grade.C)
        self.assertLess(Grade.D, Grade.A)
        self.assertGreaterEqual(Grade.B, Grade.B)
        self.assertEqual(Grade.B, Grade.B)
        self.assertNotEqual(Grade.C, Grade.D)

    eleza test_extending2(self):
        kundi Shade(Enum):
            eleza shade(self):
                andika(self.name)
        kundi Color(Shade):
            red = 1
            green = 2
            blue = 3
        ukijumuisha self.assertRaises(TypeError):
            kundi MoreColor(Color):
                cyan = 4
                magenta = 5
                yellow = 6

    eleza test_extending3(self):
        kundi Shade(Enum):
            eleza shade(self):
                rudisha self.name
        kundi Color(Shade):
            eleza hex(self):
                rudisha '%s hexlified!' % self.value
        kundi MoreColor(Color):
            cyan = 4
            magenta = 5
            yellow = 6
        self.assertEqual(MoreColor.magenta.hex(), '5 hexlified!')

    eleza test_subclass_duplicate_name(self):
        kundi Base(Enum):
            eleza test(self):
                pita
        kundi Test(Base):
            test = 1
        self.assertIs(type(Test.test), Test)

    eleza test_subclass_duplicate_name_dynamic(self):
        kutoka types agiza DynamicClassAttribute
        kundi Base(Enum):
            @DynamicClassAttribute
            eleza test(self):
                rudisha 'dynamic'
        kundi Test(Base):
            test = 1
        self.assertEqual(Test.test.test, 'dynamic')

    eleza test_no_duplicates(self):
        kundi UniqueEnum(Enum):
            eleza __init__(self, *args):
                cls = self.__class__
                ikiwa any(self.value == e.value kila e kwenye cls):
                    a = self.name
                    e = cls(self.value).name
                    ashiria ValueError(
                            "aliases sio allowed kwenye UniqueEnum:  %r --> %r"
                            % (a, e)
                            )
        kundi Color(UniqueEnum):
            red = 1
            green = 2
            blue = 3
        ukijumuisha self.assertRaises(ValueError):
            kundi Color(UniqueEnum):
                red = 1
                green = 2
                blue = 3
                grene = 2

    eleza test_init(self):
        kundi Planet(Enum):
            MERCURY = (3.303e+23, 2.4397e6)
            VENUS   = (4.869e+24, 6.0518e6)
            EARTH   = (5.976e+24, 6.37814e6)
            MARS    = (6.421e+23, 3.3972e6)
            JUPITER = (1.9e+27,   7.1492e7)
            SATURN  = (5.688e+26, 6.0268e7)
            URANUS  = (8.686e+25, 2.5559e7)
            NEPTUNE = (1.024e+26, 2.4746e7)
            eleza __init__(self, mass, radius):
                self.mass = mass       # kwenye kilograms
                self.radius = radius   # kwenye meters
            @property
            eleza surface_gravity(self):
                # universal gravitational constant  (m3 kg-1 s-2)
                G = 6.67300E-11
                rudisha G * self.mass / (self.radius * self.radius)
        self.assertEqual(round(Planet.EARTH.surface_gravity, 2), 9.80)
        self.assertEqual(Planet.EARTH.value, (5.976e+24, 6.37814e6))

    eleza test_ignore(self):
        kundi Period(timedelta, Enum):
            '''
            different lengths of time
            '''
            eleza __new__(cls, value, period):
                obj = timedelta.__new__(cls, value)
                obj._value_ = value
                obj.period = period
                rudisha obj
            _ignore_ = 'Period i'
            Period = vars()
            kila i kwenye range(13):
                Period['month_%d' % i] = i*30, 'month'
            kila i kwenye range(53):
                Period['week_%d' % i] = i*7, 'week'
            kila i kwenye range(32):
                Period['day_%d' % i] = i, 'day'
            OneDay = day_1
            OneWeek = week_1
            OneMonth = month_1
        self.assertUongo(hasattr(Period, '_ignore_'))
        self.assertUongo(hasattr(Period, 'Period'))
        self.assertUongo(hasattr(Period, 'i'))
        self.assertKweli(isinstance(Period.day_1, timedelta))
        self.assertKweli(Period.month_1 ni Period.day_30)
        self.assertKweli(Period.week_4 ni Period.day_28)

    eleza test_nonhash_value(self):
        kundi AutoNumberInAList(Enum):
            eleza __new__(cls):
                value = [len(cls.__members__) + 1]
                obj = object.__new__(cls)
                obj._value_ = value
                rudisha obj
        kundi ColorInAList(AutoNumberInAList):
            red = ()
            green = ()
            blue = ()
        self.assertEqual(list(ColorInAList), [ColorInAList.red, ColorInAList.green, ColorInAList.blue])
        kila enum, value kwenye zip(ColorInAList, range(3)):
            value += 1
            self.assertEqual(enum.value, [value])
            self.assertIs(ColorInAList([value]), enum)

    eleza test_conflicting_types_resolved_in_new(self):
        kundi LabelledIntEnum(int, Enum):
            eleza __new__(cls, *args):
                value, label = args
                obj = int.__new__(cls, value)
                obj.label = label
                obj._value_ = value
                rudisha obj

        kundi LabelledList(LabelledIntEnum):
            unprocessed = (1, "Unprocessed")
            payment_complete = (2, "Payment Complete")

        self.assertEqual(list(LabelledList), [LabelledList.unprocessed, LabelledList.payment_complete])
        self.assertEqual(LabelledList.unprocessed, 1)
        self.assertEqual(LabelledList(1), LabelledList.unprocessed)

    eleza test_auto_number(self):
        kundi Color(Enum):
            red = auto()
            blue = auto()
            green = auto()

        self.assertEqual(list(Color), [Color.red, Color.blue, Color.green])
        self.assertEqual(Color.red.value, 1)
        self.assertEqual(Color.blue.value, 2)
        self.assertEqual(Color.green.value, 3)

    eleza test_auto_name(self):
        kundi Color(Enum):
            eleza _generate_next_value_(name, start, count, last):
                rudisha name
            red = auto()
            blue = auto()
            green = auto()

        self.assertEqual(list(Color), [Color.red, Color.blue, Color.green])
        self.assertEqual(Color.red.value, 'red')
        self.assertEqual(Color.blue.value, 'blue')
        self.assertEqual(Color.green.value, 'green')

    eleza test_auto_name_inherit(self):
        kundi AutoNameEnum(Enum):
            eleza _generate_next_value_(name, start, count, last):
                rudisha name
        kundi Color(AutoNameEnum):
            red = auto()
            blue = auto()
            green = auto()

        self.assertEqual(list(Color), [Color.red, Color.blue, Color.green])
        self.assertEqual(Color.red.value, 'red')
        self.assertEqual(Color.blue.value, 'blue')
        self.assertEqual(Color.green.value, 'green')

    eleza test_auto_garbage(self):
        kundi Color(Enum):
            red = 'red'
            blue = auto()
        self.assertEqual(Color.blue.value, 1)

    eleza test_auto_garbage_corrected(self):
        kundi Color(Enum):
            red = 'red'
            blue = 2
            green = auto()

        self.assertEqual(list(Color), [Color.red, Color.blue, Color.green])
        self.assertEqual(Color.red.value, 'red')
        self.assertEqual(Color.blue.value, 2)
        self.assertEqual(Color.green.value, 3)

    eleza test_duplicate_auto(self):
        kundi Dupes(Enum):
            first = primero = auto()
            second = auto()
            third = auto()
        self.assertEqual([Dupes.first, Dupes.second, Dupes.third], list(Dupes))

    eleza test_missing(self):
        kundi Color(Enum):
            red = 1
            green = 2
            blue = 3
            @classmethod
            eleza _missing_(cls, item):
                ikiwa item == 'three':
                    rudisha cls.blue
                lasivyo item == 'bad return':
                    # trigger internal error
                    rudisha 5
                lasivyo item == 'error out':
                    ashiria ZeroDivisionError
                isipokua:
                    # trigger sio found
                    rudisha Tupu
        self.assertIs(Color('three'), Color.blue)
        self.assertRaises(ValueError, Color, 7)
        jaribu:
            Color('bad return')
        tatizo TypeError kama exc:
            self.assertKweli(isinstance(exc.__context__, ValueError))
        isipokua:
            ashiria Exception('Exception sio raised.')
        jaribu:
            Color('error out')
        tatizo ZeroDivisionError kama exc:
            self.assertKweli(isinstance(exc.__context__, ValueError))
        isipokua:
            ashiria Exception('Exception sio raised.')

    eleza test_multiple_mixin(self):
        kundi MaxMixin:
            @classproperty
            eleza MAX(cls):
                max = len(cls)
                cls.MAX = max
                rudisha max
        kundi StrMixin:
            eleza __str__(self):
                rudisha self._name_.lower()
        kundi SomeEnum(Enum):
            eleza behavior(self):
                rudisha 'booyah'
        kundi AnotherEnum(Enum):
            eleza behavior(self):
                rudisha 'nuhuh!'
            eleza social(self):
                rudisha "what's up?"
        kundi Color(MaxMixin, Enum):
            RED = auto()
            GREEN = auto()
            BLUE = auto()
        self.assertEqual(Color.RED.value, 1)
        self.assertEqual(Color.GREEN.value, 2)
        self.assertEqual(Color.BLUE.value, 3)
        self.assertEqual(Color.MAX, 3)
        self.assertEqual(str(Color.BLUE), 'Color.BLUE')
        kundi Color(MaxMixin, StrMixin, Enum):
            RED = auto()
            GREEN = auto()
            BLUE = auto()
        self.assertEqual(Color.RED.value, 1)
        self.assertEqual(Color.GREEN.value, 2)
        self.assertEqual(Color.BLUE.value, 3)
        self.assertEqual(Color.MAX, 3)
        self.assertEqual(str(Color.BLUE), 'blue')
        kundi Color(StrMixin, MaxMixin, Enum):
            RED = auto()
            GREEN = auto()
            BLUE = auto()
        self.assertEqual(Color.RED.value, 1)
        self.assertEqual(Color.GREEN.value, 2)
        self.assertEqual(Color.BLUE.value, 3)
        self.assertEqual(Color.MAX, 3)
        self.assertEqual(str(Color.BLUE), 'blue')
        kundi CoolColor(StrMixin, SomeEnum, Enum):
            RED = auto()
            GREEN = auto()
            BLUE = auto()
        self.assertEqual(CoolColor.RED.value, 1)
        self.assertEqual(CoolColor.GREEN.value, 2)
        self.assertEqual(CoolColor.BLUE.value, 3)
        self.assertEqual(str(CoolColor.BLUE), 'blue')
        self.assertEqual(CoolColor.RED.behavior(), 'booyah')
        kundi CoolerColor(StrMixin, AnotherEnum, Enum):
            RED = auto()
            GREEN = auto()
            BLUE = auto()
        self.assertEqual(CoolerColor.RED.value, 1)
        self.assertEqual(CoolerColor.GREEN.value, 2)
        self.assertEqual(CoolerColor.BLUE.value, 3)
        self.assertEqual(str(CoolerColor.BLUE), 'blue')
        self.assertEqual(CoolerColor.RED.behavior(), 'nuhuh!')
        self.assertEqual(CoolerColor.RED.social(), "what's up?")
        kundi CoolestColor(StrMixin, SomeEnum, AnotherEnum):
            RED = auto()
            GREEN = auto()
            BLUE = auto()
        self.assertEqual(CoolestColor.RED.value, 1)
        self.assertEqual(CoolestColor.GREEN.value, 2)
        self.assertEqual(CoolestColor.BLUE.value, 3)
        self.assertEqual(str(CoolestColor.BLUE), 'blue')
        self.assertEqual(CoolestColor.RED.behavior(), 'booyah')
        self.assertEqual(CoolestColor.RED.social(), "what's up?")
        kundi ConfusedColor(StrMixin, AnotherEnum, SomeEnum):
            RED = auto()
            GREEN = auto()
            BLUE = auto()
        self.assertEqual(ConfusedColor.RED.value, 1)
        self.assertEqual(ConfusedColor.GREEN.value, 2)
        self.assertEqual(ConfusedColor.BLUE.value, 3)
        self.assertEqual(str(ConfusedColor.BLUE), 'blue')
        self.assertEqual(ConfusedColor.RED.behavior(), 'nuhuh!')
        self.assertEqual(ConfusedColor.RED.social(), "what's up?")
        kundi ReformedColor(StrMixin, IntEnum, SomeEnum, AnotherEnum):
            RED = auto()
            GREEN = auto()
            BLUE = auto()
        self.assertEqual(ReformedColor.RED.value, 1)
        self.assertEqual(ReformedColor.GREEN.value, 2)
        self.assertEqual(ReformedColor.BLUE.value, 3)
        self.assertEqual(str(ReformedColor.BLUE), 'blue')
        self.assertEqual(ReformedColor.RED.behavior(), 'booyah')
        self.assertEqual(ConfusedColor.RED.social(), "what's up?")
        self.assertKweli(issubclass(ReformedColor, int))

    eleza test_multiple_inherited_mixin(self):
        kundi StrEnum(str, Enum):
            eleza __new__(cls, *args, **kwargs):
                kila a kwenye args:
                    ikiwa sio isinstance(a, str):
                        ashiria TypeError("Enumeration '%s' (%s) ni not"
                                        " a string" % (a, type(a).__name__))
                rudisha str.__new__(cls, *args, **kwargs)
        @unique
        kundi Decision1(StrEnum):
            REVERT = "REVERT"
            REVERT_ALL = "REVERT_ALL"
            RETRY = "RETRY"
        kundi MyEnum(StrEnum):
            pita
        @unique
        kundi Decision2(MyEnum):
            REVERT = "REVERT"
            REVERT_ALL = "REVERT_ALL"
            RETRY = "RETRY"

    eleza test_empty_globals(self):
        # bpo-35717: sys._getframe(2).f_globals['__name__'] fails ukijumuisha KeyError
        # when using compile na exec because f_globals ni empty
        code = "kutoka enum agiza Enum; Enum('Animal', 'ANT BEE CAT DOG')"
        code = compile(code, "<string>", "exec")
        global_ns = {}
        local_ls = {}
        exec(code, global_ns, local_ls)


kundi TestOrder(unittest.TestCase):

    eleza test_same_members(self):
        kundi Color(Enum):
            _order_ = 'red green blue'
            red = 1
            green = 2
            blue = 3

    eleza test_same_members_with_aliases(self):
        kundi Color(Enum):
            _order_ = 'red green blue'
            red = 1
            green = 2
            blue = 3
            verde = green

    eleza test_same_members_wrong_order(self):
        ukijumuisha self.assertRaisesRegex(TypeError, 'member order does sio match _order_'):
            kundi Color(Enum):
                _order_ = 'red green blue'
                red = 1
                blue = 3
                green = 2

    eleza test_order_has_extra_members(self):
        ukijumuisha self.assertRaisesRegex(TypeError, 'member order does sio match _order_'):
            kundi Color(Enum):
                _order_ = 'red green blue purple'
                red = 1
                green = 2
                blue = 3

    eleza test_order_has_extra_members_with_aliases(self):
        ukijumuisha self.assertRaisesRegex(TypeError, 'member order does sio match _order_'):
            kundi Color(Enum):
                _order_ = 'red green blue purple'
                red = 1
                green = 2
                blue = 3
                verde = green

    eleza test_enum_has_extra_members(self):
        ukijumuisha self.assertRaisesRegex(TypeError, 'member order does sio match _order_'):
            kundi Color(Enum):
                _order_ = 'red green blue'
                red = 1
                green = 2
                blue = 3
                purple = 4

    eleza test_enum_has_extra_members_with_aliases(self):
        ukijumuisha self.assertRaisesRegex(TypeError, 'member order does sio match _order_'):
            kundi Color(Enum):
                _order_ = 'red green blue'
                red = 1
                green = 2
                blue = 3
                purple = 4
                verde = green


kundi TestFlag(unittest.TestCase):
    """Tests of the Flags."""

    kundi Perm(Flag):
        R, W, X = 4, 2, 1

    kundi Open(Flag):
        RO = 0
        WO = 1
        RW = 2
        AC = 3
        CE = 1<<19

    kundi Color(Flag):
        BLACK = 0
        RED = 1
        GREEN = 2
        BLUE = 4
        PURPLE = RED|BLUE

    eleza test_str(self):
        Perm = self.Perm
        self.assertEqual(str(Perm.R), 'Perm.R')
        self.assertEqual(str(Perm.W), 'Perm.W')
        self.assertEqual(str(Perm.X), 'Perm.X')
        self.assertEqual(str(Perm.R | Perm.W), 'Perm.R|W')
        self.assertEqual(str(Perm.R | Perm.W | Perm.X), 'Perm.R|W|X')
        self.assertEqual(str(Perm(0)), 'Perm.0')
        self.assertEqual(str(~Perm.R), 'Perm.W|X')
        self.assertEqual(str(~Perm.W), 'Perm.R|X')
        self.assertEqual(str(~Perm.X), 'Perm.R|W')
        self.assertEqual(str(~(Perm.R | Perm.W)), 'Perm.X')
        self.assertEqual(str(~(Perm.R | Perm.W | Perm.X)), 'Perm.0')
        self.assertEqual(str(Perm(~0)), 'Perm.R|W|X')

        Open = self.Open
        self.assertEqual(str(Open.RO), 'Open.RO')
        self.assertEqual(str(Open.WO), 'Open.WO')
        self.assertEqual(str(Open.AC), 'Open.AC')
        self.assertEqual(str(Open.RO | Open.CE), 'Open.CE')
        self.assertEqual(str(Open.WO | Open.CE), 'Open.CE|WO')
        self.assertEqual(str(~Open.RO), 'Open.CE|AC|RW|WO')
        self.assertEqual(str(~Open.WO), 'Open.CE|RW')
        self.assertEqual(str(~Open.AC), 'Open.CE')
        self.assertEqual(str(~(Open.RO | Open.CE)), 'Open.AC')
        self.assertEqual(str(~(Open.WO | Open.CE)), 'Open.RW')

    eleza test_repr(self):
        Perm = self.Perm
        self.assertEqual(repr(Perm.R), '<Perm.R: 4>')
        self.assertEqual(repr(Perm.W), '<Perm.W: 2>')
        self.assertEqual(repr(Perm.X), '<Perm.X: 1>')
        self.assertEqual(repr(Perm.R | Perm.W), '<Perm.R|W: 6>')
        self.assertEqual(repr(Perm.R | Perm.W | Perm.X), '<Perm.R|W|X: 7>')
        self.assertEqual(repr(Perm(0)), '<Perm.0: 0>')
        self.assertEqual(repr(~Perm.R), '<Perm.W|X: 3>')
        self.assertEqual(repr(~Perm.W), '<Perm.R|X: 5>')
        self.assertEqual(repr(~Perm.X), '<Perm.R|W: 6>')
        self.assertEqual(repr(~(Perm.R | Perm.W)), '<Perm.X: 1>')
        self.assertEqual(repr(~(Perm.R | Perm.W | Perm.X)), '<Perm.0: 0>')
        self.assertEqual(repr(Perm(~0)), '<Perm.R|W|X: 7>')

        Open = self.Open
        self.assertEqual(repr(Open.RO), '<Open.RO: 0>')
        self.assertEqual(repr(Open.WO), '<Open.WO: 1>')
        self.assertEqual(repr(Open.AC), '<Open.AC: 3>')
        self.assertEqual(repr(Open.RO | Open.CE), '<Open.CE: 524288>')
        self.assertEqual(repr(Open.WO | Open.CE), '<Open.CE|WO: 524289>')
        self.assertEqual(repr(~Open.RO), '<Open.CE|AC|RW|WO: 524291>')
        self.assertEqual(repr(~Open.WO), '<Open.CE|RW: 524290>')
        self.assertEqual(repr(~Open.AC), '<Open.CE: 524288>')
        self.assertEqual(repr(~(Open.RO | Open.CE)), '<Open.AC: 3>')
        self.assertEqual(repr(~(Open.WO | Open.CE)), '<Open.RW: 2>')

    eleza test_or(self):
        Perm = self.Perm
        kila i kwenye Perm:
            kila j kwenye Perm:
                self.assertEqual((i | j), Perm(i.value | j.value))
                self.assertEqual((i | j).value, i.value | j.value)
                self.assertIs(type(i | j), Perm)
        kila i kwenye Perm:
            self.assertIs(i | i, i)
        Open = self.Open
        self.assertIs(Open.RO | Open.CE, Open.CE)

    eleza test_and(self):
        Perm = self.Perm
        RW = Perm.R | Perm.W
        RX = Perm.R | Perm.X
        WX = Perm.W | Perm.X
        RWX = Perm.R | Perm.W | Perm.X
        values = list(Perm) + [RW, RX, WX, RWX, Perm(0)]
        kila i kwenye values:
            kila j kwenye values:
                self.assertEqual((i & j).value, i.value & j.value)
                self.assertIs(type(i & j), Perm)
        kila i kwenye Perm:
            self.assertIs(i & i, i)
            self.assertIs(i & RWX, i)
            self.assertIs(RWX & i, i)
        Open = self.Open
        self.assertIs(Open.RO & Open.CE, Open.RO)

    eleza test_xor(self):
        Perm = self.Perm
        kila i kwenye Perm:
            kila j kwenye Perm:
                self.assertEqual((i ^ j).value, i.value ^ j.value)
                self.assertIs(type(i ^ j), Perm)
        kila i kwenye Perm:
            self.assertIs(i ^ Perm(0), i)
            self.assertIs(Perm(0) ^ i, i)
        Open = self.Open
        self.assertIs(Open.RO ^ Open.CE, Open.CE)
        self.assertIs(Open.CE ^ Open.CE, Open.RO)

    eleza test_invert(self):
        Perm = self.Perm
        RW = Perm.R | Perm.W
        RX = Perm.R | Perm.X
        WX = Perm.W | Perm.X
        RWX = Perm.R | Perm.W | Perm.X
        values = list(Perm) + [RW, RX, WX, RWX, Perm(0)]
        kila i kwenye values:
            self.assertIs(type(~i), Perm)
            self.assertEqual(~~i, i)
        kila i kwenye Perm:
            self.assertIs(~~i, i)
        Open = self.Open
        self.assertIs(Open.WO & ~Open.WO, Open.RO)
        self.assertIs((Open.WO|Open.CE) & ~Open.WO, Open.CE)

    eleza test_bool(self):
        Perm = self.Perm
        kila f kwenye Perm:
            self.assertKweli(f)
        Open = self.Open
        kila f kwenye Open:
            self.assertEqual(bool(f.value), bool(f))

    eleza test_programatic_function_string(self):
        Perm = Flag('Perm', 'R W X')
        lst = list(Perm)
        self.assertEqual(len(lst), len(Perm))
        self.assertEqual(len(Perm), 3, Perm)
        self.assertEqual(lst, [Perm.R, Perm.W, Perm.X])
        kila i, n kwenye enumerate('R W X'.split()):
            v = 1<<i
            e = Perm(v)
            self.assertEqual(e.value, v)
            self.assertEqual(type(e.value), int)
            self.assertEqual(e.name, n)
            self.assertIn(e, Perm)
            self.assertIs(type(e), Perm)

    eleza test_programatic_function_string_with_start(self):
        Perm = Flag('Perm', 'R W X', start=8)
        lst = list(Perm)
        self.assertEqual(len(lst), len(Perm))
        self.assertEqual(len(Perm), 3, Perm)
        self.assertEqual(lst, [Perm.R, Perm.W, Perm.X])
        kila i, n kwenye enumerate('R W X'.split()):
            v = 8<<i
            e = Perm(v)
            self.assertEqual(e.value, v)
            self.assertEqual(type(e.value), int)
            self.assertEqual(e.name, n)
            self.assertIn(e, Perm)
            self.assertIs(type(e), Perm)

    eleza test_programatic_function_string_list(self):
        Perm = Flag('Perm', ['R', 'W', 'X'])
        lst = list(Perm)
        self.assertEqual(len(lst), len(Perm))
        self.assertEqual(len(Perm), 3, Perm)
        self.assertEqual(lst, [Perm.R, Perm.W, Perm.X])
        kila i, n kwenye enumerate('R W X'.split()):
            v = 1<<i
            e = Perm(v)
            self.assertEqual(e.value, v)
            self.assertEqual(type(e.value), int)
            self.assertEqual(e.name, n)
            self.assertIn(e, Perm)
            self.assertIs(type(e), Perm)

    eleza test_programatic_function_iterable(self):
        Perm = Flag('Perm', (('R', 2), ('W', 8), ('X', 32)))
        lst = list(Perm)
        self.assertEqual(len(lst), len(Perm))
        self.assertEqual(len(Perm), 3, Perm)
        self.assertEqual(lst, [Perm.R, Perm.W, Perm.X])
        kila i, n kwenye enumerate('R W X'.split()):
            v = 1<<(2*i+1)
            e = Perm(v)
            self.assertEqual(e.value, v)
            self.assertEqual(type(e.value), int)
            self.assertEqual(e.name, n)
            self.assertIn(e, Perm)
            self.assertIs(type(e), Perm)

    eleza test_programatic_function_from_dict(self):
        Perm = Flag('Perm', OrderedDict((('R', 2), ('W', 8), ('X', 32))))
        lst = list(Perm)
        self.assertEqual(len(lst), len(Perm))
        self.assertEqual(len(Perm), 3, Perm)
        self.assertEqual(lst, [Perm.R, Perm.W, Perm.X])
        kila i, n kwenye enumerate('R W X'.split()):
            v = 1<<(2*i+1)
            e = Perm(v)
            self.assertEqual(e.value, v)
            self.assertEqual(type(e.value), int)
            self.assertEqual(e.name, n)
            self.assertIn(e, Perm)
            self.assertIs(type(e), Perm)

    eleza test_pickle(self):
        ikiwa isinstance(FlagStooges, Exception):
            ashiria FlagStooges
        test_pickle_dump_load(self.assertIs, FlagStooges.CURLY|FlagStooges.MOE)
        test_pickle_dump_load(self.assertIs, FlagStooges)

    eleza test_contains(self):
        Open = self.Open
        Color = self.Color
        self.assertUongo(Color.BLACK kwenye Open)
        self.assertUongo(Open.RO kwenye Color)
        ukijumuisha self.assertRaises(TypeError):
            'BLACK' kwenye Color
        ukijumuisha self.assertRaises(TypeError):
            'RO' kwenye Open
        ukijumuisha self.assertRaises(TypeError):
            1 kwenye Color
        ukijumuisha self.assertRaises(TypeError):
            1 kwenye Open

    eleza test_member_contains(self):
        Perm = self.Perm
        R, W, X = Perm
        RW = R | W
        RX = R | X
        WX = W | X
        RWX = R | W | X
        self.assertKweli(R kwenye RW)
        self.assertKweli(R kwenye RX)
        self.assertKweli(R kwenye RWX)
        self.assertKweli(W kwenye RW)
        self.assertKweli(W kwenye WX)
        self.assertKweli(W kwenye RWX)
        self.assertKweli(X kwenye RX)
        self.assertKweli(X kwenye WX)
        self.assertKweli(X kwenye RWX)
        self.assertUongo(R kwenye WX)
        self.assertUongo(W kwenye RX)
        self.assertUongo(X kwenye RW)

    eleza test_auto_number(self):
        kundi Color(Flag):
            red = auto()
            blue = auto()
            green = auto()

        self.assertEqual(list(Color), [Color.red, Color.blue, Color.green])
        self.assertEqual(Color.red.value, 1)
        self.assertEqual(Color.blue.value, 2)
        self.assertEqual(Color.green.value, 4)

    eleza test_auto_number_garbage(self):
        ukijumuisha self.assertRaisesRegex(TypeError, 'Invalid Flag value: .not an int.'):
            kundi Color(Flag):
                red = 'not an int'
                blue = auto()

    eleza test_cascading_failure(self):
        kundi Bizarre(Flag):
            c = 3
            d = 4
            f = 6
        # Bizarre.c | Bizarre.d
        self.assertRaisesRegex(ValueError, "5 ni sio a valid Bizarre", Bizarre, 5)
        self.assertRaisesRegex(ValueError, "5 ni sio a valid Bizarre", Bizarre, 5)
        self.assertRaisesRegex(ValueError, "2 ni sio a valid Bizarre", Bizarre, 2)
        self.assertRaisesRegex(ValueError, "2 ni sio a valid Bizarre", Bizarre, 2)
        self.assertRaisesRegex(ValueError, "1 ni sio a valid Bizarre", Bizarre, 1)
        self.assertRaisesRegex(ValueError, "1 ni sio a valid Bizarre", Bizarre, 1)

    eleza test_duplicate_auto(self):
        kundi Dupes(Enum):
            first = primero = auto()
            second = auto()
            third = auto()
        self.assertEqual([Dupes.first, Dupes.second, Dupes.third], list(Dupes))

    eleza test_bizarre(self):
        kundi Bizarre(Flag):
            b = 3
            c = 4
            d = 6
        self.assertEqual(repr(Bizarre(7)), '<Bizarre.d|c|b: 7>')

    eleza test_multiple_mixin(self):
        kundi AllMixin:
            @classproperty
            eleza ALL(cls):
                members = list(cls)
                all_value = Tupu
                ikiwa members:
                    all_value = members[0]
                    kila member kwenye members[1:]:
                        all_value |= member
                cls.ALL = all_value
                rudisha all_value
        kundi StrMixin:
            eleza __str__(self):
                rudisha self._name_.lower()
        kundi Color(AllMixin, Flag):
            RED = auto()
            GREEN = auto()
            BLUE = auto()
        self.assertEqual(Color.RED.value, 1)
        self.assertEqual(Color.GREEN.value, 2)
        self.assertEqual(Color.BLUE.value, 4)
        self.assertEqual(Color.ALL.value, 7)
        self.assertEqual(str(Color.BLUE), 'Color.BLUE')
        kundi Color(AllMixin, StrMixin, Flag):
            RED = auto()
            GREEN = auto()
            BLUE = auto()
        self.assertEqual(Color.RED.value, 1)
        self.assertEqual(Color.GREEN.value, 2)
        self.assertEqual(Color.BLUE.value, 4)
        self.assertEqual(Color.ALL.value, 7)
        self.assertEqual(str(Color.BLUE), 'blue')
        kundi Color(StrMixin, AllMixin, Flag):
            RED = auto()
            GREEN = auto()
            BLUE = auto()
        self.assertEqual(Color.RED.value, 1)
        self.assertEqual(Color.GREEN.value, 2)
        self.assertEqual(Color.BLUE.value, 4)
        self.assertEqual(Color.ALL.value, 7)
        self.assertEqual(str(Color.BLUE), 'blue')

    @support.reap_threads
    eleza test_unique_composite(self):
        # override __eq__ to be identity only
        kundi TestFlag(Flag):
            one = auto()
            two = auto()
            three = auto()
            four = auto()
            five = auto()
            six = auto()
            seven = auto()
            eight = auto()
            eleza __eq__(self, other):
                rudisha self ni other
            eleza __hash__(self):
                rudisha hash(self._value_)
        # have multiple threads competing to complete the composite members
        seen = set()
        failed = Uongo
        eleza cycle_enum():
            nonlocal failed
            jaribu:
                kila i kwenye range(256):
                    seen.add(TestFlag(i))
            tatizo Exception:
                failed = Kweli
        threads = [
                threading.Thread(target=cycle_enum)
                kila _ kwenye range(8)
                ]
        ukijumuisha support.start_threads(threads):
            pita
        # check that only 248 members were created
        self.assertUongo(
                failed,
                'at least one thread failed wakati creating composite members')
        self.assertEqual(256, len(seen), 'too many composite members created')


kundi TestIntFlag(unittest.TestCase):
    """Tests of the IntFlags."""

    kundi Perm(IntFlag):
        X = 1 << 0
        W = 1 << 1
        R = 1 << 2

    kundi Open(IntFlag):
        RO = 0
        WO = 1
        RW = 2
        AC = 3
        CE = 1<<19

    kundi Color(IntFlag):
        BLACK = 0
        RED = 1
        GREEN = 2
        BLUE = 4
        PURPLE = RED|BLUE

    eleza test_type(self):
        Perm = self.Perm
        Open = self.Open
        kila f kwenye Perm:
            self.assertKweli(isinstance(f, Perm))
            self.assertEqual(f, f.value)
        self.assertKweli(isinstance(Perm.W | Perm.X, Perm))
        self.assertEqual(Perm.W | Perm.X, 3)
        kila f kwenye Open:
            self.assertKweli(isinstance(f, Open))
            self.assertEqual(f, f.value)
        self.assertKweli(isinstance(Open.WO | Open.RW, Open))
        self.assertEqual(Open.WO | Open.RW, 3)


    eleza test_str(self):
        Perm = self.Perm
        self.assertEqual(str(Perm.R), 'Perm.R')
        self.assertEqual(str(Perm.W), 'Perm.W')
        self.assertEqual(str(Perm.X), 'Perm.X')
        self.assertEqual(str(Perm.R | Perm.W), 'Perm.R|W')
        self.assertEqual(str(Perm.R | Perm.W | Perm.X), 'Perm.R|W|X')
        self.assertEqual(str(Perm.R | 8), 'Perm.8|R')
        self.assertEqual(str(Perm(0)), 'Perm.0')
        self.assertEqual(str(Perm(8)), 'Perm.8')
        self.assertEqual(str(~Perm.R), 'Perm.W|X')
        self.assertEqual(str(~Perm.W), 'Perm.R|X')
        self.assertEqual(str(~Perm.X), 'Perm.R|W')
        self.assertEqual(str(~(Perm.R | Perm.W)), 'Perm.X')
        self.assertEqual(str(~(Perm.R | Perm.W | Perm.X)), 'Perm.-8')
        self.assertEqual(str(~(Perm.R | 8)), 'Perm.W|X')
        self.assertEqual(str(Perm(~0)), 'Perm.R|W|X')
        self.assertEqual(str(Perm(~8)), 'Perm.R|W|X')

        Open = self.Open
        self.assertEqual(str(Open.RO), 'Open.RO')
        self.assertEqual(str(Open.WO), 'Open.WO')
        self.assertEqual(str(Open.AC), 'Open.AC')
        self.assertEqual(str(Open.RO | Open.CE), 'Open.CE')
        self.assertEqual(str(Open.WO | Open.CE), 'Open.CE|WO')
        self.assertEqual(str(Open(4)), 'Open.4')
        self.assertEqual(str(~Open.RO), 'Open.CE|AC|RW|WO')
        self.assertEqual(str(~Open.WO), 'Open.CE|RW')
        self.assertEqual(str(~Open.AC), 'Open.CE')
        self.assertEqual(str(~(Open.RO | Open.CE)), 'Open.AC|RW|WO')
        self.assertEqual(str(~(Open.WO | Open.CE)), 'Open.RW')
        self.assertEqual(str(Open(~4)), 'Open.CE|AC|RW|WO')

    eleza test_repr(self):
        Perm = self.Perm
        self.assertEqual(repr(Perm.R), '<Perm.R: 4>')
        self.assertEqual(repr(Perm.W), '<Perm.W: 2>')
        self.assertEqual(repr(Perm.X), '<Perm.X: 1>')
        self.assertEqual(repr(Perm.R | Perm.W), '<Perm.R|W: 6>')
        self.assertEqual(repr(Perm.R | Perm.W | Perm.X), '<Perm.R|W|X: 7>')
        self.assertEqual(repr(Perm.R | 8), '<Perm.8|R: 12>')
        self.assertEqual(repr(Perm(0)), '<Perm.0: 0>')
        self.assertEqual(repr(Perm(8)), '<Perm.8: 8>')
        self.assertEqual(repr(~Perm.R), '<Perm.W|X: -5>')
        self.assertEqual(repr(~Perm.W), '<Perm.R|X: -3>')
        self.assertEqual(repr(~Perm.X), '<Perm.R|W: -2>')
        self.assertEqual(repr(~(Perm.R | Perm.W)), '<Perm.X: -7>')
        self.assertEqual(repr(~(Perm.R | Perm.W | Perm.X)), '<Perm.-8: -8>')
        self.assertEqual(repr(~(Perm.R | 8)), '<Perm.W|X: -13>')
        self.assertEqual(repr(Perm(~0)), '<Perm.R|W|X: -1>')
        self.assertEqual(repr(Perm(~8)), '<Perm.R|W|X: -9>')

        Open = self.Open
        self.assertEqual(repr(Open.RO), '<Open.RO: 0>')
        self.assertEqual(repr(Open.WO), '<Open.WO: 1>')
        self.assertEqual(repr(Open.AC), '<Open.AC: 3>')
        self.assertEqual(repr(Open.RO | Open.CE), '<Open.CE: 524288>')
        self.assertEqual(repr(Open.WO | Open.CE), '<Open.CE|WO: 524289>')
        self.assertEqual(repr(Open(4)), '<Open.4: 4>')
        self.assertEqual(repr(~Open.RO), '<Open.CE|AC|RW|WO: -1>')
        self.assertEqual(repr(~Open.WO), '<Open.CE|RW: -2>')
        self.assertEqual(repr(~Open.AC), '<Open.CE: -4>')
        self.assertEqual(repr(~(Open.RO | Open.CE)), '<Open.AC|RW|WO: -524289>')
        self.assertEqual(repr(~(Open.WO | Open.CE)), '<Open.RW: -524290>')
        self.assertEqual(repr(Open(~4)), '<Open.CE|AC|RW|WO: -5>')

    eleza test_or(self):
        Perm = self.Perm
        kila i kwenye Perm:
            kila j kwenye Perm:
                self.assertEqual(i | j, i.value | j.value)
                self.assertEqual((i | j).value, i.value | j.value)
                self.assertIs(type(i | j), Perm)
            kila j kwenye range(8):
                self.assertEqual(i | j, i.value | j)
                self.assertEqual((i | j).value, i.value | j)
                self.assertIs(type(i | j), Perm)
                self.assertEqual(j | i, j | i.value)
                self.assertEqual((j | i).value, j | i.value)
                self.assertIs(type(j | i), Perm)
        kila i kwenye Perm:
            self.assertIs(i | i, i)
            self.assertIs(i | 0, i)
            self.assertIs(0 | i, i)
        Open = self.Open
        self.assertIs(Open.RO | Open.CE, Open.CE)

    eleza test_and(self):
        Perm = self.Perm
        RW = Perm.R | Perm.W
        RX = Perm.R | Perm.X
        WX = Perm.W | Perm.X
        RWX = Perm.R | Perm.W | Perm.X
        values = list(Perm) + [RW, RX, WX, RWX, Perm(0)]
        kila i kwenye values:
            kila j kwenye values:
                self.assertEqual(i & j, i.value & j.value, 'i ni %r, j ni %r' % (i, j))
                self.assertEqual((i & j).value, i.value & j.value, 'i ni %r, j ni %r' % (i, j))
                self.assertIs(type(i & j), Perm, 'i ni %r, j ni %r' % (i, j))
            kila j kwenye range(8):
                self.assertEqual(i & j, i.value & j)
                self.assertEqual((i & j).value, i.value & j)
                self.assertIs(type(i & j), Perm)
                self.assertEqual(j & i, j & i.value)
                self.assertEqual((j & i).value, j & i.value)
                self.assertIs(type(j & i), Perm)
        kila i kwenye Perm:
            self.assertIs(i & i, i)
            self.assertIs(i & 7, i)
            self.assertIs(7 & i, i)
        Open = self.Open
        self.assertIs(Open.RO & Open.CE, Open.RO)

    eleza test_xor(self):
        Perm = self.Perm
        kila i kwenye Perm:
            kila j kwenye Perm:
                self.assertEqual(i ^ j, i.value ^ j.value)
                self.assertEqual((i ^ j).value, i.value ^ j.value)
                self.assertIs(type(i ^ j), Perm)
            kila j kwenye range(8):
                self.assertEqual(i ^ j, i.value ^ j)
                self.assertEqual((i ^ j).value, i.value ^ j)
                self.assertIs(type(i ^ j), Perm)
                self.assertEqual(j ^ i, j ^ i.value)
                self.assertEqual((j ^ i).value, j ^ i.value)
                self.assertIs(type(j ^ i), Perm)
        kila i kwenye Perm:
            self.assertIs(i ^ 0, i)
            self.assertIs(0 ^ i, i)
        Open = self.Open
        self.assertIs(Open.RO ^ Open.CE, Open.CE)
        self.assertIs(Open.CE ^ Open.CE, Open.RO)

    eleza test_invert(self):
        Perm = self.Perm
        RW = Perm.R | Perm.W
        RX = Perm.R | Perm.X
        WX = Perm.W | Perm.X
        RWX = Perm.R | Perm.W | Perm.X
        values = list(Perm) + [RW, RX, WX, RWX, Perm(0)]
        kila i kwenye values:
            self.assertEqual(~i, ~i.value)
            self.assertEqual((~i).value, ~i.value)
            self.assertIs(type(~i), Perm)
            self.assertEqual(~~i, i)
        kila i kwenye Perm:
            self.assertIs(~~i, i)
        Open = self.Open
        self.assertIs(Open.WO & ~Open.WO, Open.RO)
        self.assertIs((Open.WO|Open.CE) & ~Open.WO, Open.CE)

    eleza test_programatic_function_string(self):
        Perm = IntFlag('Perm', 'R W X')
        lst = list(Perm)
        self.assertEqual(len(lst), len(Perm))
        self.assertEqual(len(Perm), 3, Perm)
        self.assertEqual(lst, [Perm.R, Perm.W, Perm.X])
        kila i, n kwenye enumerate('R W X'.split()):
            v = 1<<i
            e = Perm(v)
            self.assertEqual(e.value, v)
            self.assertEqual(type(e.value), int)
            self.assertEqual(e, v)
            self.assertEqual(e.name, n)
            self.assertIn(e, Perm)
            self.assertIs(type(e), Perm)

    eleza test_programatic_function_string_with_start(self):
        Perm = IntFlag('Perm', 'R W X', start=8)
        lst = list(Perm)
        self.assertEqual(len(lst), len(Perm))
        self.assertEqual(len(Perm), 3, Perm)
        self.assertEqual(lst, [Perm.R, Perm.W, Perm.X])
        kila i, n kwenye enumerate('R W X'.split()):
            v = 8<<i
            e = Perm(v)
            self.assertEqual(e.value, v)
            self.assertEqual(type(e.value), int)
            self.assertEqual(e, v)
            self.assertEqual(e.name, n)
            self.assertIn(e, Perm)
            self.assertIs(type(e), Perm)

    eleza test_programatic_function_string_list(self):
        Perm = IntFlag('Perm', ['R', 'W', 'X'])
        lst = list(Perm)
        self.assertEqual(len(lst), len(Perm))
        self.assertEqual(len(Perm), 3, Perm)
        self.assertEqual(lst, [Perm.R, Perm.W, Perm.X])
        kila i, n kwenye enumerate('R W X'.split()):
            v = 1<<i
            e = Perm(v)
            self.assertEqual(e.value, v)
            self.assertEqual(type(e.value), int)
            self.assertEqual(e, v)
            self.assertEqual(e.name, n)
            self.assertIn(e, Perm)
            self.assertIs(type(e), Perm)

    eleza test_programatic_function_iterable(self):
        Perm = IntFlag('Perm', (('R', 2), ('W', 8), ('X', 32)))
        lst = list(Perm)
        self.assertEqual(len(lst), len(Perm))
        self.assertEqual(len(Perm), 3, Perm)
        self.assertEqual(lst, [Perm.R, Perm.W, Perm.X])
        kila i, n kwenye enumerate('R W X'.split()):
            v = 1<<(2*i+1)
            e = Perm(v)
            self.assertEqual(e.value, v)
            self.assertEqual(type(e.value), int)
            self.assertEqual(e, v)
            self.assertEqual(e.name, n)
            self.assertIn(e, Perm)
            self.assertIs(type(e), Perm)

    eleza test_programatic_function_from_dict(self):
        Perm = IntFlag('Perm', OrderedDict((('R', 2), ('W', 8), ('X', 32))))
        lst = list(Perm)
        self.assertEqual(len(lst), len(Perm))
        self.assertEqual(len(Perm), 3, Perm)
        self.assertEqual(lst, [Perm.R, Perm.W, Perm.X])
        kila i, n kwenye enumerate('R W X'.split()):
            v = 1<<(2*i+1)
            e = Perm(v)
            self.assertEqual(e.value, v)
            self.assertEqual(type(e.value), int)
            self.assertEqual(e, v)
            self.assertEqual(e.name, n)
            self.assertIn(e, Perm)
            self.assertIs(type(e), Perm)


    eleza test_programatic_function_from_empty_list(self):
        Perm = enum.IntFlag('Perm', [])
        lst = list(Perm)
        self.assertEqual(len(lst), len(Perm))
        self.assertEqual(len(Perm), 0, Perm)
        Thing = enum.Enum('Thing', [])
        lst = list(Thing)
        self.assertEqual(len(lst), len(Thing))
        self.assertEqual(len(Thing), 0, Thing)


    eleza test_programatic_function_from_empty_tuple(self):
        Perm = enum.IntFlag('Perm', ())
        lst = list(Perm)
        self.assertEqual(len(lst), len(Perm))
        self.assertEqual(len(Perm), 0, Perm)
        Thing = enum.Enum('Thing', ())
        self.assertEqual(len(lst), len(Thing))
        self.assertEqual(len(Thing), 0, Thing)

    eleza test_contains(self):
        Open = self.Open
        Color = self.Color
        self.assertKweli(Color.GREEN kwenye Color)
        self.assertKweli(Open.RW kwenye Open)
        self.assertUongo(Color.GREEN kwenye Open)
        self.assertUongo(Open.RW kwenye Color)
        ukijumuisha self.assertRaises(TypeError):
            'GREEN' kwenye Color
        ukijumuisha self.assertRaises(TypeError):
            'RW' kwenye Open
        ukijumuisha self.assertRaises(TypeError):
            2 kwenye Color
        ukijumuisha self.assertRaises(TypeError):
            2 kwenye Open

    eleza test_member_contains(self):
        Perm = self.Perm
        R, W, X = Perm
        RW = R | W
        RX = R | X
        WX = W | X
        RWX = R | W | X
        self.assertKweli(R kwenye RW)
        self.assertKweli(R kwenye RX)
        self.assertKweli(R kwenye RWX)
        self.assertKweli(W kwenye RW)
        self.assertKweli(W kwenye WX)
        self.assertKweli(W kwenye RWX)
        self.assertKweli(X kwenye RX)
        self.assertKweli(X kwenye WX)
        self.assertKweli(X kwenye RWX)
        self.assertUongo(R kwenye WX)
        self.assertUongo(W kwenye RX)
        self.assertUongo(X kwenye RW)
        ukijumuisha self.assertRaises(TypeError):
            self.assertUongo('test' kwenye RW)

    eleza test_bool(self):
        Perm = self.Perm
        kila f kwenye Perm:
            self.assertKweli(f)
        Open = self.Open
        kila f kwenye Open:
            self.assertEqual(bool(f.value), bool(f))

    eleza test_multiple_mixin(self):
        kundi AllMixin:
            @classproperty
            eleza ALL(cls):
                members = list(cls)
                all_value = Tupu
                ikiwa members:
                    all_value = members[0]
                    kila member kwenye members[1:]:
                        all_value |= member
                cls.ALL = all_value
                rudisha all_value
        kundi StrMixin:
            eleza __str__(self):
                rudisha self._name_.lower()
        kundi Color(AllMixin, IntFlag):
            RED = auto()
            GREEN = auto()
            BLUE = auto()
        self.assertEqual(Color.RED.value, 1)
        self.assertEqual(Color.GREEN.value, 2)
        self.assertEqual(Color.BLUE.value, 4)
        self.assertEqual(Color.ALL.value, 7)
        self.assertEqual(str(Color.BLUE), 'Color.BLUE')
        kundi Color(AllMixin, StrMixin, IntFlag):
            RED = auto()
            GREEN = auto()
            BLUE = auto()
        self.assertEqual(Color.RED.value, 1)
        self.assertEqual(Color.GREEN.value, 2)
        self.assertEqual(Color.BLUE.value, 4)
        self.assertEqual(Color.ALL.value, 7)
        self.assertEqual(str(Color.BLUE), 'blue')
        kundi Color(StrMixin, AllMixin, IntFlag):
            RED = auto()
            GREEN = auto()
            BLUE = auto()
        self.assertEqual(Color.RED.value, 1)
        self.assertEqual(Color.GREEN.value, 2)
        self.assertEqual(Color.BLUE.value, 4)
        self.assertEqual(Color.ALL.value, 7)
        self.assertEqual(str(Color.BLUE), 'blue')

    @support.reap_threads
    eleza test_unique_composite(self):
        # override __eq__ to be identity only
        kundi TestFlag(IntFlag):
            one = auto()
            two = auto()
            three = auto()
            four = auto()
            five = auto()
            six = auto()
            seven = auto()
            eight = auto()
            eleza __eq__(self, other):
                rudisha self ni other
            eleza __hash__(self):
                rudisha hash(self._value_)
        # have multiple threads competing to complete the composite members
        seen = set()
        failed = Uongo
        eleza cycle_enum():
            nonlocal failed
            jaribu:
                kila i kwenye range(256):
                    seen.add(TestFlag(i))
            tatizo Exception:
                failed = Kweli
        threads = [
                threading.Thread(target=cycle_enum)
                kila _ kwenye range(8)
                ]
        ukijumuisha support.start_threads(threads):
            pita
        # check that only 248 members were created
        self.assertUongo(
                failed,
                'at least one thread failed wakati creating composite members')
        self.assertEqual(256, len(seen), 'too many composite members created')


kundi TestEmptyAndNonLatinStrings(unittest.TestCase):

    eleza test_empty_string(self):
        ukijumuisha self.assertRaises(ValueError):
            empty_abc = Enum('empty_abc', ('', 'B', 'C'))

    eleza test_non_latin_character_string(self):
        greek_abc = Enum('greek_abc', ('\u03B1', 'B', 'C'))
        item = getattr(greek_abc, '\u03B1')
        self.assertEqual(item.value, 1)

    eleza test_non_latin_number_string(self):
        hebrew_123 = Enum('hebrew_123', ('\u05D0', '2', '3'))
        item = getattr(hebrew_123, '\u05D0')
        self.assertEqual(item.value, 1)


kundi TestUnique(unittest.TestCase):

    eleza test_unique_clean(self):
        @unique
        kundi Clean(Enum):
            one = 1
            two = 'dos'
            tres = 4.0
        @unique
        kundi Cleaner(IntEnum):
            single = 1
            double = 2
            triple = 3

    eleza test_unique_dirty(self):
        ukijumuisha self.assertRaisesRegex(ValueError, 'tres.*one'):
            @unique
            kundi Dirty(Enum):
                one = 1
                two = 'dos'
                tres = 1
        ukijumuisha self.assertRaisesRegex(
                ValueError,
                'double.*single.*turkey.*triple',
                ):
            @unique
            kundi Dirtier(IntEnum):
                single = 1
                double = 1
                triple = 3
                turkey = 3

    eleza test_unique_with_name(self):
        @unique
        kundi Silly(Enum):
            one = 1
            two = 'dos'
            name = 3
        @unique
        kundi Sillier(IntEnum):
            single = 1
            name = 2
            triple = 3
            value = 4



expected_help_output_with_docs = """\
Help on kundi Color kwenye module %s:

kundi Color(enum.Enum)
 |  Color(value, names=Tupu, *, module=Tupu, qualname=Tupu, type=Tupu, start=1)
 |\x20\x20
 |  An enumeration.
 |\x20\x20
 |  Method resolution order:
 |      Color
 |      enum.Enum
 |      builtins.object
 |\x20\x20
 |  Data na other attributes defined here:
 |\x20\x20
 |  blue = <Color.blue: 3>
 |\x20\x20
 |  green = <Color.green: 2>
 |\x20\x20
 |  red = <Color.red: 1>
 |\x20\x20
 |  ----------------------------------------------------------------------
 |  Data descriptors inherited kutoka enum.Enum:
 |\x20\x20
 |  name
 |      The name of the Enum member.
 |\x20\x20
 |  value
 |      The value of the Enum member.
 |\x20\x20
 |  ----------------------------------------------------------------------
 |  Readonly properties inherited kutoka enum.EnumMeta:
 |\x20\x20
 |  __members__
 |      Returns a mapping of member name->value.
 |\x20\x20\x20\x20\x20\x20
 |      This mapping lists all enum members, including aliases. Note that this
 |      ni a read-only view of the internal mapping."""

expected_help_output_without_docs = """\
Help on kundi Color kwenye module %s:

kundi Color(enum.Enum)
 |  Color(value, names=Tupu, *, module=Tupu, qualname=Tupu, type=Tupu, start=1)
 |\x20\x20
 |  Method resolution order:
 |      Color
 |      enum.Enum
 |      builtins.object
 |\x20\x20
 |  Data na other attributes defined here:
 |\x20\x20
 |  blue = <Color.blue: 3>
 |\x20\x20
 |  green = <Color.green: 2>
 |\x20\x20
 |  red = <Color.red: 1>
 |\x20\x20
 |  ----------------------------------------------------------------------
 |  Data descriptors inherited kutoka enum.Enum:
 |\x20\x20
 |  name
 |\x20\x20
 |  value
 |\x20\x20
 |  ----------------------------------------------------------------------
 |  Data descriptors inherited kutoka enum.EnumMeta:
 |\x20\x20
 |  __members__"""

kundi TestStdLib(unittest.TestCase):

    maxDiff = Tupu

    kundi Color(Enum):
        red = 1
        green = 2
        blue = 3

    eleza test_pydoc(self):
        # indirectly test __objclass__
        ikiwa StrEnum.__doc__ ni Tupu:
            expected_text = expected_help_output_without_docs % __name__
        isipokua:
            expected_text = expected_help_output_with_docs % __name__
        output = StringIO()
        helper = pydoc.Helper(output=output)
        helper(self.Color)
        result = output.getvalue().strip()
        self.assertEqual(result, expected_text)

    eleza test_inspect_getmembers(self):
        values = dict((
                ('__class__', EnumMeta),
                ('__doc__', 'An enumeration.'),
                ('__members__', self.Color.__members__),
                ('__module__', __name__),
                ('blue', self.Color.blue),
                ('green', self.Color.green),
                ('name', Enum.__dict__['name']),
                ('red', self.Color.red),
                ('value', Enum.__dict__['value']),
                ))
        result = dict(inspect.getmembers(self.Color))
        self.assertEqual(values.keys(), result.keys())
        failed = Uongo
        kila k kwenye values.keys():
            ikiwa result[k] != values[k]:
                andika()
                andika('\n%s\n     key: %s\n  result: %s\nexpected: %s\n%s\n' %
                        ('=' * 75, k, result[k], values[k], '=' * 75), sep='')
                failed = Kweli
        ikiwa failed:
            self.fail("result does sio equal expected, see print above")

    eleza test_inspect_classify_class_attrs(self):
        # indirectly test __objclass__
        kutoka inspect agiza Attribute
        values = [
                Attribute(name='__class__', kind='data',
                    defining_class=object, object=EnumMeta),
                Attribute(name='__doc__', kind='data',
                    defining_class=self.Color, object='An enumeration.'),
                Attribute(name='__members__', kind='property',
                    defining_class=EnumMeta, object=EnumMeta.__members__),
                Attribute(name='__module__', kind='data',
                    defining_class=self.Color, object=__name__),
                Attribute(name='blue', kind='data',
                    defining_class=self.Color, object=self.Color.blue),
                Attribute(name='green', kind='data',
                    defining_class=self.Color, object=self.Color.green),
                Attribute(name='red', kind='data',
                    defining_class=self.Color, object=self.Color.red),
                Attribute(name='name', kind='data',
                    defining_class=Enum, object=Enum.__dict__['name']),
                Attribute(name='value', kind='data',
                    defining_class=Enum, object=Enum.__dict__['value']),
                ]
        values.sort(key=lambda item: item.name)
        result = list(inspect.classify_class_attrs(self.Color))
        result.sort(key=lambda item: item.name)
        failed = Uongo
        kila v, r kwenye zip(values, result):
            ikiwa r != v:
                andika('\n%s\n%s\n%s\n%s\n' % ('=' * 75, r, v, '=' * 75), sep='')
                failed = Kweli
        ikiwa failed:
            self.fail("result does sio equal expected, see print above")


kundi MiscTestCase(unittest.TestCase):
    eleza test__all__(self):
        support.check__all__(self, enum)


# These are unordered here on purpose to ensure that declaration order
# makes no difference.
CONVERT_TEST_NAME_D = 5
CONVERT_TEST_NAME_C = 5
CONVERT_TEST_NAME_B = 5
CONVERT_TEST_NAME_A = 5  # This one should sort first.
CONVERT_TEST_NAME_E = 5
CONVERT_TEST_NAME_F = 5

kundi TestIntEnumConvert(unittest.TestCase):
    eleza test_convert_value_lookup_priority(self):
        test_type = enum.IntEnum._convert_(
                'UnittestConvert',
                ('test.test_enum', '__main__')[__name__=='__main__'],
                filter=lambda x: x.startswith('CONVERT_TEST_'))
        # We don't want the reverse lookup value to vary when there are
        # multiple possible names kila a given value.  It should always
        # report the first lexigraphical name kwenye that case.
        self.assertEqual(test_type(5).name, 'CONVERT_TEST_NAME_A')

    eleza test_convert(self):
        test_type = enum.IntEnum._convert_(
                'UnittestConvert',
                ('test.test_enum', '__main__')[__name__=='__main__'],
                filter=lambda x: x.startswith('CONVERT_TEST_'))
        # Ensure that test_type has all of the desired names na values.
        self.assertEqual(test_type.CONVERT_TEST_NAME_F,
                         test_type.CONVERT_TEST_NAME_A)
        self.assertEqual(test_type.CONVERT_TEST_NAME_B, 5)
        self.assertEqual(test_type.CONVERT_TEST_NAME_C, 5)
        self.assertEqual(test_type.CONVERT_TEST_NAME_D, 5)
        self.assertEqual(test_type.CONVERT_TEST_NAME_E, 5)
        # Ensure that test_type only picked up names matching the filter.
        self.assertEqual([name kila name kwenye dir(test_type)
                          ikiwa name[0:2] haiko kwenye ('CO', '__')],
                         [], msg='Names other than CONVERT_TEST_* found.')

    @unittest.skipUnless(sys.version_info[:2] == (3, 8),
                         '_convert was deprecated kwenye 3.8')
    eleza test_convert_warn(self):
        ukijumuisha self.assertWarns(DeprecationWarning):
            enum.IntEnum._convert(
                'UnittestConvert',
                ('test.test_enum', '__main__')[__name__=='__main__'],
                filter=lambda x: x.startswith('CONVERT_TEST_'))

    @unittest.skipUnless(sys.version_info >= (3, 9),
                         '_convert was removed kwenye 3.9')
    eleza test_convert_raise(self):
        ukijumuisha self.assertRaises(AttributeError):
            enum.IntEnum._convert(
                'UnittestConvert',
                ('test.test_enum', '__main__')[__name__=='__main__'],
                filter=lambda x: x.startswith('CONVERT_TEST_'))


ikiwa __name__ == '__main__':
    unittest.main()
