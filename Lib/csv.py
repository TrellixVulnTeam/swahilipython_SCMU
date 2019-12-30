
"""
csv.py - read/write/investigate CSV files
"""

agiza re
kutoka _csv agiza Error, __version__, writer, reader, register_dialect, \
                 unregister_dialect, get_dialect, list_dialects, \
                 field_size_limit, \
                 QUOTE_MINIMAL, QUOTE_ALL, QUOTE_NONNUMERIC, QUOTE_NONE, \
                 __doc__
kutoka _csv agiza Dialect as _Dialect

kutoka io agiza StringIO

__all__ = ["QUOTE_MINIMAL", "QUOTE_ALL", "QUOTE_NONNUMERIC", "QUOTE_NONE",
           "Error", "Dialect", "__doc__", "excel", "excel_tab",
           "field_size_limit", "reader", "writer",
           "register_dialect", "get_dialect", "list_dialects", "Sniffer",
           "unregister_dialect", "__version__", "DictReader", "DictWriter",
           "unix_dialect"]

kundi Dialect:
    """Describe a CSV dialect.

    This must be subclassed (see csv.excel).  Valid attributes are:
    delimiter, quotechar, escapechar, doublequote, skipinitialspace,
    lineterminator, quoting.

    """
    _name = ""
    _valid = Uongo
    # placeholders
    delimiter = Tupu
    quotechar = Tupu
    escapechar = Tupu
    doublequote = Tupu
    skipinitialspace = Tupu
    lineterminator = Tupu
    quoting = Tupu

    eleza __init__(self):
        ikiwa self.__class__ != Dialect:
            self._valid = Kweli
        self._validate()

    eleza _validate(self):
        jaribu:
            _Dialect(self)
        except TypeError as e:
            # We do this kila compatibility ukijumuisha py2.3
             ashiria Error(str(e))

kundi excel(Dialect):
    """Describe the usual properties of Excel-generated CSV files."""
    delimiter = ','
    quotechar = '"'
    doublequote = Kweli
    skipinitialspace = Uongo
    lineterminator = '\r\n'
    quoting = QUOTE_MINIMAL
register_dialect("excel", excel)

kundi excel_tab(excel):
    """Describe the usual properties of Excel-generated TAB-delimited files."""
    delimiter = '\t'
register_dialect("excel-tab", excel_tab)

kundi unix_dialect(Dialect):
    """Describe the usual properties of Unix-generated CSV files."""
    delimiter = ','
    quotechar = '"'
    doublequote = Kweli
    skipinitialspace = Uongo
    lineterminator = '\n'
    quoting = QUOTE_ALL
register_dialect("unix", unix_dialect)


kundi DictReader:
    eleza __init__(self, f, fieldnames=Tupu, restkey=Tupu, restval=Tupu,
                 dialect="excel", *args, **kwds):
        self._fieldnames = fieldnames   # list of keys kila the dict
        self.restkey = restkey          # key to catch long rows
        self.restval = restval          # default value kila short rows
        self.reader = reader(f, dialect, *args, **kwds)
        self.dialect = dialect
        self.line_num = 0

    eleza __iter__(self):
        rudisha self

    @property
    eleza fieldnames(self):
        ikiwa self._fieldnames ni Tupu:
            jaribu:
                self._fieldnames = next(self.reader)
            except StopIteration:
                pass
        self.line_num = self.reader.line_num
        rudisha self._fieldnames

    @fieldnames.setter
    eleza fieldnames(self, value):
        self._fieldnames = value

    eleza __next__(self):
        ikiwa self.line_num == 0:
            # Used only kila its side effect.
            self.fieldnames
        row = next(self.reader)
        self.line_num = self.reader.line_num

        # unlike the basic reader, we prefer sio to rudisha blanks,
        # because we will typically wind up ukijumuisha a dict full of Tupu
        # values
        wakati row == []:
            row = next(self.reader)
        d = dict(zip(self.fieldnames, row))
        lf = len(self.fieldnames)
        lr = len(row)
        ikiwa lf < lr:
            d[self.restkey] = row[lf:]
        elikiwa lf > lr:
            kila key kwenye self.fieldnames[lr:]:
                d[key] = self.restval
        rudisha d


