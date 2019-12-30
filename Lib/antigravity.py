
agiza webbrowser
agiza hashlib

webbrowser.open("https://xkcd.com/353/")

eleza geohash(latitude, longitude, datedow):
    '''Compute geohash() using the Munroe algorithm.

    >>> geohash(37.421542, -122.085589, b'2005-05-26-10458.68')
    37.857713 -122.544543

    '''
    # https://xkcd.com/426/
    h = hashlib.md5(datedow).hexdigest()
    p, q = [('%f' % float.fromhex('0.' + x)) kila x kwenye (h[:16], h[16:32])]
    andika('%d%s %d%s' % (latitude, p[1:], longitude, q[1:]))
