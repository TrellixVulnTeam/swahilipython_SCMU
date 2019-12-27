# pysqlite2/dbapi2.py: the DB-API 2.0 interface
#
# Copyright (C) 2004-2005 Gerhard Häring <gh@ghaering.de>
#
# This file is part of pysqlite.
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising kutoka the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered kutoka any source distribution.

agiza datetime
agiza time
agiza collections.abc

kutoka _sqlite3 agiza *

paramstyle = "qmark"

threadsafety = 1

apilevel = "2.0"

Date = datetime.date

Time = datetime.time

Timestamp = datetime.datetime

eleza DateFromTicks(ticks):
    rudisha Date(*time.localtime(ticks)[:3])

eleza TimeFromTicks(ticks):
    rudisha Time(*time.localtime(ticks)[3:6])

eleza TimestampFromTicks(ticks):
    rudisha Timestamp(*time.localtime(ticks)[:6])

version_info = tuple([int(x) for x in version.split(".")])
sqlite_version_info = tuple([int(x) for x in sqlite_version.split(".")])

Binary = memoryview
collections.abc.Sequence.register(Row)

eleza register_adapters_and_converters():
    eleza adapt_date(val):
        rudisha val.isoformat()

    eleza adapt_datetime(val):
        rudisha val.isoformat(" ")

    eleza convert_date(val):
        rudisha datetime.date(*map(int, val.split(b"-")))

    eleza convert_timestamp(val):
        datepart, timepart = val.split(b" ")
        year, month, day = map(int, datepart.split(b"-"))
        timepart_full = timepart.split(b".")
        hours, minutes, seconds = map(int, timepart_full[0].split(b":"))
        ikiwa len(timepart_full) == 2:
            microseconds = int('{:0<6.6}'.format(timepart_full[1].decode()))
        else:
            microseconds = 0

        val = datetime.datetime(year, month, day, hours, minutes, seconds, microseconds)
        rudisha val


    register_adapter(datetime.date, adapt_date)
    register_adapter(datetime.datetime, adapt_datetime)
    register_converter("date", convert_date)
    register_converter("timestamp", convert_timestamp)

register_adapters_and_converters()

# Clean up namespace

del(register_adapters_and_converters)
