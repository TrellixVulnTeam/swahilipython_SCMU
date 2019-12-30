
# Various microbenchmarks comparing unicode na byte string performance
# Please keep this file both 2.x na 3.x compatible!

agiza timeit
agiza itertools
agiza operator
agiza re
agiza sys
agiza datetime
agiza optparse

VERSION = '2.0'

eleza p(*args):
    sys.stdout.write(' '.join(str(s) kila s kwenye args) + '\n')

ikiwa sys.version_info >= (3,):
    BYTES = bytes_from_str = lambda x: x.encode('ascii')
    UNICODE = unicode_from_str = lambda x: x
isipokua:
    BYTES = bytes_from_str = lambda x: x
    UNICODE = unicode_from_str = lambda x: x.decode('ascii')

kundi UnsupportedType(TypeError):
    pita


p('stringbench v%s' % VERSION)
p(sys.version)
p(datetime.datetime.now())

REPEAT = 1
REPEAT = 3
#REPEAT = 7

ikiwa __name__ != "__main__":
    ashiria SystemExit("Must run kama main program")

parser = optparse.OptionParser()
parser.add_option("-R", "--skip-re", dest="skip_re",
                  action="store_true",
                  help="skip regular expression tests")
parser.add_option("-8", "--8-bit", dest="bytes_only",
                  action="store_true",
                  help="only do 8-bit string benchmarks")
parser.add_option("-u", "--unicode", dest="unicode_only",
                  action="store_true",
                  help="only do Unicode string benchmarks")


_RANGE_1000 = list(range(1000))
_RANGE_100 = list(range(100))
_RANGE_10 = list(range(10))

dups = {}
eleza bench(s, group, repeat_count):
    eleza blah(f):
        ikiwa f.__name__ kwenye dups:
            ashiria AssertionError("Multiple functions ukijumuisha same name: %r" %
                                 (f.__name__,))
        dups[f.__name__] = 1
        f.comment = s
        f.is_bench = Kweli
        f.group = group
        f.repeat_count = repeat_count
        rudisha f
    rudisha blah

eleza uses_re(f):
    f.uses_re = Kweli

####### 'in' comparisons

@bench('"A" kwenye "A"*1000', "early match, single character", 1000)
eleza in_test_quick_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("A")
    kila x kwenye _RANGE_1000:
        s2 kwenye s1

@bench('"B" kwenye "A"*1000', "no match, single character", 1000)
eleza in_test_no_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("B")
    kila x kwenye _RANGE_1000:
        s2 kwenye s1