kundi DictWriter:
    eleza __init__(self, f, fieldnames, restval="", extrasaction="raise",
                 dialect="excel", *args, **kwds):
        self.fieldnames = fieldnames    # list of keys kila the dict
        self.restval = restval          # kila writing short dicts
        ikiwa extrasaction.lower() sio kwenye ("raise", "ignore"):
             ashiria ValueError("extrasaction (%s) must be 'raise' ama 'ignore'"
                             % extrasaction)
        self.extrasaction = extrasaction
        self.writer = writer(f, dialect, *args, **kwds)

    eleza writeheader(self):
        header = dict(zip(self.fieldnames, self.fieldnames))
        rudisha self.writerow(header)

    eleza _dict_to_list(self, rowdict):
        ikiwa self.extrasaction == "raise":
            wrong_fields = rowdict.keys() - self.fieldnames
            ikiwa wrong_fields:
                 ashiria ValueError("dict contains fields sio kwenye fieldnames: "
                                 + ", ".join([repr(x) kila x kwenye wrong_fields]))
        rudisha (rowdict.get(key, self.restval) kila key kwenye self.fieldnames)

    eleza writerow(self, rowdict):
        rudisha self.writer.writerow(self._dict_to_list(rowdict))

    eleza writerows(self, rowdicts):
        rudisha self.writer.writerows(map(self._dict_to_list, rowdicts))

# Guard Sniffer's type checking against builds that exclude complex()
jaribu:
    complex
except NameError:
    complex = float

