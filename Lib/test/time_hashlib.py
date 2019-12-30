# It's intended that this script be run by hand.  It runs speed tests on
# hashlib functions; it does sio test kila correctness.

agiza sys
agiza time
agiza hashlib


eleza creatorFunc():
     ashiria RuntimeError("eek, creatorFunc sio overridden")

eleza test_scaled_msg(scale, name):
    iterations = 106201//scale * 20
    longStr = b'Z'*scale

    localCF = creatorFunc
    start = time.perf_counter()
    kila f kwenye range(iterations):
        x = localCF(longStr).digest()
    end = time.perf_counter()

    andika(('%2.2f' % (end-start)), "seconds", iterations, "x", len(longStr), "bytes", name)

eleza test_create():
    start = time.perf_counter()
    kila f kwenye range(20000):
        d = creatorFunc()
    end = time.perf_counter()

    andika(('%2.2f' % (end-start)), "seconds", '[20000 creations]')

eleza test_zero():
    start = time.perf_counter()
    kila f kwenye range(20000):
        x = creatorFunc().digest()
    end = time.perf_counter()

    andika(('%2.2f' % (end-start)), "seconds", '[20000 "" digests]')



hName = sys.argv[1]

#
# setup our creatorFunc to test the requested hash
#
ikiwa hName kwenye ('_md5', '_sha'):
    exec('agiza '+hName)
    exec('creatorFunc = '+hName+'.new')
    andika("testing speed of old", hName, "legacy interface")
elikiwa hName == '_hashlib' na len(sys.argv) > 3:
    agiza _hashlib
    exec('creatorFunc = _hashlib.%s' % sys.argv[2])
    andika("testing speed of _hashlib.%s" % sys.argv[2], getattr(_hashlib, sys.argv[2]))
elikiwa hName == '_hashlib' na len(sys.argv) == 3:
    agiza _hashlib
    exec('creatorFunc = lambda x=_hashlib.new : x(%r)' % sys.argv[2])
    andika("testing speed of _hashlib.new(%r)" % sys.argv[2])
elikiwa hasattr(hashlib, hName) na hasattr(getattr(hashlib, hName), '__call__'):
    creatorFunc = getattr(hashlib, hName)
    andika("testing speed of hashlib."+hName, getattr(hashlib, hName))
isipokua:
    exec("creatorFunc = lambda x=hashlib.new : x(%r)" % hName)
    andika("testing speed of hashlib.new(%r)" % hName)

jaribu:
    test_create()
except ValueError:
    andika()
    andika("pass argument(s) naming the hash to run a speed test on:")
    andika(" '_md5' na '_sha' test the legacy builtin md5 na sha")
    andika(" '_hashlib' 'openssl_hName' 'fast' tests the builtin _hashlib")
    andika(" '_hashlib' 'hName' tests builtin _hashlib.new(shaFOO)")
    andika(" 'hName' tests the hashlib.hName() implementation ikiwa it exists")
    andika("         otherwise it uses hashlib.new(hName).")
    andika()
    raise

test_zero()
test_scaled_msg(scale=106201, name='[huge data]')
test_scaled_msg(scale=10620, name='[large data]')
test_scaled_msg(scale=1062, name='[medium data]')
test_scaled_msg(scale=424, name='[4*small data]')
test_scaled_msg(scale=336, name='[3*small data]')
test_scaled_msg(scale=212, name='[2*small data]')
test_scaled_msg(scale=106, name='[small data]')
test_scaled_msg(scale=creatorFunc().digest_size, name='[digest_size data]')
test_scaled_msg(scale=10, name='[tiny data]')
