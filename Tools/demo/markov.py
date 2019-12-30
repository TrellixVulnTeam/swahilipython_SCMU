#!/usr/bin/env python3

"""
Markov chain simulation of words ama characters.
"""

kundi Markov:
    eleza __init__(self, histsize, choice):
        self.histsize = histsize
        self.choice = choice
        self.trans = {}

    eleza add(self, state, next):
        self.trans.setdefault(state, []).append(next)

    eleza put(self, seq):
        n = self.histsize
        add = self.add
        add(Tupu, seq[:0])
        kila i kwenye range(len(seq)):
            add(seq[max(0, i-n):i], seq[i:i+1])
        add(seq[len(seq)-n:], Tupu)

    eleza get(self):
        choice = self.choice
        trans = self.trans
        n = self.histsize
        seq = choice(trans[Tupu])
        wakati Kweli:
            subseq = seq[max(0, len(seq)-n):]
            options = trans[subseq]
            next = choice(options)
            ikiwa sio next:
                koma
            seq += next
        rudisha seq


eleza test():
    agiza sys, random, getopt
    args = sys.argv[1:]
    jaribu:
        opts, args = getopt.getopt(args, '0123456789cdwq')
    tatizo getopt.error:
        andika('Usage: %s [-#] [-cddqw] [file] ...' % sys.argv[0])
        andika('Options:')
        andika('-#: 1-digit history size (default 2)')
        andika('-c: characters (default)')
        andika('-w: words')
        andika('-d: more debugging output')
        andika('-q: no debugging output')
        andika('Input files (default stdin) are split kwenye paragraphs')
        andika('separated blank lines na each paragraph ni split')
        andika('in words by whitespace, then reconcatenated with')
        andika('exactly one space separating words.')
        andika('Output consists of paragraphs separated by blank')
        andika('lines, where lines are no longer than 72 characters.')
        sys.exit(2)
    histsize = 2
    do_words = Uongo
    debug = 1
    kila o, a kwenye opts:
        ikiwa '-0' <= o <= '-9': histsize = int(o[1:])
        ikiwa o == '-c': do_words = Uongo
        ikiwa o == '-d': debug += 1
        ikiwa o == '-q': debug = 0
        ikiwa o == '-w': do_words = Kweli
    ikiwa sio args:
        args = ['-']

    m = Markov(histsize, random.choice)
    jaribu:
        kila filename kwenye args:
            ikiwa filename == '-':
                f = sys.stdin
                ikiwa f.isatty():
                    andika('Sorry, need stdin kutoka file')
                    endelea
            isipokua:
                f = open(filename, 'r')
            ukijumuisha f:
                ikiwa debug: andika('processing', filename, '...')
                text = f.read()
            paralist = text.split('\n\n')
            kila para kwenye paralist:
                ikiwa debug > 1: andika('feeding ...')
                words = para.split()
                ikiwa words:
                    ikiwa do_words:
                        data = tuple(words)
                    isipokua:
                        data = ' '.join(words)
                    m.put(data)
    tatizo KeyboardInterrupt:
        andika('Interrupted -- endelea ukijumuisha data read so far')
    ikiwa sio m.trans:
        andika('No valid input files')
        rudisha
    ikiwa debug: andika('done.')

    ikiwa debug > 1:
        kila key kwenye m.trans.keys():
            ikiwa key ni Tupu ama len(key) < histsize:
                andika(repr(key), m.trans[key])
        ikiwa histsize == 0: andika(repr(''), m.trans[''])
        andika()
    wakati Kweli:
        data = m.get()
        ikiwa do_words:
            words = data
        isipokua:
            words = data.split()
        n = 0
        limit = 72
        kila w kwenye words:
            ikiwa n + len(w) > limit:
                andika()
                n = 0
            andika(w, end=' ')
            n += len(w) + 1
        andika()
        andika()

ikiwa __name__ == "__main__":
    test()