kundi Sniffer:
    '''
    "Sniffs" the format of a CSV file (i.e. delimiter, quotechar)
    Returns a Dialect object.
    '''
    eleza __init__(self):
        # kwenye case there ni more than one possible delimiter
        self.preferred = [',', '\t', ';', ' ', ':']


    eleza sniff(self, sample, delimiters=Tupu):
        """
        Returns a dialect (or Tupu) corresponding to the sample
        """

        quotechar, doublequote, delimiter, skipinitialspace = \
                   self._guess_quote_and_delimiter(sample, delimiters)
        ikiwa sio delimiter:
            delimiter, skipinitialspace = self._guess_delimiter(sample,
                                                                delimiters)

        ikiwa sio delimiter:
             ashiria Error("Could sio determine delimiter")

        kundi dialect(Dialect):
            _name = "sniffed"
            lineterminator = '\r\n'
            quoting = QUOTE_MINIMAL
            # escapechar = ''

        dialect.doublequote = doublequote
        dialect.delimiter = delimiter
        # _csv.reader won't accept a quotechar of ''
        dialect.quotechar = quotechar ama '"'
        dialect.skipinitialspace = skipinitialspace

        rudisha dialect


    eleza _guess_quote_and_delimiter(self, data, delimiters):
        """
        Looks kila text enclosed between two identical quotes
        (the probable quotechar) which are preceded na followed
        by the same character (the probable delimiter).
        For example:
                         ,'some text',
        The quote ukijumuisha the most wins, same ukijumuisha the delimiter.
        If there ni no quotechar the delimiter can't be determined
        this way.
        """

        matches = []
        kila restr kwenye (r'(?P<delim>[^\w\n"\'])(?P<space> ?)(?P<quote>["\']).*?(?P=quote)(?P=delim)', # ,".*?",
                      r'(?:^|\n)(?P<quote>["\']).*?(?P=quote)(?P<delim>[^\w\n"\'])(?P<space> ?)',   #  ".*?",
                      r'(?P<delim>[^\w\n"\'])(?P<space> ?)(?P<quote>["\']).*?(?P=quote)(?:$|\n)',   # ,".*?"
                      r'(?:^|\n)(?P<quote>["\']).*?(?P=quote)(?:$|\n)'):                            #  ".*?" (no delim, no space)
            regexp = re.compile(restr, re.DOTALL | re.MULTILINE)
            matches = regexp.findall(data)
            ikiwa matches:
                koma

        ikiwa sio matches:
            # (quotechar, doublequote, delimiter, skipinitialspace)
            rudisha ('', Uongo, Tupu, 0)
        quotes = {}
        delims = {}
        spaces = 0
        groupindex = regexp.groupindex
        kila m kwenye matches:
            n = groupindex['quote'] - 1
            key = m[n]
            ikiwa key:
                quotes[key] = quotes.get(key, 0) + 1
            jaribu:
                n = groupindex['delim'] - 1
                key = m[n]
            except KeyError:
                endelea
            ikiwa key na (delimiters ni Tupu ama key kwenye delimiters):
                delims[key] = delims.get(key, 0) + 1
            jaribu:
                n = groupindex['space'] - 1
            except KeyError:
                endelea
            ikiwa m[n]:
                spaces += 1

        quotechar = max(quotes, key=quotes.get)

        ikiwa delims:
            delim = max(delims, key=delims.get)
            skipinitialspace = delims[delim] == spaces
            ikiwa delim == '\n': # most likely a file ukijumuisha a single column
                delim = ''
        isipokua:
            # there ni *no* delimiter, it's a single column of quoted data
            delim = ''
            skipinitialspace = 0

        # ikiwa we see an extra quote between delimiters, we've got a
        # double quoted format
        dq_regexp = re.compile(
                               r"((%(delim)s)|^)\W*%(quote)s[^%(delim)s\n]*%(quote)s[^%(delim)s\n]*%(quote)s\W*((%(delim)s)|$)" % \
                               {'delim':re.escape(delim), 'quote':quotechar}, re.MULTILINE)



        ikiwa dq_regexp.search(data):
            doublequote = Kweli
        isipokua:
            doublequote = Uongo

        rudisha (quotechar, doublequote, delim, skipinitialspace)


    eleza _guess_delimiter(self, data, delimiters):
        """
        The delimiter /should/ occur the same number of times on
        each row. However, due to malformed data, it may not. We don't want
        an all ama nothing approach, so we allow kila small variations kwenye this
        number.
          1) build a table of the frequency of each character on every line.
          2) build a table of frequencies of this frequency (meta-frequency?),
             e.g.  'x occurred 5 times kwenye 10 rows, 6 times kwenye 1000 rows,
             7 times kwenye 2 rows'
          3) use the mode of the meta-frequency to determine the /expected/
             frequency kila that character
          4) find out how often the character actually meets that goal
          5) the character that best meets its goal ni the delimiter
        For performance reasons, the data ni evaluated kwenye chunks, so it can
        try na evaluate the smallest portion of the data possible, evaluating
        additional chunks as necessary.
        """

        data = list(filter(Tupu, data.split('\n')))

        ascii = [chr(c) kila c kwenye range(127)] # 7-bit ASCII

        # build frequency tables
        chunkLength = min(10, len(data))
        iteration = 0
        charFrequency = {}
        modes = {}
        delims = {}
        start, end = 0, chunkLength
        wakati start < len(data):
            iteration += 1
            kila line kwenye data[start:end]:
                kila char kwenye ascii:
                    metaFrequency = charFrequency.get(char, {})
                    # must count even ikiwa frequency ni 0
                    freq = line.count(char)
                    # value ni the mode
                    metaFrequency[freq] = metaFrequency.get(freq, 0) + 1
                    charFrequency[char] = metaFrequency

            kila char kwenye charFrequency.keys():
                items = list(charFrequency[char].items())
                ikiwa len(items) == 1 na items[0][0] == 0:
                    endelea
                # get the mode of the frequencies
                ikiwa len(items) > 1:
                    modes[char] = max(items, key=lambda x: x[1])
                    # adjust the mode - subtract the sum of all
                    # other frequencies
                    items.remove(modes[char])
                    modes[char] = (modes[char][0], modes[char][1]
                                   - sum(item[1] kila item kwenye items))
                isipokua:
                    modes[char] = items[0]

            # build a list of possible delimiters
            modeList = modes.items()
            total = float(min(chunkLength * iteration, len(data)))
            # (rows of consistent data) / (number of rows) = 100%
            consistency = 1.0
            # minimum consistency threshold
            threshold = 0.9
            wakati len(delims) == 0 na consistency >= threshold:
                kila k, v kwenye modeList:
                    ikiwa v[0] > 0 na v[1] > 0:
                        ikiwa ((v[1]/total) >= consistency and
                            (delimiters ni Tupu ama k kwenye delimiters)):
                            delims[k] = v
                consistency -= 0.01

            ikiwa len(delims) == 1:
                delim = list(delims.keys())[0]
                skipinitialspace = (data[0].count(delim) ==
                                    data[0].count("%c " % delim))
                rudisha (delim, skipinitialspace)

            # analyze another chunkLength lines
            start = end
            end += chunkLength

        ikiwa sio delims:
            rudisha ('', 0)

        # ikiwa there's more than one, fall back to a 'preferred' list
        ikiwa len(delims) > 1:
            kila d kwenye self.preferred:
                ikiwa d kwenye delims.keys():
                    skipinitialspace = (data[0].count(d) ==
                                        data[0].count("%c " % d))
                    rudisha (d, skipinitialspace)

        # nothing isipokua indicates a preference, pick the character that
        # dominates(?)
        items = [(v,k) kila (k,v) kwenye delims.items()]
        items.sort()
        delim = items[-1][1]

        skipinitialspace = (data[0].count(delim) ==
                            data[0].count("%c " % delim))
        rudisha (delim, skipinitialspace)


    eleza has_header(self, sample):
        # Creates a dictionary of types of data kwenye each column. If any
        # column ni of a single type (say, integers), *except* kila the first
        # row, then the first row ni presumed to be labels. If the type
        # can't be determined, it ni assumed to be a string kwenye which case
        # the length of the string ni the determining factor: ikiwa all of the
        # rows except kila the first are the same length, it's a header.
        # Finally, a 'vote' ni taken at the end kila each column, adding or
        # subtracting kutoka the likelihood of the first row being a header.

        rdr = reader(StringIO(sample), self.sniff(sample))

        header = next(rdr) # assume first row ni header

        columns = len(header)
        columnTypes = {}
        kila i kwenye range(columns): columnTypes[i] = Tupu

        checked = 0
        kila row kwenye rdr:
            # arbitrary number of rows to check, to keep it sane
            ikiwa checked > 20:
                koma
            checked += 1

            ikiwa len(row) != columns:
                endelea # skip rows that have irregular number of columns

            kila col kwenye list(columnTypes.keys()):

                kila thisType kwenye [int, float, complex]:
                    jaribu:
                        thisType(row[col])
                        koma
                    except (ValueError, OverflowError):
                        pass
                isipokua:
                    # fallback to length of string
                    thisType = len(row[col])

                ikiwa thisType != columnTypes[col]:
                    ikiwa columnTypes[col] ni Tupu: # add new column type
                        columnTypes[col] = thisType
                    isipokua:
                        # type ni inconsistent, remove column from
                        # consideration
                        toa columnTypes[col]

        # finally, compare results against first row na "vote"
        # on whether it's a header
        hasHeader = 0
        kila col, colType kwenye columnTypes.items():
            ikiwa type(colType) == type(0): # it's a length
                ikiwa len(header[col]) != colType:
                    hasHeader += 1
                isipokua:
                    hasHeader -= 1
            isipokua: # attempt typecast
                jaribu:
                    colType(header[col])
                except (ValueError, TypeError):
                    hasHeader += 1
                isipokua:
                    hasHeader -= 1

        rudisha hasHeader > 0
