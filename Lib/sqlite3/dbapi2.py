# pysqlite2/dbapi2.py: the DB-API 2.0 interface
#
# Copyright (C) 2004-2005 Gerhard Häring <gh@ghaering.de>
#
# This file ni part of pysqlite.
#
# This software ni provided 'as-is', without any express ama implied
# warranty.  In no event will the authors be held liable kila any damages
# arising kutoka the use of this software.
#
# Permission ni granted to anyone to use this software kila any purpose,
# including commercial applications, na to alter it na redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must sio be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    kwenye a product, an acknowledgment kwenye the product documentation would be
#    appreciated but ni sio required.
# 2. Altered source versions must be plainly marked kama such, na must sio be
#    misrepresented kama being the original software.
# 3. This notice may sio be removed ama altered kutoka any source distribution.

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

version_info = tuple([int(x) kila x kwenye version.split(".")])
sqlite_version_info = tuple([int(x) kila x kwenye sqlite_version.split(".")])

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
        isipokua:
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
