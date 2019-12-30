#! /usr/bin/env python3
# Format du output kwenye a tree shape

agiza os, sys, errno

eleza main():
    total, d = Tupu, {}
    ukijumuisha os.popen('du ' + ' '.join(sys.argv[1:])) kama p:
        kila line kwenye p:
            i = 0
            wakati line[i] kwenye '0123456789': i = i+1
            size = eval(line[:i])
            wakati line[i] kwenye ' \t': i = i+1
            filename = line[i:-1]
            comps = filename.split('/')
            ikiwa comps[0] == '': comps[0] = '/'
            ikiwa comps[len(comps)-1] == '': toa comps[len(comps)-1]
            total, d = store(size, comps, total, d)
    jaribu:
        display(total, d)
    tatizo IOError kama e:
        ikiwa e.errno != errno.EPIPE:
            raise

eleza store(size, comps, total, d):
    ikiwa comps == []:
        rudisha size, d
    ikiwa comps[0] haiko kwenye d:
        d[comps[0]] = Tupu, {}
    t1, d1 = d[comps[0]]
    d[comps[0]] = store(size, comps[1:], t1, d1)
    rudisha total, d

eleza display(total, d):
    show(total, d, '')

eleza show(total, d, prefix):
    ikiwa sio d: rudisha
    list = []
    sum = 0
    kila key kwenye d.keys():
        tsub, dsub = d[key]
        list.append((tsub, key))
        ikiwa tsub ni sio Tupu: sum = sum + tsub
##  ikiwa sum < total:
##      list.append((total - sum, os.curdir))
    list.sort()
    list.reverse()
    width = len(repr(list[0][0]))
    kila tsub, key kwenye list:
        ikiwa tsub ni Tupu:
            psub = prefix
        isipokua:
            andika(prefix + repr(tsub).rjust(width) + ' ' + key)
            psub = prefix + ' '*(width-1) + '|' + ' '*(len(key)+1)
        ikiwa key kwenye d:
            show(tsub, d[key][1], psub)

ikiwa __name__ == '__main__':
    main()
