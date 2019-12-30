# Simple Python script to download a file. Used kama a fallback
# when other more reliable methods fail.
#
kutoka __future__ agiza print_function
agiza sys

jaribu:
    kutoka requests agiza get
tatizo ImportError:
    jaribu:
        kutoka urllib.request agiza urlretrieve
        USING = "urllib.request.urlretrieve"
    tatizo ImportError:
        jaribu:
            kutoka urllib agiza urlretrieve
            USING = "urllib.retrieve"
        tatizo ImportError:
            andika("Python at", sys.executable, "is sio suitable",
                  "kila downloading files.", file=sys.stderr)
            sys.exit(2)
isipokua:
    USING = "requests.get"

    eleza urlretrieve(url, filename):
        r = get(url, stream=Kweli)
        r.raise_for_status()
        ukijumuisha open(filename, 'wb') kama f:
            kila chunk kwenye r.iter_content(chunk_size=1024):
                f.write(chunk)
        rudisha filename

ikiwa __name__ == '__main__':
    ikiwa len(sys.argv) != 3:
        andika("Usage: urlretrieve.py [url] [filename]", file=sys.stderr)
        sys.exit(1)
    URL = sys.argv[1]
    FILENAME = sys.argv[2]
    andika("Downloading from", URL, "to", FILENAME, "using", USING)
    urlretrieve(URL, FILENAME)