@bench('"AB" kwenye "AB"*1000', "early match, two characters", 1000)
eleza in_test_quick_match_two_characters(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("AB")
    kila x kwenye _RANGE_1000:
        s2 kwenye s1

@bench('"BC" kwenye "AB"*1000', "no match, two characters", 1000)
eleza in_test_no_match_two_character(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("BC")
    kila x kwenye _RANGE_1000:
        s2 kwenye s1

@bench('"BC" kwenye ("AB"*300+"C")', "late match, two characters", 1000)
eleza in_test_slow_match_two_characters(STR):
    s1 = STR("AB" * 300+"C")
    s2 = STR("BC")
    kila x kwenye _RANGE_1000:
        s2 kwenye s1

@bench('s="ABC"*33; (s+"E") kwenye ((s+"D")*300+s+"E")',
       "late match, 100 characters", 100)
eleza in_test_slow_match_100_characters(STR):
    m = STR("ABC"*33)
    d = STR("D")
    e = STR("E")
    s1 = (m+d)*300 + m+e
    s2 = m+e
    kila x kwenye _RANGE_100:
        s2 kwenye s1

# Try ukijumuisha regex
@uses_re
@bench('s="ABC"*33; re.compile(s+"D").search((s+"D")*300+s+"E")',
       "late match, 100 characters", 100)
eleza re_test_slow_match_100_characters(STR):
    m = STR("ABC"*33)
    d = STR("D")
    e = STR("E")
    s1 = (m+d)*300 + m+e
    s2 = m+e
    pat = re.compile(s2)
    search = pat.search
    kila x kwenye _RANGE_100:
        search(s1)


#### same tests kama 'in' but use 'find'

@bench('("A"*1000).find("A")', "early match, single character", 1000)
eleza find_test_quick_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("A")
    s1_find = s1.find
    kila x kwenye _RANGE_1000:
        s1_find(s2)

@bench('("A"*1000).find("B")', "no match, single character", 1000)
eleza find_test_no_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("B")
    s1_find = s1.find
    kila x kwenye _RANGE_1000:
        s1_find(s2)


@bench('("AB"*1000).find("AB")', "early match, two characters", 1000)
eleza find_test_quick_match_two_characters(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("AB")
    s1_find = s1.find
    kila x kwenye _RANGE_1000:
        s1_find(s2)

@bench('("AB"*1000).find("BC")', "no match, two characters", 1000)
eleza find_test_no_match_two_character(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("BC")
    s1_find = s1.find
    kila x kwenye _RANGE_1000:
        s1_find(s2)

@bench('("AB"*1000).find("CA")', "no match, two characters", 1000)
eleza find_test_no_match_two_character_bis(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("CA")
    s1_find = s1.find
    kila x kwenye _RANGE_1000:
        s1_find(s2)

@bench('("AB"*300+"C").find("BC")', "late match, two characters", 1000)
eleza find_test_slow_match_two_characters(STR):
    s1 = STR("AB" * 300+"C")
    s2 = STR("BC")
    s1_find = s1.find
    kila x kwenye _RANGE_1000:
        s1_find(s2)

@bench('("AB"*300+"CA").find("CA")', "late match, two characters", 1000)
eleza find_test_slow_match_two_characters_bis(STR):
    s1 = STR("AB" * 300+"CA")
    s2 = STR("CA")
    s1_find = s1.find
    kila x kwenye _RANGE_1000:
        s1_find(s2)

@bench('s="ABC"*33; ((s+"D")*500+s+"E").find(s+"E")',
       "late match, 100 characters", 100)
eleza find_test_slow_match_100_characters(STR):
    m = STR("ABC"*33)
    d = STR("D")
    e = STR("E")
    s1 = (m+d)*500 + m+e
    s2 = m+e
    s1_find = s1.find
    kila x kwenye _RANGE_100:
        s1_find(s2)

@bench('s="ABC"*33; ((s+"D")*500+"E"+s).find("E"+s)',
       "late match, 100 characters", 100)
eleza find_test_slow_match_100_characters_bis(STR):
    m = STR("ABC"*33)
    d = STR("D")
    e = STR("E")
    s1 = (m+d)*500 + e+m
    s2 = e+m
    s1_find = s1.find
    kila x kwenye _RANGE_100:
        s1_find(s2)


#### Same tests kila 'rfind'

@bench('("A"*1000).rfind("A")', "early match, single character", 1000)
eleza rfind_test_quick_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("A")
    s1_rfind = s1.rfind
    kila x kwenye _RANGE_1000:
        s1_rfind(s2)

@bench('("A"*1000).rfind("B")', "no match, single character", 1000)
eleza rfind_test_no_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("B")
    s1_rfind = s1.rfind
    kila x kwenye _RANGE_1000:
        s1_rfind(s2)


@bench('("AB"*1000).rfind("AB")', "early match, two characters", 1000)
eleza rfind_test_quick_match_two_characters(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("AB")
    s1_rfind = s1.rfind
    kila x kwenye _RANGE_1000:
        s1_rfind(s2)

@bench('("AB"*1000).rfind("BC")', "no match, two characters", 1000)
eleza rfind_test_no_match_two_character(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("BC")
    s1_rfind = s1.rfind
    kila x kwenye _RANGE_1000:
        s1_rfind(s2)

@bench('("AB"*1000).rfind("CA")', "no match, two characters", 1000)
eleza rfind_test_no_match_two_character_bis(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("CA")
    s1_rfind = s1.rfind
    kila x kwenye _RANGE_1000:
        s1_rfind(s2)

@bench('("C"+"AB"*300).rfind("CA")', "late match, two characters", 1000)
eleza rfind_test_slow_match_two_characters(STR):
    s1 = STR("C" + "AB" * 300)
    s2 = STR("CA")
    s1_rfind = s1.rfind
    kila x kwenye _RANGE_1000:
        s1_rfind(s2)

@bench('("BC"+"AB"*300).rfind("BC")', "late match, two characters", 1000)
eleza rfind_test_slow_match_two_characters_bis(STR):
    s1 = STR("BC" + "AB" * 300)
    s2 = STR("BC")
    s1_rfind = s1.rfind
    kila x kwenye _RANGE_1000:
        s1_rfind(s2)

@bench('s="ABC"*33; ("E"+s+("D"+s)*500).rfind("E"+s)',
       "late match, 100 characters", 100)
eleza rfind_test_slow_match_100_characters(STR):
    m = STR("ABC"*33)
    d = STR("D")
    e = STR("E")
    s1 = e+m + (d+m)*500
    s2 = e+m
    s1_rfind = s1.rfind
    kila x kwenye _RANGE_100:
        s1_rfind(s2)

@bench('s="ABC"*33; (s+"E"+("D"+s)*500).rfind(s+"E")',
       "late match, 100 characters", 100)
eleza rfind_test_slow_match_100_characters_bis(STR):
    m = STR("ABC"*33)
    d = STR("D")
    e = STR("E")
    s1 = m+e + (d+m)*500
    s2 = m+e
    s1_rfind = s1.rfind
    kila x kwenye _RANGE_100:
        s1_rfind(s2)


#### Now ukijumuisha index.
# Skip the ones which fail because that would include exception overhead.

@bench('("A"*1000).index("A")', "early match, single character", 1000)
eleza index_test_quick_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("A")
    s1_index = s1.index
    kila x kwenye _RANGE_1000:
        s1_index(s2)

@bench('("AB"*1000).index("AB")', "early match, two characters", 1000)
eleza index_test_quick_match_two_characters(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("AB")
    s1_index = s1.index
    kila x kwenye _RANGE_1000:
        s1_index(s2)

@bench('("AB"*300+"C").index("BC")', "late match, two characters", 1000)
eleza index_test_slow_match_two_characters(STR):
    s1 = STR("AB" * 300+"C")
    s2 = STR("BC")
    s1_index = s1.index
    kila x kwenye _RANGE_1000:
        s1_index(s2)

@bench('s="ABC"*33; ((s+"D")*500+s+"E").index(s+"E")',
       "late match, 100 characters", 100)
eleza index_test_slow_match_100_characters(STR):
    m = STR("ABC"*33)
    d = STR("D")
    e = STR("E")
    s1 = (m+d)*500 + m+e
    s2 = m+e
    s1_index = s1.index
    kila x kwenye _RANGE_100:
        s1_index(s2)


#### Same kila rindex

@bench('("A"*1000).rindex("A")', "early match, single character", 1000)
eleza rindex_test_quick_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("A")
    s1_rindex = s1.rindex
    kila x kwenye _RANGE_1000:
        s1_rindex(s2)

@bench('("AB"*1000).rindex("AB")', "early match, two characters", 1000)
eleza rindex_test_quick_match_two_characters(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("AB")
    s1_rindex = s1.rindex
    kila x kwenye _RANGE_1000:
        s1_rindex(s2)

@bench('("C"+"AB"*300).rindex("CA")', "late match, two characters", 1000)
eleza rindex_test_slow_match_two_characters(STR):
    s1 = STR("C" + "AB" * 300)
    s2 = STR("CA")
    s1_rindex = s1.rindex
    kila x kwenye _RANGE_1000:
        s1_rindex(s2)

@bench('s="ABC"*33; ("E"+s+("D"+s)*500).rindex("E"+s)',
       "late match, 100 characters", 100)
eleza rindex_test_slow_match_100_characters(STR):
    m = STR("ABC"*33)
    d = STR("D")
    e = STR("E")
    s1 = e + m + (d+m)*500
    s2 = e + m
    s1_rindex = s1.rindex
    kila x kwenye _RANGE_100:
        s1_rindex(s2)


#### Same kila partition

@bench('("A"*1000).partition("A")', "early match, single character", 1000)
eleza partition_test_quick_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("A")
    s1_partition = s1.partition
    kila x kwenye _RANGE_1000:
        s1_partition(s2)

@bench('("A"*1000).partition("B")', "no match, single character", 1000)
eleza partition_test_no_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("B")
    s1_partition = s1.partition
    kila x kwenye _RANGE_1000:
        s1_partition(s2)


@bench('("AB"*1000).partition("AB")', "early match, two characters", 1000)
eleza partition_test_quick_match_two_characters(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("AB")
    s1_partition = s1.partition
    kila x kwenye _RANGE_1000:
        s1_partition(s2)

@bench('("AB"*1000).partition("BC")', "no match, two characters", 1000)
eleza partition_test_no_match_two_character(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("BC")
    s1_partition = s1.partition
    kila x kwenye _RANGE_1000:
        s1_partition(s2)

@bench('("AB"*300+"C").partition("BC")', "late match, two characters", 1000)
eleza partition_test_slow_match_two_characters(STR):
    s1 = STR("AB" * 300+"C")
    s2 = STR("BC")
    s1_partition = s1.partition
    kila x kwenye _RANGE_1000:
        s1_partition(s2)

@bench('s="ABC"*33; ((s+"D")*500+s+"E").partition(s+"E")',
       "late match, 100 characters", 100)
eleza partition_test_slow_match_100_characters(STR):
    m = STR("ABC"*33)
    d = STR("D")
    e = STR("E")
    s1 = (m+d)*500 + m+e
    s2 = m+e
    s1_partition = s1.partition
    kila x kwenye _RANGE_100:
        s1_partition(s2)


#### Same kila rpartition

@bench('("A"*1000).rpartition("A")', "early match, single character", 1000)
eleza rpartition_test_quick_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("A")
    s1_rpartition = s1.rpartition
    kila x kwenye _RANGE_1000:
        s1_rpartition(s2)

@bench('("A"*1000).rpartition("B")', "no match, single character", 1000)
eleza rpartition_test_no_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("B")
    s1_rpartition = s1.rpartition
    kila x kwenye _RANGE_1000:
        s1_rpartition(s2)


@bench('("AB"*1000).rpartition("AB")', "early match, two characters", 1000)
eleza rpartition_test_quick_match_two_characters(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("AB")
    s1_rpartition = s1.rpartition
    kila x kwenye _RANGE_1000:
        s1_rpartition(s2)

@bench('("AB"*1000).rpartition("BC")', "no match, two characters", 1000)
eleza rpartition_test_no_match_two_character(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("BC")
    s1_rpartition = s1.rpartition
    kila x kwenye _RANGE_1000:
        s1_rpartition(s2)

@bench('("C"+"AB"*300).rpartition("CA")', "late match, two characters", 1000)
eleza rpartition_test_slow_match_two_characters(STR):
    s1 = STR("C" + "AB" * 300)
    s2 = STR("CA")
    s1_rpartition = s1.rpartition
    kila x kwenye _RANGE_1000:
        s1_rpartition(s2)

@bench('s="ABC"*33; ("E"+s+("D"+s)*500).rpartition("E"+s)',
       "late match, 100 characters", 100)
eleza rpartition_test_slow_match_100_characters(STR):
    m = STR("ABC"*33)
    d = STR("D")
    e = STR("E")
    s1 = e + m + (d+m)*500
    s2 = e + m
    s1_rpartition = s1.rpartition
    kila x kwenye _RANGE_100:
        s1_rpartition(s2)


#### Same kila split(s, 1)

@bench('("A"*1000).split("A", 1)', "early match, single character", 1000)
eleza split_test_quick_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("A")
    s1_split = s1.split
    kila x kwenye _RANGE_1000:
        s1_split(s2, 1)

@bench('("A"*1000).split("B", 1)', "no match, single character", 1000)
eleza split_test_no_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("B")
    s1_split = s1.split
    kila x kwenye _RANGE_1000:
        s1_split(s2, 1)


@bench('("AB"*1000).split("AB", 1)', "early match, two characters", 1000)
eleza split_test_quick_match_two_characters(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("AB")
    s1_split = s1.split
    kila x kwenye _RANGE_1000:
        s1_split(s2, 1)

@bench('("AB"*1000).split("BC", 1)', "no match, two characters", 1000)
eleza split_test_no_match_two_character(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("BC")
    s1_split = s1.split
    kila x kwenye _RANGE_1000:
        s1_split(s2, 1)

@bench('("AB"*300+"C").split("BC", 1)', "late match, two characters", 1000)
eleza split_test_slow_match_two_characters(STR):
    s1 = STR("AB" * 300+"C")
    s2 = STR("BC")
    s1_split = s1.split
    kila x kwenye _RANGE_1000:
        s1_split(s2, 1)

@bench('s="ABC"*33; ((s+"D")*500+s+"E").split(s+"E", 1)',
       "late match, 100 characters", 100)
eleza split_test_slow_match_100_characters(STR):
    m = STR("ABC"*33)
    d = STR("D")
    e = STR("E")
    s1 = (m+d)*500 + m+e
    s2 = m+e
    s1_split = s1.split
    kila x kwenye _RANGE_100:
        s1_split(s2, 1)


#### Same kila rsplit(s, 1)

@bench('("A"*1000).rsplit("A", 1)', "early match, single character", 1000)
eleza rsplit_test_quick_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("A")
    s1_rsplit = s1.rsplit
    kila x kwenye _RANGE_1000:
        s1_rsplit(s2, 1)

@bench('("A"*1000).rsplit("B", 1)', "no match, single character", 1000)
eleza rsplit_test_no_match_single_character(STR):
    s1 = STR("A" * 1000)
    s2 = STR("B")
    s1_rsplit = s1.rsplit
    kila x kwenye _RANGE_1000:
        s1_rsplit(s2, 1)


@bench('("AB"*1000).rsplit("AB", 1)', "early match, two characters", 1000)
eleza rsplit_test_quick_match_two_characters(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("AB")
    s1_rsplit = s1.rsplit
    kila x kwenye _RANGE_1000:
        s1_rsplit(s2, 1)

@bench('("AB"*1000).rsplit("BC", 1)', "no match, two characters", 1000)
eleza rsplit_test_no_match_two_character(STR):
    s1 = STR("AB" * 1000)
    s2 = STR("BC")
    s1_rsplit = s1.rsplit
    kila x kwenye _RANGE_1000:
        s1_rsplit(s2, 1)

@bench('("C"+"AB"*300).rsplit("CA", 1)', "late match, two characters", 1000)
eleza rsplit_test_slow_match_two_characters(STR):
    s1 = STR("C" + "AB" * 300)
    s2 = STR("CA")
    s1_rsplit = s1.rsplit
    kila x kwenye _RANGE_1000:
        s1_rsplit(s2, 1)

@bench('s="ABC"*33; ("E"+s+("D"+s)*500).rsplit("E"+s, 1)',
       "late match, 100 characters", 100)
eleza rsplit_test_slow_match_100_characters(STR):
    m = STR("ABC"*33)
    d = STR("D")
    e = STR("E")
    s1 = e + m + (d+m)*500
    s2 = e + m
    s1_rsplit = s1.rsplit
    kila x kwenye _RANGE_100:
        s1_rsplit(s2, 1)


#### Benchmark the operator-based methods

@bench('"A"*10', "repeat 1 character 10 times", 1000)
eleza repeat_single_10_times(STR):
    s = STR("A")
    kila x kwenye _RANGE_1000:
        s * 10

@bench('"A"*1000', "repeat 1 character 1000 times", 1000)
eleza repeat_single_1000_times(STR):
    s = STR("A")
    kila x kwenye _RANGE_1000:
        s * 1000

@bench('"ABCDE"*10', "repeat 5 characters 10 times", 1000)
eleza repeat_5_10_times(STR):
    s = STR("ABCDE")
    kila x kwenye _RANGE_1000:
        s * 10

@bench('"ABCDE"*1000', "repeat 5 characters 1000 times", 1000)
eleza repeat_5_1000_times(STR):
    s = STR("ABCDE")
    kila x kwenye _RANGE_1000:
        s * 1000

# + kila concat

@bench('"Andrew"+"Dalke"', "concat two strings", 1000)
eleza concat_two_strings(STR):
    s1 = STR("Andrew")
    s2 = STR("Dalke")
    kila x kwenye _RANGE_1000:
        s1+s2

@bench('s1+s2+s3+s4+...+s20', "concat 20 strings of words length 4 to 15",
       1000)
eleza concat_many_strings(STR):
    s1=STR('TIXSGYNREDCVBHJ')
    s2=STR('PUMTLXBZVDO')
    s3=STR('FVZNJ')
    s4=STR('OGDXUW')
    s5=STR('WEIMRNCOYVGHKB')
    s6=STR('FCQTNMXPUZH')
    s7=STR('TICZJYRLBNVUEAK')
    s8=STR('REYB')
    s9=STR('PWUOQ')
    s10=STR('EQHCMKBS')
    s11=STR('AEVDFOH')
    s12=STR('IFHVD')
    s13=STR('JGTCNLXWOHQ')
    s14=STR('ITSKEPYLROZAWXF')
    s15=STR('THEK')
    s16=STR('GHPZFBUYCKMNJIT')
    s17=STR('JMUZ')
    s18=STR('WLZQMTB')
    s19=STR('KPADCBW')
    s20=STR('TNJHZQAGBU')
    kila x kwenye _RANGE_1000:
        (s1 + s2+ s3+ s4+ s5+ s6+ s7+ s8+ s9+s10+
         s11+s12+s13+s14+s15+s16+s17+s18+s19+s20)


#### Benchmark join

eleza get_bytes_yielding_seq(STR, arg):
    ikiwa STR ni BYTES na sys.version_info >= (3,):
        ashiria UnsupportedType
    rudisha STR(arg)

@bench('"A".join("")',
       "join empty string, ukijumuisha 1 character sep", 100)
eleza join_empty_single(STR):
    sep = STR("A")
    s2 = get_bytes_yielding_seq(STR, "")
    sep_join = sep.join
    kila x kwenye _RANGE_100:
        sep_join(s2)

@bench('"ABCDE".join("")',
       "join empty string, ukijumuisha 5 character sep", 100)
eleza join_empty_5(STR):
    sep = STR("ABCDE")
    s2 = get_bytes_yielding_seq(STR, "")
    sep_join = sep.join
    kila x kwenye _RANGE_100:
        sep_join(s2)

@bench('"A".join("ABC..Z")',
       "join string ukijumuisha 26 characters, ukijumuisha 1 character sep", 1000)
eleza join_alphabet_single(STR):
    sep = STR("A")
    s2 = get_bytes_yielding_seq(STR, "ABCDEFGHIJKLMnOPQRSTUVWXYZ")
    sep_join = sep.join
    kila x kwenye _RANGE_1000:
        sep_join(s2)

@bench('"ABCDE".join("ABC..Z")',
       "join string ukijumuisha 26 characters, ukijumuisha 5 character sep", 1000)
eleza join_alphabet_5(STR):
    sep = STR("ABCDE")
    s2 = get_bytes_yielding_seq(STR, "ABCDEFGHIJKLMnOPQRSTUVWXYZ")
    sep_join = sep.join
    kila x kwenye _RANGE_1000:
        sep_join(s2)

@bench('"A".join(list("ABC..Z"))',
       "join list of 26 characters, ukijumuisha 1 character sep", 1000)
eleza join_alphabet_list_single(STR):
    sep = STR("A")
    s2 = [STR(x) kila x kwenye "ABCDEFGHIJKLMnOPQRSTUVWXYZ"]
    sep_join = sep.join
    kila x kwenye _RANGE_1000:
        sep_join(s2)

@bench('"ABCDE".join(list("ABC..Z"))',
       "join list of 26 characters, ukijumuisha 5 character sep", 1000)
eleza join_alphabet_list_five(STR):
    sep = STR("ABCDE")
    s2 = [STR(x) kila x kwenye "ABCDEFGHIJKLMnOPQRSTUVWXYZ"]
    sep_join = sep.join
    kila x kwenye _RANGE_1000:
        sep_join(s2)

@bench('"A".join(["Bob"]*100))',
       "join list of 100 words, ukijumuisha 1 character sep", 1000)
eleza join_100_words_single(STR):
    sep = STR("A")
    s2 = [STR("Bob")]*100
    sep_join = sep.join
    kila x kwenye _RANGE_1000:
        sep_join(s2)

@bench('"ABCDE".join(["Bob"]*100))',
       "join list of 100 words, ukijumuisha 5 character sep", 1000)
eleza join_100_words_5(STR):
    sep = STR("ABCDE")
    s2 = [STR("Bob")]*100
    sep_join = sep.join
    kila x kwenye _RANGE_1000:
        sep_join(s2)

#### split tests

@bench('("Here are some words. "*2).split()', "split whitespace (small)", 1000)
eleza whitespace_split(STR):
    s = STR("Here are some words. "*2)
    s_split = s.split
    kila x kwenye _RANGE_1000:
        s_split()

@bench('("Here are some words. "*2).rsplit()', "split whitespace (small)", 1000)
eleza whitespace_rsplit(STR):
    s = STR("Here are some words. "*2)
    s_rsplit = s.rsplit
    kila x kwenye _RANGE_1000:
        s_rsplit()

@bench('("Here are some words. "*2).split(Tupu, 1)',
       "split 1 whitespace", 1000)
eleza whitespace_split_1(STR):
    s = STR("Here are some words. "*2)
    s_split = s.split
    N = Tupu
    kila x kwenye _RANGE_1000:
        s_split(N, 1)

@bench('("Here are some words. "*2).rsplit(Tupu, 1)',
       "split 1 whitespace", 1000)
eleza whitespace_rsplit_1(STR):
    s = STR("Here are some words. "*2)
    s_rsplit = s.rsplit
    N = Tupu
    kila x kwenye _RANGE_1000:
        s_rsplit(N, 1)

@bench('("Here are some words. "*2).partition(" ")',
       "split 1 whitespace", 1000)
eleza whitespace_partition(STR):
    sep = STR(" ")
    s = STR("Here are some words. "*2)
    s_partition = s.partition
    kila x kwenye _RANGE_1000:
        s_partition(sep)

@bench('("Here are some words. "*2).rpartition(" ")',
       "split 1 whitespace", 1000)
eleza whitespace_rpartition(STR):
    sep = STR(" ")
    s = STR("Here are some words. "*2)
    s_rpartition = s.rpartition
    kila x kwenye _RANGE_1000:
        s_rpartition(sep)

human_text = """\
Python ni a dynamic object-oriented programming language that can be
used kila many kinds of software development. It offers strong support
kila integration ukijumuisha other languages na tools, comes ukijumuisha extensive
standard libraries, na can be learned kwenye a few days. Many Python
programmers report substantial productivity gains na feel the language
encourages the development of higher quality, more maintainable code.

Python runs on Windows, Linux/Unix, Mac OS X, Amiga, Palm
Handhelds, na Nokia mobile phones. Python has also been ported to the
Java na .NET virtual machines.

Python ni distributed under an OSI-approved open source license that
makes it free to use, even kila commercial products.
"""*25
human_text_bytes = bytes_from_str(human_text)
human_text_unicode = unicode_from_str(human_text)
eleza _get_human_text(STR):
    ikiwa STR ni UNICODE:
        rudisha human_text_unicode
    ikiwa STR ni BYTES:
        rudisha human_text_bytes
    ashiria AssertionError

@bench('human_text.split()', "split whitespace (huge)", 10)
eleza whitespace_split_huge(STR):
    s = _get_human_text(STR)
    s_split = s.split
    kila x kwenye _RANGE_10:
        s_split()

@bench('human_text.rsplit()', "split whitespace (huge)", 10)
eleza whitespace_rsplit_huge(STR):
    s = _get_human_text(STR)
    s_rsplit = s.rsplit
    kila x kwenye _RANGE_10:
        s_rsplit()



@bench('"this\\nis\\na\\ntest\\n".split("\\n")', "split newlines", 1000)
eleza newlines_split(STR):
    s = STR("this\nis\na\ntest\n")
    s_split = s.split
    nl = STR("\n")
    kila x kwenye _RANGE_1000:
        s_split(nl)


@bench('"this\\nis\\na\\ntest\\n".rsplit("\\n")', "split newlines", 1000)
eleza newlines_rsplit(STR):
    s = STR("this\nis\na\ntest\n")
    s_rsplit = s.rsplit
    nl = STR("\n")
    kila x kwenye _RANGE_1000:
        s_rsplit(nl)

@bench('"this\\nis\\na\\ntest\\n".splitlines()', "split newlines", 1000)
eleza newlines_splitlines(STR):
    s = STR("this\nis\na\ntest\n")
    s_splitlines = s.splitlines
    kila x kwenye _RANGE_1000:
        s_splitlines()

## split text ukijumuisha 2000 newlines

eleza _make_2000_lines():
    agiza random
    r = random.Random(100)
    chars = list(map(chr, range(32, 128)))
    i = 0
    wakati i < len(chars):
        chars[i] = " "
        i += r.randrange(9)
    s = "".join(chars)
    s = s*4
    words = []
    kila i kwenye range(2000):
        start = r.randrange(96)
        n = r.randint(5, 65)
        words.append(s[start:start+n])
    rudisha "\n".join(words)+"\n"

_text_with_2000_lines = _make_2000_lines()
_text_with_2000_lines_bytes = bytes_from_str(_text_with_2000_lines)
_text_with_2000_lines_unicode = unicode_from_str(_text_with_2000_lines)
eleza _get_2000_lines(STR):
    ikiwa STR ni UNICODE:
        rudisha _text_with_2000_lines_unicode
    ikiwa STR ni BYTES:
        rudisha _text_with_2000_lines_bytes
    ashiria AssertionError


@bench('"...text...".split("\\n")', "split 2000 newlines", 10)
eleza newlines_split_2000(STR):
    s = _get_2000_lines(STR)
    s_split = s.split
    nl = STR("\n")
    kila x kwenye _RANGE_10:
        s_split(nl)

@bench('"...text...".rsplit("\\n")', "split 2000 newlines", 10)
eleza newlines_rsplit_2000(STR):
    s = _get_2000_lines(STR)
    s_rsplit = s.rsplit
    nl = STR("\n")
    kila x kwenye _RANGE_10:
        s_rsplit(nl)

@bench('"...text...".splitlines()', "split 2000 newlines", 10)
eleza newlines_splitlines_2000(STR):
    s = _get_2000_lines(STR)
    s_splitlines = s.splitlines
    kila x kwenye _RANGE_10:
        s_splitlines()


## split text on "--" characters
@bench(
    '"this--is--a--test--of--the--emergency--broadcast--system".split("--")',
    "split on multicharacter separator (small)", 1000)
eleza split_multichar_sep_small(STR):
    s = STR("this--is--a--test--of--the--emergency--broadcast--system")
    s_split = s.split
    pat = STR("--")
    kila x kwenye _RANGE_1000:
        s_split(pat)
@bench(
    '"this--is--a--test--of--the--emergency--broadcast--system".rsplit("--")',
    "split on multicharacter separator (small)", 1000)
eleza rsplit_multichar_sep_small(STR):
    s = STR("this--is--a--test--of--the--emergency--broadcast--system")
    s_rsplit = s.rsplit
    pat = STR("--")
    kila x kwenye _RANGE_1000:
        s_rsplit(pat)

## split dna text on "ACTAT" characters
@bench('dna.split("ACTAT")',
       "split on multicharacter separator (dna)", 10)
eleza split_multichar_sep_dna(STR):
    s = _get_dna(STR)
    s_split = s.split
    pat = STR("ACTAT")
    kila x kwenye _RANGE_10:
        s_split(pat)

@bench('dna.rsplit("ACTAT")',
       "split on multicharacter separator (dna)", 10)
eleza rsplit_multichar_sep_dna(STR):
    s = _get_dna(STR)
    s_rsplit = s.rsplit
    pat = STR("ACTAT")
    kila x kwenye _RANGE_10:
        s_rsplit(pat)



## split ukijumuisha limits

GFF3_example = "\t".join([
    "I", "Genomic_canonical", "region", "357208", "396183", ".", "+", ".",
    "ID=Sequence:R119;note=Clone R119%3B Genbank AF063007;Name=R119"])

@bench('GFF3_example.split("\\t")', "tab split", 1000)
eleza tab_split_no_limit(STR):
    sep = STR("\t")
    s = STR(GFF3_example)
    s_split = s.split
    kila x kwenye _RANGE_1000:
        s_split(sep)

@bench('GFF3_example.split("\\t", 8)', "tab split", 1000)
eleza tab_split_limit(STR):
    sep = STR("\t")
    s = STR(GFF3_example)
    s_split = s.split
    kila x kwenye _RANGE_1000:
        s_split(sep, 8)

@bench('GFF3_example.rsplit("\\t")', "tab split", 1000)
eleza tab_rsplit_no_limit(STR):
    sep = STR("\t")
    s = STR(GFF3_example)
    s_rsplit = s.rsplit
    kila x kwenye _RANGE_1000:
        s_rsplit(sep)

@bench('GFF3_example.rsplit("\\t", 8)', "tab split", 1000)
eleza tab_rsplit_limit(STR):
    sep = STR("\t")
    s = STR(GFF3_example)
    s_rsplit = s.rsplit
    kila x kwenye _RANGE_1000:
        s_rsplit(sep, 8)

#### Count characters

@bench('...text.with.2000.newlines.count("\\n")',
       "count newlines", 10)
eleza count_newlines(STR):
    s = _get_2000_lines(STR)
    s_count = s.count
    nl = STR("\n")
    kila x kwenye _RANGE_10:
        s_count(nl)

# Orchid sequences concatenated, kutoka Biopython
_dna = """
CGTAACAAGGTTTCCGTAGGTGAACCTGCGGAAGGATCATTGTTGAGATCACATAATAATTGATCGGGTT
AATCTGGAGGATCTGTTTACTTTGGTCACCCATGAGCATTTGCTGTTGAAGTGACCTAGAATTGCCATCG
AGCCTCCTTGGGAGCTTTCTTGTTGGCGAGATCTAAACCCTTGCCCGGCGCAGTTTTGCTCCAAGTCGTT
TGACACATAATTGGTGAAGGGGGTGGCATCCTTCCCTGACCCTCCCCCAACTATTTTTTTAACAACTCTC
AGCAACGGAGACTCAGTCTTCGGCAAATGCGATAAATGGTGTGAATTGCAGAATCCCGTGCACCATCGAG
TCTTTGAACGCAAGTTGCGCCCGAGGCCATCAGGCCAAGGGCACGCCTGCCTGGGCATTGCGAGTCATAT
CTCTCCCTTAACGAGGCTGTCCATACATACTGTTCAGCCGGTGCGGATGTGAGTTTGGCCCCTTGTTCTT
TGGTACGGGGGGTCTAAGAGCTGCATGGGCTTTTGATGGTCCTAAATACGGCAAGAGGTGGACGAACTAT
GCTACAACAAAATTGTTGTGCAGAGGCCCCGGGTTGTCGTATTAGATGGGCCACCGTAATCTGAAGACCC
TTTTGAACCCCATTGGAGGCCCATCAACCCATGATCAGTTGATGGCCATTTGGTTGCGACCCCAGGTCAG
GTGAGCAACAGCTGTCGTAACAAGGTTTCCGTAGGGTGAACTGCGGAAGGATCATTGTTGAGATCACATA
ATAATTGATCGAGTTAATCTGGAGGATCTGTTTACTTGGGTCACCCATGGGCATTTGCTGTTGAAGTGAC
CTAGATTTGCCATCGAGCCTCCTTGGGAGCATCCTTGTTGGCGATATCTAAACCCTCAATTTTTCCCCCA
ATCAAATTACACAAAATTGGTGGAGGGGGTGGCATTCTTCCCTTACCCTCCCCCAAATATTTTTTTAACA
ACTCTCAGCAACGGATATCTCAGCTCTTGCATCGATGAAGAACCCACCGAAATGCGATAAATGGTGTGAA
TTGCAGAATCCCGTGAACCATCGAGTCTTTGAACGCAAGTTGCGCCCGAGGCCATCAGGCCAAGGGCACG
CCTGCCTGGGCATTGCGAGTCATATCTCTCCCTTAACGAGGCTGTCCATACATACTGTTCAGCCGGTGCG
GATGTGAGTTTGGCCCCTTGTTCTTTGGTACGGGGGGTCTAAGAGATGCATGGGCTTTTGATGGTCCTAA
ATACGGCAAGAGGTGGACGAACTATGCTACAACAAAATTGTTGTGCAAAGGCCCCGGGTTGTCGTATAAG
ATGGGCCACCGATATCTGAAGACCCTTTTGGACCCCATTGGAGCCCATCAACCCATGTCAGTTGATGGCC
ATTCGTAACAAGGTTTCCGTAGGTGAACCTGCGGAAGGATCATTGTTGAGATCACATAATAATTGATCGA
GTTAATCTGGAGGATCTGTTTACTTGGGTCACCCATGGGCATTTGCTGTTGAAGTGACCTAGATTTGCCA
TCGAGCCTCCTTGGGAGCTTTCTTGTTGGCGATATCTAAACCCTTGCCCGGCAGAGTTTTGGGAATCCCG
TGAACCATCGAGTCTTTGAACGCAAGTTGCGCCCGAGGCCATCAGGCCAAGGGCACGCCTGCCTGGGCAT
TGCGAGTCATATCTCTCCCTTAACGAGGCTGTCCATACACACCTGTTCAGCCGGTGCGGATGTGAGTTTG
GCCCCTTGTTCTTTGGTACGGGGGGTCTAAGAGCTGCATGGGCTTTTGATGGTCCTAAATACGGCAAGAG
GTGGACGAACTATGCTACAACAAAATTGTTGTGCAAAGGCCCCGGGTTGTCGTATTAGATGGGCCACCAT
AATCTGAAGACCCTTTTGAACCCCATTGGAGGCCCATCAACCCATGATCAGTTGATGGCCATTTGGTTGC
GACCCAGTCAGGTGAGGGTAGGTGAACCTGCGGAAGGATCATTGTTGAGATCACATAATAATTGATCGAG
TTAATCTGGAGGATCTGTTTACTTTGGTCACCCATGGGCATTTGCTGTTGAAGTGACCTAGATTTGCCAT
CGAGCCTCCTTGGGAGCTTTCTTGTTGGCGAGATCTAAACCCTTGCCCGGCGGAGTTTGGCGCCAAGTCA
TATGACACATAATTGGTGAAGGGGGTGGCATCCTGCCCTGACCCTCCCCAAATTATTTTTTTAACAACTC
TCAGCAACGGATATCTCGGCTCTTGCATCGATGAAGAACGCAGCGAAATGCGATAAATGGTGTGAATTGC
AGAATCCCGTGAACCATCGAGTCTTTGGAACGCAAGTTGCGCCCGAGGCCATCAGGCCAAGGGCACGCCT
GCCTGGGCATTGGGAATCATATCTCTCCCCTAACGAGGCTATCCAAACATACTGTTCATCCGGTGCGGAT
GTGAGTTTGGCCCCTTGTTCTTTGGTACCGGGGGTCTAAGAGCTGCATGGGCATTTGATGGTCCTCAAAA
CGGCAAGAGGTGGACGAACTATGCCACAACAAAATTGTTGTCCCAAGGCCCCGGGTTGTCGTATTAGATG
GGCCACCGTAACCTGAAGACCCTTTTGAACCCCATTGGAGGCCCATCAACCCATGATCAGTTGATGACCA
TTTGTTGCGACCCCAGTCAGCTGAGCAACCCGCTGAGTGGAAGGTCATTGCCGATATCACATAATAATTG
ATCGAGTTAATCTGGAGGATCTGTTTACTTGGTCACCCATGAGCATTTGCTGTTGAAGTGACCTAGATTT
GCCATCGAGCCTCCTTGGGAGTTTTCTTGTTGGCGAGATCTAAACCCTTGCCCGGCGGAGTTGTGCGCCA
AGTCATATGACACATAATTGGTGAAGGGGGTGGCATCCTGCCCTGACCCTCCCCAAATTATTTTTTTAAC
AACTCTCAGCAACGGATATCTCGGCTCTTGCATCGATGAAGAACGCAGCGAAATGCGATAAATGGTGTGA
ATTGCAGAATCCCGTGAACCATCGAGTCTTTGAACGCAAGTTGCGCCCGAGGCCATCAGGCCAAGGGCAC
GCCTGCCTGGGCATTGCGAGTCATATCTCTCCCTTAACGAGGCTGTCCATACATACTGTTCATCCGGTGC
GGATGTGAGTTTGGCCCCTTGTTCTTTGGTACGGGGGGTCTAAGAGCTGCATGGGCATTTGATGGTCCTC
AAAACGGCAAGAGGTGGACGAACTATGCTACAACCAAATTGTTGTCCCAAGGCCCCGGGTTGTCGTATTA
GATGGGCCACCGTAACCTGAAGACCCTTTTGAACCCCATTGGAGGCCCATCAACCCATGATCAGTTGATG
ACCATGTGTTGCGACCCCAGTCAGCTGAGCAACGCGCTGAGCGTAACAAGGTTTCCGTAGGTGGACCTCC
GGGAGGATCATTGTTGAGATCACATAATAATTGATCGAGGTAATCTGGAGGATCTGCATATTTTGGTCAC
"""
_dna = "".join(_dna.splitlines())
_dna = _dna * 25
_dna_bytes = bytes_from_str(_dna)
_dna_unicode = unicode_from_str(_dna)

eleza _get_dna(STR):
    ikiwa STR ni UNICODE:
        rudisha _dna_unicode
    ikiwa STR ni BYTES:
        rudisha _dna_bytes
    ashiria AssertionError

@bench('dna.count("AACT")', "count AACT substrings kwenye DNA example", 10)
eleza count_aact(STR):
    seq = _get_dna(STR)
    seq_count = seq.count
    needle = STR("AACT")
    kila x kwenye _RANGE_10:
        seq_count(needle)

##### startsukijumuisha na endswith

@bench('"Andrew".startswith("A")', 'startsukijumuisha single character', 1000)
eleza startswith_single(STR):
    s1 = STR("Andrew")
    s2 = STR("A")
    s1_startsukijumuisha = s1.startswith
    kila x kwenye _RANGE_1000:
        s1_startswith(s2)

@bench('"Andrew".startswith("Andrew")', 'startsukijumuisha multiple characters',
       1000)
eleza startswith_multiple(STR):
    s1 = STR("Andrew")
    s2 = STR("Andrew")
    s1_startsukijumuisha = s1.startswith
    kila x kwenye _RANGE_1000:
        s1_startswith(s2)

@bench('"Andrew".startswith("Anders")',
       'startsukijumuisha multiple characters - not!', 1000)
eleza startswith_multiple_not(STR):
    s1 = STR("Andrew")
    s2 = STR("Anders")
    s1_startsukijumuisha = s1.startswith
    kila x kwenye _RANGE_1000:
        s1_startswith(s2)


# endswith

@bench('"Andrew".endswith("w")', 'endsukijumuisha single character', 1000)
eleza endswith_single(STR):
    s1 = STR("Andrew")
    s2 = STR("w")
    s1_endsukijumuisha = s1.endswith
    kila x kwenye _RANGE_1000:
        s1_endswith(s2)

@bench('"Andrew".endswith("Andrew")', 'endsukijumuisha multiple characters', 1000)
eleza endswith_multiple(STR):
    s1 = STR("Andrew")
    s2 = STR("Andrew")
    s1_endsukijumuisha = s1.endswith
    kila x kwenye _RANGE_1000:
        s1_endswith(s2)

@bench('"Andrew".endswith("Anders")',
       'endsukijumuisha multiple characters - not!', 1000)
eleza endswith_multiple_not(STR):
    s1 = STR("Andrew")
    s2 = STR("Anders")
    s1_endsukijumuisha = s1.endswith
    kila x kwenye _RANGE_1000:
        s1_endswith(s2)

#### Strip

@bench('"Hello!\\n".strip()', 'strip terminal newline', 1000)
eleza terminal_newline_strip_right(STR):
    s = STR("Hello!\n")
    s_strip = s.strip
    kila x kwenye _RANGE_1000:
        s_strip()

@bench('"Hello!\\n".rstrip()', 'strip terminal newline', 1000)
eleza terminal_newline_rstrip(STR):
    s = STR("Hello!\n")
    s_rstrip = s.rstrip
    kila x kwenye _RANGE_1000:
        s_rstrip()

@bench('"\\nHello!".strip()', 'strip terminal newline', 1000)
eleza terminal_newline_strip_left(STR):
    s = STR("\nHello!")
    s_strip = s.strip
    kila x kwenye _RANGE_1000:
        s_strip()

@bench('"\\nHello!\\n".strip()', 'strip terminal newline', 1000)
eleza terminal_newline_strip_both(STR):
    s = STR("\nHello!\n")
    s_strip = s.strip
    kila x kwenye _RANGE_1000:
        s_strip()

@bench('"\\nHello!".rstrip()', 'strip terminal newline', 1000)
eleza terminal_newline_lstrip(STR):
    s = STR("\nHello!")
    s_lstrip = s.lstrip
    kila x kwenye _RANGE_1000:
        s_lstrip()

@bench('s="Hello!\\n"; s[:-1] ikiwa s[-1]=="\\n" isipokua s',
       'strip terminal newline', 1000)
eleza terminal_newline_if_else(STR):
    s = STR("Hello!\n")
    NL = STR("\n")
    kila x kwenye _RANGE_1000:
        s[:-1] ikiwa (s[-1] == NL) isipokua s


# Strip multiple spaces ama tabs

@bench('"Hello\\t   \\t".strip()', 'strip terminal spaces na tabs', 1000)
eleza terminal_space_strip(STR):
    s = STR("Hello\t   \t!")
    s_strip = s.strip
    kila x kwenye _RANGE_1000:
        s_strip()

@bench('"Hello\\t   \\t".rstrip()', 'strip terminal spaces na tabs', 1000)
eleza terminal_space_rstrip(STR):
    s = STR("Hello!\t   \t")
    s_rstrip = s.rstrip
    kila x kwenye _RANGE_1000:
        s_rstrip()

@bench('"\\t   \\tHello".rstrip()', 'strip terminal spaces na tabs', 1000)
eleza terminal_space_lstrip(STR):
    s = STR("\t   \tHello!")
    s_lstrip = s.lstrip
    kila x kwenye _RANGE_1000:
        s_lstrip()


#### replace
@bench('"This ni a test".replace(" ", "\\t")', 'replace single character',
       1000)
eleza replace_single_character(STR):
    s = STR("This ni a test!")
    from_str = STR(" ")
    to_str = STR("\t")
    s_replace = s.replace
    kila x kwenye _RANGE_1000:
        s_replace(from_str, to_str)

@uses_re
@bench('re.sub(" ", "\\t", "This ni a test"', 'replace single character',
       1000)
eleza replace_single_character_re(STR):
    s = STR("This ni a test!")
    pat = re.compile(STR(" "))
    to_str = STR("\t")
    pat_sub = pat.sub
    kila x kwenye _RANGE_1000:
        pat_sub(to_str, s)

@bench('"...text.with.2000.lines...replace("\\n", " ")',
       'replace single character, big string', 10)
eleza replace_single_character_big(STR):
    s = _get_2000_lines(STR)
    from_str = STR("\n")
    to_str = STR(" ")
    s_replace = s.replace
    kila x kwenye _RANGE_10:
        s_replace(from_str, to_str)

@uses_re
@bench('re.sub("\\n", " ", "...text.with.2000.lines...")',
       'replace single character, big string', 10)
eleza replace_single_character_big_re(STR):
    s = _get_2000_lines(STR)
    pat = re.compile(STR("\n"))
    to_str = STR(" ")
    pat_sub = pat.sub
    kila x kwenye _RANGE_10:
        pat_sub(to_str, s)


@bench('dna.replace("ATC", "ATT")',
       'replace multiple characters, dna', 10)
eleza replace_multiple_characters_dna(STR):
    seq = _get_dna(STR)
    from_str = STR("ATC")
    to_str = STR("ATT")
    seq_replace = seq.replace
    kila x kwenye _RANGE_10:
        seq_replace(from_str, to_str)

# This increases the character count
@bench('"...text.with.2000.newlines...replace("\\n", "\\r\\n")',
       'replace na expand multiple characters, big string', 10)
eleza replace_multiple_character_big(STR):
    s = _get_2000_lines(STR)
    from_str = STR("\n")
    to_str = STR("\r\n")
    s_replace = s.replace
    kila x kwenye _RANGE_10:
        s_replace(from_str, to_str)


# This decreases the character count
@bench('"When shall we three meet again?".replace("ee", "")',
       'replace/remove multiple characters', 1000)
eleza replace_multiple_character_remove(STR):
    s = STR("When shall we three meet again?")
    from_str = STR("ee")
    to_str = STR("")
    s_replace = s.replace
    kila x kwenye _RANGE_1000:
        s_replace(from_str, to_str)


big_s = "A" + ("Z"*128*1024)
big_s_bytes = bytes_from_str(big_s)
big_s_unicode = unicode_from_str(big_s)
eleza _get_big_s(STR):
    ikiwa STR ni UNICODE: rudisha big_s_unicode
    ikiwa STR ni BYTES: rudisha big_s_bytes
    ashiria AssertionError

# The older replace implementation counted all matches kwenye
# the string even when it only needed to make one replacement.
@bench('("A" + ("Z"*128*1024)).replace("A", "BB", 1)',
       'quick replace single character match', 10)
eleza quick_replace_single_match(STR):
    s = _get_big_s(STR)
    from_str = STR("A")
    to_str = STR("BB")
    s_replace = s.replace
    kila x kwenye _RANGE_10:
        s_replace(from_str, to_str, 1)

@bench('("A" + ("Z"*128*1024)).replace("AZZ", "BBZZ", 1)',
       'quick replace multiple character match', 10)
eleza quick_replace_multiple_match(STR):
    s = _get_big_s(STR)
    from_str = STR("AZZ")
    to_str = STR("BBZZ")
    s_replace = s.replace
    kila x kwenye _RANGE_10:
        s_replace(from_str, to_str, 1)


####

# CCP does a lot of this, kila internationalisation of ingame messages.
_format = "The %(thing)s ni %(place)s the %(location)s."
_format_dict = { "thing":"THING", "place":"PLACE", "location":"LOCATION", }
_format_bytes = bytes_from_str(_format)
_format_unicode = unicode_from_str(_format)
_format_dict_bytes = dict((bytes_from_str(k), bytes_from_str(v)) kila (k,v) kwenye _format_dict.items())
_format_dict_unicode = dict((unicode_from_str(k), unicode_from_str(v)) kila (k,v) kwenye _format_dict.items())

eleza _get_format(STR):
    ikiwa STR ni UNICODE:
        rudisha _format_unicode
    ikiwa STR ni BYTES:
        ikiwa sys.version_info >= (3,):
            ashiria UnsupportedType
        rudisha _format_bytes
    ashiria AssertionError

eleza _get_format_dict(STR):
    ikiwa STR ni UNICODE:
        rudisha _format_dict_unicode
    ikiwa STR ni BYTES:
        ikiwa sys.version_info >= (3,):
            ashiria UnsupportedType
        rudisha _format_dict_bytes
    ashiria AssertionError

# Formatting.
@bench('"The %(k1)s ni %(k2)s the %(k3)s."%{"k1":"x","k2":"y","k3":"z",}',
       'formatting a string type ukijumuisha a dict', 1000)
eleza format_with_dict(STR):
    s = _get_format(STR)
    d = _get_format_dict(STR)
    kila x kwenye _RANGE_1000:
        s % d


#### Upper- na lower- case conversion

@bench('("Where kwenye the world ni Carmen San Deigo?"*10).lower()',
       "case conversion -- rare", 1000)
eleza lower_conversion_rare(STR):
    s = STR("Where kwenye the world ni Carmen San Deigo?"*10)
    s_lower = s.lower
    kila x kwenye _RANGE_1000:
        s_lower()

@bench('("WHERE IN THE WORLD IS CARMEN SAN DEIGO?"*10).lower()',
       "case conversion -- dense", 1000)
eleza lower_conversion_dense(STR):
    s = STR("WHERE IN THE WORLD IS CARMEN SAN DEIGO?"*10)
    s_lower = s.lower
    kila x kwenye _RANGE_1000:
        s_lower()


@bench('("wHERE IN THE WORLD IS cARMEN sAN dEIGO?"*10).upper()',
       "case conversion -- rare", 1000)
eleza upper_conversion_rare(STR):
    s = STR("Where kwenye the world ni Carmen San Deigo?"*10)
    s_upper = s.upper
    kila x kwenye _RANGE_1000:
        s_upper()

@bench('("where kwenye the world ni carmen san deigo?"*10).upper()',
       "case conversion -- dense", 1000)
eleza upper_conversion_dense(STR):
    s = STR("where kwenye the world ni carmen san deigo?"*10)
    s_upper = s.upper
    kila x kwenye _RANGE_1000:
        s_upper()


# end of benchmarks

#################

kundi BenchTimer(timeit.Timer):
    eleza best(self, repeat=1):
        kila i kwenye range(1, 10):
            number = 10**i
            x = self.timeit(number)
            ikiwa x > 0.02:
                koma
        times = [x]
        kila i kwenye range(1, repeat):
            times.append(self.timeit(number))
        rudisha min(times) / number

eleza main():
    (options, test_names) = parser.parse_args()
    ikiwa options.bytes_only na options.unicode_only:
        ashiria SystemExit("Only one of --8-bit na --unicode are allowed")

    bench_functions = []
    kila (k,v) kwenye globals().items():
        ikiwa hasattr(v, "is_bench"):
            ikiwa test_names:
                kila name kwenye test_names:
                    ikiwa name kwenye v.group:
                        koma
                isipokua:
                    # Not selected, ignore
                    endelea
            ikiwa options.skip_re na hasattr(v, "uses_re"):
                endelea

            bench_functions.append( (v.group, k, v) )
    bench_functions.sort()

    p("bytes\tunicode")
    p("(in ms)\t(in ms)\t%\tcomment")

    bytes_total = uni_total = 0.0

    kila title, group kwenye itertools.groupby(bench_functions,
                                      operator.itemgetter(0)):
        # Flush buffer before each group
        sys.stdout.flush()
        p("="*10, title)
        kila (_, k, v) kwenye group:
            ikiwa hasattr(v, "is_bench"):
                bytes_time = 0.0
                bytes_time_s = " - "
                ikiwa sio options.unicode_only:
                    jaribu:
                        bytes_time = BenchTimer("__main__.%s(__main__.BYTES)" % (k,),
                                                "agiza __main__").best(REPEAT)
                        bytes_time_s = "%.2f" % (1000 * bytes_time)
                        bytes_total += bytes_time
                    tatizo UnsupportedType:
                        bytes_time_s = "N/A"
                uni_time = 0.0
                uni_time_s = " - "
                ikiwa sio options.bytes_only:
                    jaribu:
                        uni_time = BenchTimer("__main__.%s(__main__.UNICODE)" % (k,),
                                              "agiza __main__").best(REPEAT)
                        uni_time_s = "%.2f" % (1000 * uni_time)
                        uni_total += uni_time
                    tatizo UnsupportedType:
                        uni_time_s = "N/A"
                jaribu:
                    average = bytes_time/uni_time
                tatizo (TypeError, ZeroDivisionError):
                    average = 0.0
                p("%s\t%s\t%.1f\t%s (*%d)" % (
                    bytes_time_s, uni_time_s, 100.*average,
                    v.comment, v.repeat_count))

    ikiwa bytes_total == uni_total == 0.0:
        p("That was zippy!")
    isipokua:
        jaribu:
            ratio = bytes_total/uni_total
        tatizo ZeroDivisionError:
            ratio = 0.0
        p("%.2f\t%.2f\t%.1f\t%s" % (
            1000*bytes_total, 1000*uni_total, 100.*ratio,
            "TOTAL"))

ikiwa __name__ == "__main__":
    main()
