"""
Module difflib -- helpers kila computing deltas between objects.

Function get_close_matches(word, possibilities, n=3, cutoff=0.6):
    Use SequenceMatcher to rudisha list of the best "good enough" matches.

Function context_diff(a, b):
    For two lists of strings, rudisha a delta kwenye context diff format.

Function ndiff(a, b):
    Return a delta: the difference between `a` na `b` (lists of strings).

Function restore(delta, which):
    Return one of the two sequences that generated an ndiff delta.

Function unified_diff(a, b):
    For two lists of strings, rudisha a delta kwenye unified diff format.

Class SequenceMatcher:
    A flexible kundi kila comparing pairs of sequences of any type.

Class Differ:
    For producing human-readable deltas kutoka sequences of lines of text.

Class HtmlDiff:
    For producing HTML side by side comparison ukijumuisha change highlights.
"""

__all__ = ['get_close_matches', 'ndiff', 'restore', 'SequenceMatcher',
           'Differ','IS_CHARACTER_JUNK', 'IS_LINE_JUNK', 'context_diff',
           'unified_diff', 'diff_bytes', 'HtmlDiff', 'Match']

kutoka heapq agiza nlargest kama _nlargest
kutoka collections agiza namedtuple kama _namedtuple

Match = _namedtuple('Match', 'a b size')

eleza _calculate_ratio(matches, length):
    ikiwa length:
        rudisha 2.0 * matches / length
    rudisha 1.0

kundi SequenceMatcher:

    """
    SequenceMatcher ni a flexible kundi kila comparing pairs of sequences of
    any type, so long kama the sequence elements are hashable.  The basic
    algorithm predates, na ni a little fancier than, an algorithm
    published kwenye the late 1980's by Ratcliff na Obershelp under the
    hyperbolic name "gestalt pattern matching".  The basic idea ni to find
    the longest contiguous matching subsequence that contains no "junk"
    elements (R-O doesn't address junk).  The same idea ni then applied
    recursively to the pieces of the sequences to the left na to the right
    of the matching subsequence.  This does sio tuma minimal edit
    sequences, but does tend to tuma matches that "look right" to people.

    SequenceMatcher tries to compute a "human-friendly diff" between two
    sequences.  Unlike e.g. UNIX(tm) diff, the fundamental notion ni the
    longest *contiguous* & junk-free matching subsequence.  That's what
    catches peoples' eyes.  The Windows(tm) windiff has another interesting
    notion, pairing up elements that appear uniquely kwenye each sequence.
    That, na the method here, appear to tuma more intuitive difference
    reports than does diff.  This method appears to be the least vulnerable
    to synching up on blocks of "junk lines", though (like blank lines kwenye
    ordinary text files, ama maybe "<P>" lines kwenye HTML files).  That may be
    because this ni the only method of the 3 that has a *concept* of
    "junk" <wink>.

    Example, comparing two strings, na considering blanks to be "junk":

    >>> s = SequenceMatcher(lambda x: x == " ",
    ...                     "private Thread currentThread;",
    ...                     "private volatile Thread currentThread;")
    >>>

    .ratio() returns a float kwenye [0, 1], measuring the "similarity" of the
    sequences.  As a rule of thumb, a .ratio() value over 0.6 means the
    sequences are close matches:

    >>> andika(round(s.ratio(), 3))
    0.866
    >>>

    If you're only interested kwenye where the sequences match,
    .get_matching_blocks() ni handy:

    >>> kila block kwenye s.get_matching_blocks():
    ...     andika("a[%d] na b[%d] match kila %d elements" % block)
    a[0] na b[0] match kila 8 elements
    a[8] na b[17] match kila 21 elements
    a[29] na b[38] match kila 0 elements

    Note that the last tuple returned by .get_matching_blocks() ni always a
    dummy, (len(a), len(b), 0), na this ni the only case kwenye which the last
    tuple element (number of elements matched) ni 0.

    If you want to know how to change the first sequence into the second,
    use .get_opcodes():

    >>> kila opcode kwenye s.get_opcodes():
    ...     andika("%6s a[%d:%d] b[%d:%d]" % opcode)
     equal a[0:8] b[0:8]
    insert a[8:8] b[8:17]
     equal a[8:29] b[17:38]

    See the Differ kundi kila a fancy human-friendly file differencer, which
    uses SequenceMatcher both to compare sequences of lines, na to compare
    sequences of characters within similar (near-matching) lines.

    See also function get_close_matches() kwenye this module, which shows how
    simple code building on SequenceMatcher can be used to do useful work.

    Timing:  Basic R-O ni cubic time worst case na quadratic time expected
    case.  SequenceMatcher ni quadratic time kila the worst case na has
    expected-case behavior dependent kwenye a complicated way on how many
    elements the sequences have kwenye common; best case time ni linear.

    Methods:

    __init__(isjunk=Tupu, a='', b='')
        Construct a SequenceMatcher.

    set_seqs(a, b)
        Set the two sequences to be compared.

    set_seq1(a)
        Set the first sequence to be compared.

    set_seq2(b)
        Set the second sequence to be compared.

    find_longest_match(alo, ahi, blo, bhi)
        Find longest matching block kwenye a[alo:ahi] na b[blo:bhi].

    get_matching_blocks()
        Return list of triples describing matching subsequences.

    get_opcodes()
        Return list of 5-tuples describing how to turn a into b.

    ratio()
        Return a measure of the sequences' similarity (float kwenye [0,1]).

    quick_ratio()
        Return an upper bound on .ratio() relatively quickly.

    real_quick_ratio()
        Return an upper bound on ratio() very quickly.
    """

    eleza __init__(self, isjunk=Tupu, a='', b='', autojunk=Kweli):
        """Construct a SequenceMatcher.

        Optional arg isjunk ni Tupu (the default), ama a one-argument
        function that takes a sequence element na returns true iff the
        element ni junk.  Tupu ni equivalent to pitaing "lambda x: 0", i.e.
        no elements are considered to be junk.  For example, pita
            lambda x: x kwenye " \\t"
        ikiwa you're comparing lines kama sequences of characters, na don't
        want to synch up on blanks ama hard tabs.

        Optional arg a ni the first of two sequences to be compared.  By
        default, an empty string.  The elements of a must be hashable.  See
        also .set_seqs() na .set_seq1().

        Optional arg b ni the second of two sequences to be compared.  By
        default, an empty string.  The elements of b must be hashable. See
        also .set_seqs() na .set_seq2().

        Optional arg autojunk should be set to Uongo to disable the
        "automatic junk heuristic" that treats popular elements kama junk
        (see module documentation kila more information).
        """

        # Members:
        # a
        #      first sequence
        # b
        #      second sequence; differences are computed kama "what do
        #      we need to do to 'a' to change it into 'b'?"
        # b2j
        #      kila x kwenye b, b2j[x] ni a list of the indices (into b)
        #      at which x appears; junk na popular elements do sio appear
        # fullbcount
        #      kila x kwenye b, fullbcount[x] == the number of times x
        #      appears kwenye b; only materialized ikiwa really needed (used
        #      only kila computing quick_ratio())
        # matching_blocks
        #      a list of (i, j, k) triples, where a[i:i+k] == b[j:j+k];
        #      ascending & non-overlapping kwenye i na kwenye j; terminated by
        #      a dummy (len(a), len(b), 0) sentinel
        # opcodes
        #      a list of (tag, i1, i2, j1, j2) tuples, where tag is
        #      one of
        #          'replace'   a[i1:i2] should be replaced by b[j1:j2]
        #          'delete'    a[i1:i2] should be deleted
        #          'insert'    b[j1:j2] should be inserted
        #          'equal'     a[i1:i2] == b[j1:j2]
        # isjunk
        #      a user-supplied function taking a sequence element na
        #      returning true iff the element ni "junk" -- this has
        #      subtle but helpful effects on the algorithm, which I'll
        #      get around to writing up someday <0.9 wink>.
        #      DON'T USE!  Only __chain_b uses this.  Use "in self.bjunk".
        # bjunk
        #      the items kwenye b kila which isjunk ni Kweli.
        # bpopular
        #      nonjunk items kwenye b treated kama junk by the heuristic (ikiwa used).

        self.isjunk = isjunk
        self.a = self.b = Tupu
        self.autojunk = autojunk
        self.set_seqs(a, b)

    eleza set_seqs(self, a, b):
        """Set the two sequences to be compared.

        >>> s = SequenceMatcher()
        >>> s.set_seqs("abcd", "bcde")
        >>> s.ratio()
        0.75
        """

        self.set_seq1(a)
        self.set_seq2(b)

    eleza set_seq1(self, a):
        """Set the first sequence to be compared.

        The second sequence to be compared ni sio changed.

        >>> s = SequenceMatcher(Tupu, "abcd", "bcde")
        >>> s.ratio()
        0.75
        >>> s.set_seq1("bcde")
        >>> s.ratio()
        1.0
        >>>

        SequenceMatcher computes na caches detailed information about the
        second sequence, so ikiwa you want to compare one sequence S against
        many sequences, use .set_seq2(S) once na call .set_seq1(x)
        repeatedly kila each of the other sequences.

        See also set_seqs() na set_seq2().
        """

        ikiwa a ni self.a:
            rudisha
        self.a = a
        self.matching_blocks = self.opcodes = Tupu

    eleza set_seq2(self, b):
        """Set the second sequence to be compared.

        The first sequence to be compared ni sio changed.

        >>> s = SequenceMatcher(Tupu, "abcd", "bcde")
        >>> s.ratio()
        0.75
        >>> s.set_seq2("abcd")
        >>> s.ratio()
        1.0
        >>>

        SequenceMatcher computes na caches detailed information about the
        second sequence, so ikiwa you want to compare one sequence S against
        many sequences, use .set_seq2(S) once na call .set_seq1(x)
        repeatedly kila each of the other sequences.

        See also set_seqs() na set_seq1().
        """

        ikiwa b ni self.b:
            rudisha
        self.b = b
        self.matching_blocks = self.opcodes = Tupu
        self.fullbcount = Tupu
        self.__chain_b()

    # For each element x kwenye b, set b2j[x] to a list of the indices kwenye
    # b where x appears; the indices are kwenye increasing order; note that
    # the number of times x appears kwenye b ni len(b2j[x]) ...
    # when self.isjunk ni defined, junk elements don't show up kwenye this
    # map at all, which stops the central find_longest_match method
    # kutoka starting any matching block at a junk element ...
    # b2j also does sio contain entries kila "popular" elements, meaning
    # elements that account kila more than 1 + 1% of the total elements, na
    # when the sequence ni reasonably large (>= 200 elements); this can
    # be viewed kama an adaptive notion of semi-junk, na tumas an enormous
    # speedup when, e.g., comparing program files ukijumuisha hundreds of
    # instances of "rudisha NULL;" ...
    # note that this ni only called when b changes; so kila cross-product
    # kinds of matches, it's best to call set_seq2 once, then set_seq1
    # repeatedly

    eleza __chain_b(self):
        # Because isjunk ni a user-defined (sio C) function, na we test
        # kila junk a LOT, it's important to minimize the number of calls.
        # Before the tricks described here, __chain_b was by far the most
        # time-consuming routine kwenye the whole module!  If anyone sees
        # Jim Roskind, thank him again kila profile.py -- I never would
        # have guessed that.
        # The first trick ni to build b2j ignoring the possibility
        # of junk.  I.e., we don't call isjunk at all yet.  Throwing
        # out the junk later ni much cheaper than building b2j "right"
        # kutoka the start.
        b = self.b
        self.b2j = b2j = {}

        kila i, elt kwenye enumerate(b):
            indices = b2j.setdefault(elt, [])
            indices.append(i)

        # Purge junk elements
        self.bjunk = junk = set()
        isjunk = self.isjunk
        ikiwa isjunk:
            kila elt kwenye b2j.keys():
                ikiwa isjunk(elt):
                    junk.add(elt)
            kila elt kwenye junk: # separate loop avoids separate list of keys
                toa b2j[elt]

        # Purge popular elements that are sio junk
        self.bpopular = popular = set()
        n = len(b)
        ikiwa self.autojunk na n >= 200:
            ntest = n // 100 + 1
            kila elt, idxs kwenye b2j.items():
                ikiwa len(idxs) > ntest:
                    popular.add(elt)
            kila elt kwenye popular: # ditto; kama fast kila 1% deletion
                toa b2j[elt]

    eleza find_longest_match(self, alo, ahi, blo, bhi):
        """Find longest matching block kwenye a[alo:ahi] na b[blo:bhi].

        If isjunk ni sio defined:

        Return (i,j,k) such that a[i:i+k] ni equal to b[j:j+k], where
            alo <= i <= i+k <= ahi
            blo <= j <= j+k <= bhi
        na kila all (i',j',k') meeting those conditions,
            k >= k'
            i <= i'
            na ikiwa i == i', j <= j'

        In other words, of all maximal matching blocks, rudisha one that
        starts earliest kwenye a, na of all those maximal matching blocks that
        start earliest kwenye a, rudisha the one that starts earliest kwenye b.

        >>> s = SequenceMatcher(Tupu, " abcd", "abcd abcd")
        >>> s.find_longest_match(0, 5, 0, 9)
        Match(a=0, b=4, size=5)

        If isjunk ni defined, first the longest matching block is
        determined kama above, but ukijumuisha the additional restriction that no
        junk element appears kwenye the block.  Then that block ni extended as
        far kama possible by matching (only) junk elements on both sides.  So
        the resulting block never matches on junk tatizo kama identical junk
        happens to be adjacent to an "interesting" match.

        Here's the same example kama before, but considering blanks to be
        junk.  That prevents " abcd" kutoka matching the " abcd" at the tail
        end of the second sequence directly.  Instead only the "abcd" can
        match, na matches the leftmost "abcd" kwenye the second sequence:

        >>> s = SequenceMatcher(lambda x: x==" ", " abcd", "abcd abcd")
        >>> s.find_longest_match(0, 5, 0, 9)
        Match(a=1, b=0, size=4)

        If no blocks match, rudisha (alo, blo, 0).

        >>> s = SequenceMatcher(Tupu, "ab", "c")
        >>> s.find_longest_match(0, 2, 0, 1)
        Match(a=0, b=0, size=0)
        """

        # CAUTION:  stripping common prefix ama suffix would be incorrect.
        # E.g.,
        #    ab
        #    acab
        # Longest matching block ni "ab", but ikiwa common prefix is
        # stripped, it's "a" (tied ukijumuisha "b").  UNIX(tm) diff does so
        # strip, so ends up claiming that ab ni changed to acab by
        # inserting "ca" kwenye the middle.  That's minimal but unintuitive:
        # "it's obvious" that someone inserted "ac" at the front.
        # Windiff ends up at the same place kama diff, but by pairing up
        # the unique 'b's na then matching the first two 'a's.

        a, b, b2j, isbjunk = self.a, self.b, self.b2j, self.bjunk.__contains__
        besti, bestj, bestsize = alo, blo, 0
        # find longest junk-free match
        # during an iteration of the loop, j2len[j] = length of longest
        # junk-free match ending ukijumuisha a[i-1] na b[j]
        j2len = {}
        nothing = []
        kila i kwenye range(alo, ahi):
            # look at all instances of a[i] kwenye b; note that because
            # b2j has no junk keys, the loop ni skipped ikiwa a[i] ni junk
            j2lenget = j2len.get
            newj2len = {}
            kila j kwenye b2j.get(a[i], nothing):
                # a[i] matches b[j]
                ikiwa j < blo:
                    endelea
                ikiwa j >= bhi:
                    koma
                k = newj2len[j] = j2lenget(j-1, 0) + 1
                ikiwa k > bestsize:
                    besti, bestj, bestsize = i-k+1, j-k+1, k
            j2len = newj2len

        # Extend the best by non-junk elements on each end.  In particular,
        # "popular" non-junk elements aren't kwenye b2j, which greatly speeds
        # the inner loop above, but also means "the best" match so far
        # doesn't contain any junk *or* popular non-junk elements.
        wakati besti > alo na bestj > blo na \
              sio isbjunk(b[bestj-1]) na \
              a[besti-1] == b[bestj-1]:
            besti, bestj, bestsize = besti-1, bestj-1, bestsize+1
        wakati besti+bestsize < ahi na bestj+bestsize < bhi na \
              sio isbjunk(b[bestj+bestsize]) na \
              a[besti+bestsize] == b[bestj+bestsize]:
            bestsize += 1

        # Now that we have a wholly interesting match (albeit possibly
        # empty!), we may kama well suck up the matching junk on each
        # side of it too.  Can't think of a good reason sio to, na it
        # saves post-processing the (possibly considerable) expense of
        # figuring out what to do ukijumuisha it.  In the case of an empty
        # interesting match, this ni clearly the right thing to do,
        # because no other kind of match ni possible kwenye the regions.
        wakati besti > alo na bestj > blo na \
              isbjunk(b[bestj-1]) na \
              a[besti-1] == b[bestj-1]:
            besti, bestj, bestsize = besti-1, bestj-1, bestsize+1
        wakati besti+bestsize < ahi na bestj+bestsize < bhi na \
              isbjunk(b[bestj+bestsize]) na \
              a[besti+bestsize] == b[bestj+bestsize]:
            bestsize = bestsize + 1

        rudisha Match(besti, bestj, bestsize)

    eleza get_matching_blocks(self):
        """Return list of triples describing matching subsequences.

        Each triple ni of the form (i, j, n), na means that
        a[i:i+n] == b[j:j+n].  The triples are monotonically increasing kwenye
        i na kwenye j.  New kwenye Python 2.5, it's also guaranteed that if
        (i, j, n) na (i', j', n') are adjacent triples kwenye the list, na
        the second ni sio the last triple kwenye the list, then i+n != i' ama
        j+n != j'.  IOW, adjacent triples never describe adjacent equal
        blocks.

        The last triple ni a dummy, (len(a), len(b), 0), na ni the only
        triple ukijumuisha n==0.

        >>> s = SequenceMatcher(Tupu, "abxcd", "abcd")
        >>> list(s.get_matching_blocks())
        [Match(a=0, b=0, size=2), Match(a=3, b=2, size=2), Match(a=5, b=4, size=0)]
        """

        ikiwa self.matching_blocks ni sio Tupu:
            rudisha self.matching_blocks
        la, lb = len(self.a), len(self.b)

        # This ni most naturally expressed kama a recursive algorithm, but
        # at least one user bumped into extreme use cases that exceeded
        # the recursion limit on their box.  So, now we maintain a list
        # ('queue`) of blocks we still need to look at, na append partial
        # results to `matching_blocks` kwenye a loop; the matches are sorted
        # at the end.
        queue = [(0, la, 0, lb)]
        matching_blocks = []
        wakati queue:
            alo, ahi, blo, bhi = queue.pop()
            i, j, k = x = self.find_longest_match(alo, ahi, blo, bhi)
            # a[alo:i] vs b[blo:j] unknown
            # a[i:i+k] same kama b[j:j+k]
            # a[i+k:ahi] vs b[j+k:bhi] unknown
            ikiwa k:   # ikiwa k ni 0, there was no matching block
                matching_blocks.append(x)
                ikiwa alo < i na blo < j:
                    queue.append((alo, i, blo, j))
                ikiwa i+k < ahi na j+k < bhi:
                    queue.append((i+k, ahi, j+k, bhi))
        matching_blocks.sort()

        # It's possible that we have adjacent equal blocks kwenye the
        # matching_blocks list now.  Starting ukijumuisha 2.5, this code was added
        # to collapse them.
        i1 = j1 = k1 = 0
        non_adjacent = []
        kila i2, j2, k2 kwenye matching_blocks:
            # Is this block adjacent to i1, j1, k1?
            ikiwa i1 + k1 == i2 na j1 + k1 == j2:
                # Yes, so collapse them -- this just increases the length of
                # the first block by the length of the second, na the first
                # block so lengthened remains the block to compare against.
                k1 += k2
            isipokua:
                # Not adjacent.  Remember the first block (k1==0 means it's
                # the dummy we started with), na make the second block the
                # new block to compare against.
                ikiwa k1:
                    non_adjacent.append((i1, j1, k1))
                i1, j1, k1 = i2, j2, k2
        ikiwa k1:
            non_adjacent.append((i1, j1, k1))

        non_adjacent.append( (la, lb, 0) )
        self.matching_blocks = list(map(Match._make, non_adjacent))
        rudisha self.matching_blocks

    eleza get_opcodes(self):
        """Return list of 5-tuples describing how to turn a into b.

        Each tuple ni of the form (tag, i1, i2, j1, j2).  The first tuple
        has i1 == j1 == 0, na remaining tuples have i1 == the i2 kutoka the
        tuple preceding it, na likewise kila j1 == the previous j2.

        The tags are strings, ukijumuisha these meanings:

        'replace':  a[i1:i2] should be replaced by b[j1:j2]
        'delete':   a[i1:i2] should be deleted.
                    Note that j1==j2 kwenye this case.
        'insert':   b[j1:j2] should be inserted at a[i1:i1].
                    Note that i1==i2 kwenye this case.
        'equal':    a[i1:i2] == b[j1:j2]

        >>> a = "qabxcd"
        >>> b = "abycdf"
        >>> s = SequenceMatcher(Tupu, a, b)
        >>> kila tag, i1, i2, j1, j2 kwenye s.get_opcodes():
        ...    andika(("%7s a[%d:%d] (%s) b[%d:%d] (%s)" %
        ...           (tag, i1, i2, a[i1:i2], j1, j2, b[j1:j2])))
         delete a[0:1] (q) b[0:0] ()
          equal a[1:3] (ab) b[0:2] (ab)
        replace a[3:4] (x) b[2:3] (y)
          equal a[4:6] (cd) b[3:5] (cd)
         insert a[6:6] () b[5:6] (f)
        """

        ikiwa self.opcodes ni sio Tupu:
            rudisha self.opcodes
        i = j = 0
        self.opcodes = answer = []
        kila ai, bj, size kwenye self.get_matching_blocks():
            # invariant:  we've pumped out correct diffs to change
            # a[:i] into b[:j], na the next matching block is
            # a[ai:ai+size] == b[bj:bj+size].  So we need to pump
            # out a diff to change a[i:ai] into b[j:bj], pump out
            # the matching block, na move (i,j) beyond the match
            tag = ''
            ikiwa i < ai na j < bj:
                tag = 'replace'
            lasivyo i < ai:
                tag = 'delete'
            lasivyo j < bj:
                tag = 'insert'
            ikiwa tag:
                answer.append( (tag, i, ai, j, bj) )
            i, j = ai+size, bj+size
            # the list of matching blocks ni terminated by a
            # sentinel ukijumuisha size 0
            ikiwa size:
                answer.append( ('equal', ai, i, bj, j) )
        rudisha answer

    eleza get_grouped_opcodes(self, n=3):
        """ Isolate change clusters by eliminating ranges ukijumuisha no changes.

        Return a generator of groups ukijumuisha up to n lines of context.
        Each group ni kwenye the same format kama returned by get_opcodes().

        >>> kutoka pprint agiza pprint
        >>> a = list(map(str, range(1,40)))
        >>> b = a[:]
        >>> b[8:8] = ['i']     # Make an insertion
        >>> b[20] += 'x'       # Make a replacement
        >>> b[23:28] = []      # Make a deletion
        >>> b[30] += 'y'       # Make another replacement
        >>> pandika(list(SequenceMatcher(Tupu,a,b).get_grouped_opcodes()))
        [[('equal', 5, 8, 5, 8), ('insert', 8, 8, 8, 9), ('equal', 8, 11, 9, 12)],
         [('equal', 16, 19, 17, 20),
          ('replace', 19, 20, 20, 21),
          ('equal', 20, 22, 21, 23),
          ('delete', 22, 27, 23, 23),
          ('equal', 27, 30, 23, 26)],
         [('equal', 31, 34, 27, 30),
          ('replace', 34, 35, 30, 31),
          ('equal', 35, 38, 31, 34)]]
        """

        codes = self.get_opcodes()
        ikiwa sio codes:
            codes = [("equal", 0, 1, 0, 1)]
        # Fixup leading na trailing groups ikiwa they show no changes.
        ikiwa codes[0][0] == 'equal':
            tag, i1, i2, j1, j2 = codes[0]
            codes[0] = tag, max(i1, i2-n), i2, max(j1, j2-n), j2
        ikiwa codes[-1][0] == 'equal':
            tag, i1, i2, j1, j2 = codes[-1]
            codes[-1] = tag, i1, min(i2, i1+n), j1, min(j2, j1+n)

        nn = n + n
        group = []
        kila tag, i1, i2, j1, j2 kwenye codes:
            # End the current group na start a new one whenever
            # there ni a large range ukijumuisha no changes.
            ikiwa tag == 'equal' na i2-i1 > nn:
                group.append((tag, i1, min(i2, i1+n), j1, min(j2, j1+n)))
                tuma group
                group = []
                i1, j1 = max(i1, i2-n), max(j1, j2-n)
            group.append((tag, i1, i2, j1 ,j2))
        ikiwa group na sio (len(group)==1 na group[0][0] == 'equal'):
            tuma group

    eleza ratio(self):
        """Return a measure of the sequences' similarity (float kwenye [0,1]).

        Where T ni the total number of elements kwenye both sequences, na
        M ni the number of matches, this ni 2.0*M / T.
        Note that this ni 1 ikiwa the sequences are identical, na 0 if
        they have nothing kwenye common.

        .ratio() ni expensive to compute ikiwa you haven't already computed
        .get_matching_blocks() ama .get_opcodes(), kwenye which case you may
        want to try .quick_ratio() ama .real_quick_ratio() first to get an
        upper bound.

        >>> s = SequenceMatcher(Tupu, "abcd", "bcde")
        >>> s.ratio()
        0.75
        >>> s.quick_ratio()
        0.75
        >>> s.real_quick_ratio()
        1.0
        """

        matches = sum(triple[-1] kila triple kwenye self.get_matching_blocks())
        rudisha _calculate_ratio(matches, len(self.a) + len(self.b))

    eleza quick_ratio(self):
        """Return an upper bound on ratio() relatively quickly.

        This isn't defined beyond that it ni an upper bound on .ratio(), na
        ni faster to compute.
        """

        # viewing a na b kama multisets, set matches to the cardinality
        # of their intersection; this counts the number of matches
        # without regard to order, so ni clearly an upper bound
        ikiwa self.fullbcount ni Tupu:
            self.fullbcount = fullbcount = {}
            kila elt kwenye self.b:
                fullbcount[elt] = fullbcount.get(elt, 0) + 1
        fullbcount = self.fullbcount
        # avail[x] ni the number of times x appears kwenye 'b' less the
        # number of times we've seen it kwenye 'a' so far ... kinda
        avail = {}
        availhas, matches = avail.__contains__, 0
        kila elt kwenye self.a:
            ikiwa availhas(elt):
                numb = avail[elt]
            isipokua:
                numb = fullbcount.get(elt, 0)
            avail[elt] = numb - 1
            ikiwa numb > 0:
                matches = matches + 1
        rudisha _calculate_ratio(matches, len(self.a) + len(self.b))

    eleza real_quick_ratio(self):
        """Return an upper bound on ratio() very quickly.

        This isn't defined beyond that it ni an upper bound on .ratio(), na
        ni faster to compute than either .ratio() ama .quick_ratio().
        """

        la, lb = len(self.a), len(self.b)
        # can't have more matches than the number of elements kwenye the
        # shorter sequence
        rudisha _calculate_ratio(min(la, lb), la + lb)

eleza get_close_matches(word, possibilities, n=3, cutoff=0.6):
    """Use SequenceMatcher to rudisha list of the best "good enough" matches.

    word ni a sequence kila which close matches are desired (typically a
    string).

    possibilities ni a list of sequences against which to match word
    (typically a list of strings).

    Optional arg n (default 3) ni the maximum number of close matches to
    return.  n must be > 0.

    Optional arg cutoff (default 0.6) ni a float kwenye [0, 1].  Possibilities
    that don't score at least that similar to word are ignored.

    The best (no more than n) matches among the possibilities are returned
    kwenye a list, sorted by similarity score, most similar first.

    >>> get_close_matches("appel", ["ape", "apple", "peach", "puppy"])
    ['apple', 'ape']
    >>> agiza keyword kama _keyword
    >>> get_close_matches("wheel", _keyword.kwlist)
    ['while']
    >>> get_close_matches("Apple", _keyword.kwlist)
    []
    >>> get_close_matches("accept", _keyword.kwlist)
    ['except']
    """

    ikiwa sio n >  0:
        ashiria ValueError("n must be > 0: %r" % (n,))
    ikiwa sio 0.0 <= cutoff <= 1.0:
        ashiria ValueError("cutoff must be kwenye [0.0, 1.0]: %r" % (cutoff,))
    result = []
    s = SequenceMatcher()
    s.set_seq2(word)
    kila x kwenye possibilities:
        s.set_seq1(x)
        ikiwa s.real_quick_ratio() >= cutoff na \
           s.quick_ratio() >= cutoff na \
           s.ratio() >= cutoff:
            result.append((s.ratio(), x))

    # Move the best scorers to head of list
    result = _nlargest(n, result)
    # Strip scores kila the best n matches
    rudisha [x kila score, x kwenye result]


eleza _keep_original_ws(s, tag_s):
    """Replace whitespace ukijumuisha the original whitespace characters kwenye `s`"""
    rudisha ''.join(
        c ikiwa tag_c == " " na c.isspace() isipokua tag_c
        kila c, tag_c kwenye zip(s, tag_s)
    )



kundi Differ:
    r"""
    Differ ni a kundi kila comparing sequences of lines of text, na
    producing human-readable differences ama deltas.  Differ uses
    SequenceMatcher both to compare sequences of lines, na to compare
    sequences of characters within similar (near-matching) lines.

    Each line of a Differ delta begins ukijumuisha a two-letter code:

        '- '    line unique to sequence 1
        '+ '    line unique to sequence 2
        '  '    line common to both sequences
        '? '    line sio present kwenye either input sequence

    Lines beginning ukijumuisha '? ' attempt to guide the eye to intraline
    differences, na were sio present kwenye either input sequence.  These lines
    can be confusing ikiwa the sequences contain tab characters.

    Note that Differ makes no claim to produce a *minimal* diff.  To the
    contrary, minimal diffs are often counter-intuitive, because they synch
    up anywhere possible, sometimes accidental matches 100 pages apart.
    Restricting synch points to contiguous matches preserves some notion of
    locality, at the occasional cost of producing a longer diff.

    Example: Comparing two texts.

    First we set up the texts, sequences of individual single-line strings
    ending ukijumuisha newlines (such sequences can also be obtained kutoka the
    `readlines()` method of file-like objects):

    >>> text1 = '''  1. Beautiful ni better than ugly.
    ...   2. Explicit ni better than implicit.
    ...   3. Simple ni better than complex.
    ...   4. Complex ni better than complicated.
    ... '''.splitlines(keepends=Kweli)
    >>> len(text1)
    4
    >>> text1[0][-1]
    '\n'
    >>> text2 = '''  1. Beautiful ni better than ugly.
    ...   3.   Simple ni better than complex.
    ...   4. Complicated ni better than complex.
    ...   5. Flat ni better than nested.
    ... '''.splitlines(keepends=Kweli)

    Next we instantiate a Differ object:

    >>> d = Differ()

    Note that when instantiating a Differ object we may pita functions to
    filter out line na character 'junk'.  See Differ.__init__ kila details.

    Finally, we compare the two:

    >>> result = list(d.compare(text1, text2))

    'result' ni a list of strings, so let's pretty-print it:

    >>> kutoka pprint agiza pprint kama _pprint
    >>> _pandika(result)
    ['    1. Beautiful ni better than ugly.\n',
     '-   2. Explicit ni better than implicit.\n',
     '-   3. Simple ni better than complex.\n',
     '+   3.   Simple ni better than complex.\n',
     '?     ++\n',
     '-   4. Complex ni better than complicated.\n',
     '?            ^                     ---- ^\n',
     '+   4. Complicated ni better than complex.\n',
     '?           ++++ ^                      ^\n',
     '+   5. Flat ni better than nested.\n']

    As a single multi-line string it looks like this:

    >>> andika(''.join(result), end="")
        1. Beautiful ni better than ugly.
    -   2. Explicit ni better than implicit.
    -   3. Simple ni better than complex.
    +   3.   Simple ni better than complex.
    ?     ++
    -   4. Complex ni better than complicated.
    ?            ^                     ---- ^
    +   4. Complicated ni better than complex.
    ?           ++++ ^                      ^
    +   5. Flat ni better than nested.

    Methods:

    __init__(linejunk=Tupu, charjunk=Tupu)
        Construct a text differencer, ukijumuisha optional filters.

    compare(a, b)
        Compare two sequences of lines; generate the resulting delta.
    """

    eleza __init__(self, linejunk=Tupu, charjunk=Tupu):
        """
        Construct a text differencer, ukijumuisha optional filters.

        The two optional keyword parameters are kila filter functions:

        - `linejunk`: A function that should accept a single string argument,
          na rudisha true iff the string ni junk. The module-level function
          `IS_LINE_JUNK` may be used to filter out lines without visible
          characters, tatizo kila at most one splat ('#').  It ni recommended
          to leave linejunk Tupu; the underlying SequenceMatcher kundi has
          an adaptive notion of "noise" lines that's better than any static
          definition the author has ever been able to craft.

        - `charjunk`: A function that should accept a string of length 1. The
          module-level function `IS_CHARACTER_JUNK` may be used to filter out
          whitespace characters (a blank ama tab; **note**: bad idea to include
          newline kwenye this!).  Use of IS_CHARACTER_JUNK ni recommended.
        """

        self.linejunk = linejunk
        self.charjunk = charjunk

    eleza compare(self, a, b):
        r"""
        Compare two sequences of lines; generate the resulting delta.

        Each sequence must contain individual single-line strings ending with
        newlines. Such sequences can be obtained kutoka the `readlines()` method
        of file-like objects.  The delta generated also consists of newline-
        terminated strings, ready to be printed as-is via the writeline()
        method of a file-like object.

        Example:

        >>> andika(''.join(Differ().compare('one\ntwo\nthree\n'.splitlines(Kweli),
        ...                                'ore\ntree\nemu\n'.splitlines(Kweli))),
        ...       end="")
        - one
        ?  ^
        + ore
        ?  ^
        - two
        - three
        ?  -
        + tree
        + emu
        """

        cruncher = SequenceMatcher(self.linejunk, a, b)
        kila tag, alo, ahi, blo, bhi kwenye cruncher.get_opcodes():
            ikiwa tag == 'replace':
                g = self._fancy_replace(a, alo, ahi, b, blo, bhi)
            lasivyo tag == 'delete':
                g = self._dump('-', a, alo, ahi)
            lasivyo tag == 'insert':
                g = self._dump('+', b, blo, bhi)
            lasivyo tag == 'equal':
                g = self._dump(' ', a, alo, ahi)
            isipokua:
                ashiria ValueError('unknown tag %r' % (tag,))

            tuma kutoka g

    eleza _dump(self, tag, x, lo, hi):
        """Generate comparison results kila a same-tagged range."""
        kila i kwenye range(lo, hi):
            tuma '%s %s' % (tag, x[i])

    eleza _plain_replace(self, a, alo, ahi, b, blo, bhi):
        assert alo < ahi na blo < bhi
        # dump the shorter block first -- reduces the burden on short-term
        # memory ikiwa the blocks are of very different sizes
        ikiwa bhi - blo < ahi - alo:
            first  = self._dump('+', b, blo, bhi)
            second = self._dump('-', a, alo, ahi)
        isipokua:
            first  = self._dump('-', a, alo, ahi)
            second = self._dump('+', b, blo, bhi)

        kila g kwenye first, second:
            tuma kutoka g

    eleza _fancy_replace(self, a, alo, ahi, b, blo, bhi):
        r"""
        When replacing one block of lines ukijumuisha another, search the blocks
        kila *similar* lines; the best-matching pair (ikiwa any) ni used kama a
        synch point, na intraline difference marking ni done on the
        similar pair. Lots of work, but often worth it.

        Example:

        >>> d = Differ()
        >>> results = d._fancy_replace(['abcDefghiJkl\n'], 0, 1,
        ...                            ['abcdefGhijkl\n'], 0, 1)
        >>> andika(''.join(results), end="")
        - abcDefghiJkl
        ?    ^  ^  ^
        + abcdefGhijkl
        ?    ^  ^  ^
        """

        # don't synch up unless the lines have a similarity score of at
        # least cutoff; best_ratio tracks the best score seen so far
        best_ratio, cutoff = 0.74, 0.75
        cruncher = SequenceMatcher(self.charjunk)
        eqi, eqj = Tupu, Tupu   # 1st indices of equal lines (ikiwa any)

        # search kila the pair that matches best without being identical
        # (identical lines must be junk lines, & we don't want to synch up
        # on junk -- unless we have to)
        kila j kwenye range(blo, bhi):
            bj = b[j]
            cruncher.set_seq2(bj)
            kila i kwenye range(alo, ahi):
                ai = a[i]
                ikiwa ai == bj:
                    ikiwa eqi ni Tupu:
                        eqi, eqj = i, j
                    endelea
                cruncher.set_seq1(ai)
                # computing similarity ni expensive, so use the quick
                # upper bounds first -- have seen this speed up messy
                # compares by a factor of 3.
                # note that ratio() ni only expensive to compute the first
                # time it's called on a sequence pair; the expensive part
                # of the computation ni cached by cruncher
                ikiwa cruncher.real_quick_ratio() > best_ratio na \
                      cruncher.quick_ratio() > best_ratio na \
                      cruncher.ratio() > best_ratio:
                    best_ratio, best_i, best_j = cruncher.ratio(), i, j
        ikiwa best_ratio < cutoff:
            # no non-identical "pretty close" pair
            ikiwa eqi ni Tupu:
                # no identical pair either -- treat it kama a straight replace
                tuma kutoka self._plain_replace(a, alo, ahi, b, blo, bhi)
                rudisha
            # no close pair, but an identical pair -- synch up on that
            best_i, best_j, best_ratio = eqi, eqj, 1.0
        isipokua:
            # there's a close pair, so forget the identical pair (ikiwa any)
            eqi = Tupu

        # a[best_i] very similar to b[best_j]; eqi ni Tupu iff they're sio
        # identical

        # pump out diffs kutoka before the synch point
        tuma kutoka self._fancy_helper(a, alo, best_i, b, blo, best_j)

        # do intraline marking on the synch pair
        aelt, belt = a[best_i], b[best_j]
        ikiwa eqi ni Tupu:
            # pump out a '-', '?', '+', '?' quad kila the synched lines
            atags = btags = ""
            cruncher.set_seqs(aelt, belt)
            kila tag, ai1, ai2, bj1, bj2 kwenye cruncher.get_opcodes():
                la, lb = ai2 - ai1, bj2 - bj1
                ikiwa tag == 'replace':
                    atags += '^' * la
                    btags += '^' * lb
                lasivyo tag == 'delete':
                    atags += '-' * la
                lasivyo tag == 'insert':
                    btags += '+' * lb
                lasivyo tag == 'equal':
                    atags += ' ' * la
                    btags += ' ' * lb
                isipokua:
                    ashiria ValueError('unknown tag %r' % (tag,))
            tuma kutoka self._qformat(aelt, belt, atags, btags)
        isipokua:
            # the synch pair ni identical
            tuma '  ' + aelt

        # pump out diffs kutoka after the synch point
        tuma kutoka self._fancy_helper(a, best_i+1, ahi, b, best_j+1, bhi)

    eleza _fancy_helper(self, a, alo, ahi, b, blo, bhi):
        g = []
        ikiwa alo < ahi:
            ikiwa blo < bhi:
                g = self._fancy_replace(a, alo, ahi, b, blo, bhi)
            isipokua:
                g = self._dump('-', a, alo, ahi)
        lasivyo blo < bhi:
            g = self._dump('+', b, blo, bhi)

        tuma kutoka g

    eleza _qformat(self, aline, bline, atags, btags):
        r"""
        Format "?" output na deal ukijumuisha tabs.

        Example:

        >>> d = Differ()
        >>> results = d._qformat('\tabcDefghiJkl\n', '\tabcdefGhijkl\n',
        ...                      '  ^ ^  ^      ', '  ^ ^  ^      ')
        >>> kila line kwenye results: andika(repr(line))
        ...
        '- \tabcDefghiJkl\n'
        '? \t ^ ^  ^\n'
        '+ \tabcdefGhijkl\n'
        '? \t ^ ^  ^\n'
        """
        atags = _keep_original_ws(aline, atags).rstrip()
        btags = _keep_original_ws(bline, btags).rstrip()

        tuma "- " + aline
        ikiwa atags:
            tuma f"? {atags}\n"

        tuma "+ " + bline
        ikiwa btags:
            tuma f"? {btags}\n"

# With respect to junk, an earlier version of ndiff simply refused to
# *start* a match ukijumuisha a junk element.  The result was cases like this:
#     before: private Thread currentThread;
#     after:  private volatile Thread currentThread;
# If you consider whitespace to be junk, the longest contiguous match
# sio starting ukijumuisha junk ni "e Thread currentThread".  So ndiff reported
# that "e volatil" was inserted between the 't' na the 'e' kwenye "private".
# While an accurate view, to people that's absurd.  The current version
# looks kila matching blocks that are entirely junk-free, then extends the
# longest one of those kama far kama possible but only ukijumuisha matching junk.
# So now "currentThread" ni matched, then extended to suck up the
# preceding blank; then "private" ni matched, na extended to suck up the
# following blank; then "Thread" ni matched; na finally ndiff reports
# that "volatile " was inserted before "Thread".  The only quibble
# remaining ni that perhaps it was really the case that " volatile"
# was inserted after "private".  I can live ukijumuisha that <wink>.

agiza re

eleza IS_LINE_JUNK(line, pat=re.compile(r"\s*(?:#\s*)?$").match):
    r"""
    Return 1 kila ignorable line: iff `line` ni blank ama contains a single '#'.

    Examples:

    >>> IS_LINE_JUNK('\n')
    Kweli
    >>> IS_LINE_JUNK('  #   \n')
    Kweli
    >>> IS_LINE_JUNK('hello\n')
    Uongo
    """

    rudisha pat(line) ni sio Tupu

eleza IS_CHARACTER_JUNK(ch, ws=" \t"):
    r"""
    Return 1 kila ignorable character: iff `ch` ni a space ama tab.

    Examples:

    >>> IS_CHARACTER_JUNK(' ')
    Kweli
    >>> IS_CHARACTER_JUNK('\t')
    Kweli
    >>> IS_CHARACTER_JUNK('\n')
    Uongo
    >>> IS_CHARACTER_JUNK('x')
    Uongo
    """

    rudisha ch kwenye ws


########################################################################
###  Unified Diff
########################################################################

eleza _format_range_unified(start, stop):
    'Convert range to the "ed" format'
    # Per the diff spec at http://www.unix.org/single_unix_specification/
    beginning = start + 1     # lines start numbering ukijumuisha one
    length = stop - start
    ikiwa length == 1:
        rudisha '{}'.format(beginning)
    ikiwa sio length:
        beginning -= 1        # empty ranges begin at line just before the range
    rudisha '{},{}'.format(beginning, length)

eleza unified_diff(a, b, fromfile='', tofile='', fromfiledate='',
                 tofiledate='', n=3, lineterm='\n'):
    r"""
    Compare two sequences of lines; generate the delta kama a unified diff.

    Unified diffs are a compact way of showing line changes na a few
    lines of context.  The number of context lines ni set by 'n' which
    defaults to three.

    By default, the diff control lines (those ukijumuisha ---, +++, ama @@) are
    created ukijumuisha a trailing newline.  This ni helpful so that inputs
    created kutoka file.readlines() result kwenye diffs that are suitable for
    file.writelines() since both the inputs na outputs have trailing
    newlines.

    For inputs that do sio have trailing newlines, set the lineterm
    argument to "" so that the output will be uniformly newline free.

    The unidiff format normally has a header kila filenames na modification
    times.  Any ama all of these may be specified using strings for
    'fromfile', 'tofile', 'fromfiledate', na 'tofiledate'.
    The modification times are normally expressed kwenye the ISO 8601 format.

    Example:

    >>> kila line kwenye unified_diff('one two three four'.split(),
    ...             'zero one tree four'.split(), 'Original', 'Current',
    ...             '2005-01-26 23:30:50', '2010-04-02 10:20:52',
    ...             lineterm=''):
    ...     andika(line)                 # doctest: +NORMALIZE_WHITESPACE
    --- Original        2005-01-26 23:30:50
    +++ Current         2010-04-02 10:20:52
    @@ -1,4 +1,4 @@
    +zero
     one
    -two
    -three
    +tree
     four
    """

    _check_types(a, b, fromfile, tofile, fromfiledate, tofiledate, lineterm)
    started = Uongo
    kila group kwenye SequenceMatcher(Tupu,a,b).get_grouped_opcodes(n):
        ikiwa sio started:
            started = Kweli
            fromdate = '\t{}'.format(fromfiledate) ikiwa fromfiledate isipokua ''
            todate = '\t{}'.format(tofiledate) ikiwa tofiledate isipokua ''
            tuma '--- {}{}{}'.format(fromfile, fromdate, lineterm)
            tuma '+++ {}{}{}'.format(tofile, todate, lineterm)

        first, last = group[0], group[-1]
        file1_range = _format_range_unified(first[1], last[2])
        file2_range = _format_range_unified(first[3], last[4])
        tuma '@@ -{} +{} @@{}'.format(file1_range, file2_range, lineterm)

        kila tag, i1, i2, j1, j2 kwenye group:
            ikiwa tag == 'equal':
                kila line kwenye a[i1:i2]:
                    tuma ' ' + line
                endelea
            ikiwa tag kwenye {'replace', 'delete'}:
                kila line kwenye a[i1:i2]:
                    tuma '-' + line
            ikiwa tag kwenye {'replace', 'insert'}:
                kila line kwenye b[j1:j2]:
                    tuma '+' + line


########################################################################
###  Context Diff
########################################################################

eleza _format_range_context(start, stop):
    'Convert range to the "ed" format'
    # Per the diff spec at http://www.unix.org/single_unix_specification/
    beginning = start + 1     # lines start numbering ukijumuisha one
    length = stop - start
    ikiwa sio length:
        beginning -= 1        # empty ranges begin at line just before the range
    ikiwa length <= 1:
        rudisha '{}'.format(beginning)
    rudisha '{},{}'.format(beginning, beginning + length - 1)

# See http://www.unix.org/single_unix_specification/
eleza context_diff(a, b, fromfile='', tofile='',
                 fromfiledate='', tofiledate='', n=3, lineterm='\n'):
    r"""
    Compare two sequences of lines; generate the delta kama a context diff.

    Context diffs are a compact way of showing line changes na a few
    lines of context.  The number of context lines ni set by 'n' which
    defaults to three.

    By default, the diff control lines (those ukijumuisha *** ama ---) are
    created ukijumuisha a trailing newline.  This ni helpful so that inputs
    created kutoka file.readlines() result kwenye diffs that are suitable for
    file.writelines() since both the inputs na outputs have trailing
    newlines.

    For inputs that do sio have trailing newlines, set the lineterm
    argument to "" so that the output will be uniformly newline free.

    The context diff format normally has a header kila filenames na
    modification times.  Any ama all of these may be specified using
    strings kila 'fromfile', 'tofile', 'fromfiledate', na 'tofiledate'.
    The modification times are normally expressed kwenye the ISO 8601 format.
    If sio specified, the strings default to blanks.

    Example:

    >>> andika(''.join(context_diff('one\ntwo\nthree\nfour\n'.splitlines(Kweli),
    ...       'zero\none\ntree\nfour\n'.splitlines(Kweli), 'Original', 'Current')),
    ...       end="")
    *** Original
    --- Current
    ***************
    *** 1,4 ****
      one
    ! two
    ! three
      four
    --- 1,4 ----
    + zero
      one
    ! tree
      four
    """

    _check_types(a, b, fromfile, tofile, fromfiledate, tofiledate, lineterm)
    prefix = dict(insert='+ ', delete='- ', replace='! ', equal='  ')
    started = Uongo
    kila group kwenye SequenceMatcher(Tupu,a,b).get_grouped_opcodes(n):
        ikiwa sio started:
            started = Kweli
            fromdate = '\t{}'.format(fromfiledate) ikiwa fromfiledate isipokua ''
            todate = '\t{}'.format(tofiledate) ikiwa tofiledate isipokua ''
            tuma '*** {}{}{}'.format(fromfile, fromdate, lineterm)
            tuma '--- {}{}{}'.format(tofile, todate, lineterm)

        first, last = group[0], group[-1]
        tuma '***************' + lineterm

        file1_range = _format_range_context(first[1], last[2])
        tuma '*** {} ****{}'.format(file1_range, lineterm)

        ikiwa any(tag kwenye {'replace', 'delete'} kila tag, _, _, _, _ kwenye group):
            kila tag, i1, i2, _, _ kwenye group:
                ikiwa tag != 'insert':
                    kila line kwenye a[i1:i2]:
                        tuma prefix[tag] + line

        file2_range = _format_range_context(first[3], last[4])
        tuma '--- {} ----{}'.format(file2_range, lineterm)

        ikiwa any(tag kwenye {'replace', 'insert'} kila tag, _, _, _, _ kwenye group):
            kila tag, _, _, j1, j2 kwenye group:
                ikiwa tag != 'delete':
                    kila line kwenye b[j1:j2]:
                        tuma prefix[tag] + line

eleza _check_types(a, b, *args):
    # Checking types ni weird, but the alternative ni garbled output when
    # someone pitaes mixed bytes na str to {unified,context}_diff(). E.g.
    # without this check, pitaing filenames kama bytes results kwenye output like
    #   --- b'oldfile.txt'
    #   +++ b'newfile.txt'
    # because of how str.format() incorporates bytes objects.
    ikiwa a na sio isinstance(a[0], str):
        ashiria TypeError('lines to compare must be str, sio %s (%r)' %
                        (type(a[0]).__name__, a[0]))
    ikiwa b na sio isinstance(b[0], str):
        ashiria TypeError('lines to compare must be str, sio %s (%r)' %
                        (type(b[0]).__name__, b[0]))
    kila arg kwenye args:
        ikiwa sio isinstance(arg, str):
            ashiria TypeError('all arguments must be str, not: %r' % (arg,))

eleza diff_bytes(dfunc, a, b, fromfile=b'', tofile=b'',
               fromfiledate=b'', tofiledate=b'', n=3, lineterm=b'\n'):
    r"""
    Compare `a` na `b`, two sequences of lines represented kama bytes rather
    than str. This ni a wrapper kila `dfunc`, which ni typically either
    unified_diff() ama context_diff(). Inputs are losslessly converted to
    strings so that `dfunc` only has to worry about strings, na encoded
    back to bytes on return. This ni necessary to compare files with
    unknown ama inconsistent encoding. All other inputs (tatizo `n`) must be
    bytes rather than str.
    """
    eleza decode(s):
        jaribu:
            rudisha s.decode('ascii', 'surrogateescape')
        tatizo AttributeError kama err:
            msg = ('all arguments must be bytes, sio %s (%r)' %
                   (type(s).__name__, s))
            ashiria TypeError(msg) kutoka err
    a = list(map(decode, a))
    b = list(map(decode, b))
    fromfile = decode(fromfile)
    tofile = decode(tofile)
    fromfiledate = decode(fromfiledate)
    tofiledate = decode(tofiledate)
    lineterm = decode(lineterm)

    lines = dfunc(a, b, fromfile, tofile, fromfiledate, tofiledate, n, lineterm)
    kila line kwenye lines:
        tuma line.encode('ascii', 'surrogateescape')

eleza ndiff(a, b, linejunk=Tupu, charjunk=IS_CHARACTER_JUNK):
    r"""
    Compare `a` na `b` (lists of strings); rudisha a `Differ`-style delta.

    Optional keyword parameters `linejunk` na `charjunk` are kila filter
    functions, ama can be Tupu:

    - linejunk: A function that should accept a single string argument na
      rudisha true iff the string ni junk.  The default ni Tupu, na is
      recommended; the underlying SequenceMatcher kundi has an adaptive
      notion of "noise" lines.

    - charjunk: A function that accepts a character (string of length
      1), na returns true iff the character ni junk. The default is
      the module-level function IS_CHARACTER_JUNK, which filters out
      whitespace characters (a blank ama tab; note: it's a bad idea to
      include newline kwenye this!).

    Tools/scripts/ndiff.py ni a command-line front-end to this function.

    Example:

    >>> diff = ndiff('one\ntwo\nthree\n'.splitlines(keepends=Kweli),
    ...              'ore\ntree\nemu\n'.splitlines(keepends=Kweli))
    >>> andika(''.join(diff), end="")
    - one
    ?  ^
    + ore
    ?  ^
    - two
    - three
    ?  -
    + tree
    + emu
    """
    rudisha Differ(linejunk, charjunk).compare(a, b)

eleza _mdiff(fromlines, tolines, context=Tupu, linejunk=Tupu,
           charjunk=IS_CHARACTER_JUNK):
    r"""Returns generator tumaing marked up from/to side by side differences.

    Arguments:
    fromlines -- list of text lines to compared to tolines
    tolines -- list of text lines to be compared to fromlines
    context -- number of context lines to display on each side of difference,
               ikiwa Tupu, all from/to text lines will be generated.
    linejunk -- pitaed on to ndiff (see ndiff documentation)
    charjunk -- pitaed on to ndiff (see ndiff documentation)

    This function returns an iterator which returns a tuple:
    (kutoka line tuple, to line tuple, boolean flag)

    from/to line tuple -- (line num, line text)
        line num -- integer ama Tupu (to indicate a context separation)
        line text -- original line text ukijumuisha following markers inserted:
            '\0+' -- marks start of added text
            '\0-' -- marks start of deleted text
            '\0^' -- marks start of changed text
            '\1' -- marks end of added/deleted/changed text

    boolean flag -- Tupu indicates context separation, Kweli indicates
        either "from" ama "to" line contains a change, otherwise Uongo.

    This function/iterator was originally developed to generate side by side
    file difference kila making HTML pages (see HtmlDiff kundi kila example
    usage).

    Note, this function utilizes the ndiff function to generate the side by
    side difference markup.  Optional ndiff arguments may be pitaed to this
    function na they kwenye turn will be pitaed to ndiff.
    """
    agiza re

    # regular expression kila finding intraline change indices
    change_re = re.compile(r'(\++|\-+|\^+)')

    # create the difference iterator to generate the differences
    diff_lines_iterator = ndiff(fromlines,tolines,linejunk,charjunk)

    eleza _make_line(lines, format_key, side, num_lines=[0,0]):
        """Returns line of text ukijumuisha user's change markup na line formatting.

        lines -- list of lines kutoka the ndiff generator to produce a line of
                 text from.  When producing the line of text to return, the
                 lines used are removed kutoka this list.
        format_key -- '+' rudisha first line kwenye list ukijumuisha "add" markup around
                          the entire line.
                      '-' rudisha first line kwenye list ukijumuisha "delete" markup around
                          the entire line.
                      '?' rudisha first line kwenye list ukijumuisha add/delete/change
                          intraline markup (indices obtained kutoka second line)
                      Tupu rudisha first line kwenye list ukijumuisha no markup
        side -- indice into the num_lines list (0=from,1=to)
        num_lines -- from/to current line number.  This ni NOT intended to be a
                     pitaed parameter.  It ni present kama a keyword argument to
                     maintain memory of the current line numbers between calls
                     of this function.

        Note, this function ni purposefully sio defined at the module scope so
        that data it needs kutoka its parent function (within whose context it
        ni defined) does sio need to be of module scope.
        """
        num_lines[side] += 1
        # Handle case where no user markup ni to be added, just rudisha line of
        # text ukijumuisha user's line format to allow kila usage of the line number.
        ikiwa format_key ni Tupu:
            rudisha (num_lines[side],lines.pop(0)[2:])
        # Handle case of intraline changes
        ikiwa format_key == '?':
            text, markers = lines.pop(0), lines.pop(0)
            # find intraline changes (store change type na indices kwenye tuples)
            sub_info = []
            eleza record_sub_info(match_object,sub_info=sub_info):
                sub_info.append([match_object.group(1)[0],match_object.span()])
                rudisha match_object.group(1)
            change_re.sub(record_sub_info,markers)
            # process each tuple inserting our special marks that won't be
            # noticed by an xml/html escaper.
            kila key,(begin,end) kwenye reversed(sub_info):
                text = text[0:begin]+'\0'+key+text[begin:end]+'\1'+text[end:]
            text = text[2:]
        # Handle case of add/delete entire line
        isipokua:
            text = lines.pop(0)[2:]
            # ikiwa line of text ni just a newline, insert a space so there is
            # something kila the user to highlight na see.
            ikiwa sio text:
                text = ' '
            # insert marks that won't be noticed by an xml/html escaper.
            text = '\0' + format_key + text + '\1'
        # Return line of text, first allow user's line formatter to do its
        # thing (such kama adding the line number) then replace the special
        # marks ukijumuisha what the user's change markup.
        rudisha (num_lines[side],text)

    eleza _line_iterator():
        """Yields from/to lines of text ukijumuisha a change indication.

        This function ni an iterator.  It itself pulls lines kutoka a
        differencing iterator, processes them na tumas them.  When it can
        it tumas both a "from" na a "to" line, otherwise it will tuma one
        ama the other.  In addition to tumaing the lines of from/to text, a
        boolean flag ni tumaed to indicate ikiwa the text line(s) have
        differences kwenye them.

        Note, this function ni purposefully sio defined at the module scope so
        that data it needs kutoka its parent function (within whose context it
        ni defined) does sio need to be of module scope.
        """
        lines = []
        num_blanks_pending, num_blanks_to_tuma = 0, 0
        wakati Kweli:
            # Load up next 4 lines so we can look ahead, create strings which
            # are a concatenation of the first character of each of the 4 lines
            # so we can do some very readable comparisons.
            wakati len(lines) < 4:
                lines.append(next(diff_lines_iterator, 'X'))
            s = ''.join([line[0] kila line kwenye lines])
            ikiwa s.startswith('X'):
                # When no more lines, pump out any remaining blank lines so the
                # corresponding add/delete lines get a matching blank line so
                # all line pairs get tumaed at the next level.
                num_blanks_to_tuma = num_blanks_pending
            lasivyo s.startswith('-?+?'):
                # simple intraline change
                tuma _make_line(lines,'?',0), _make_line(lines,'?',1), Kweli
                endelea
            lasivyo s.startswith('--++'):
                # kwenye delete block, add block coming: we do NOT want to get
                # caught up on blank lines yet, just process the delete line
                num_blanks_pending -= 1
                tuma _make_line(lines,'-',0), Tupu, Kweli
                endelea
            lasivyo s.startswith(('--?+', '--+', '- ')):
                # kwenye delete block na see an intraline change ama unchanged line
                # coming: tuma the delete line na then blanks
                from_line,to_line = _make_line(lines,'-',0), Tupu
                num_blanks_to_tuma,num_blanks_pending = num_blanks_pending-1,0
            lasivyo s.startswith('-+?'):
                # intraline change
                tuma _make_line(lines,Tupu,0), _make_line(lines,'?',1), Kweli
                endelea
            lasivyo s.startswith('-?+'):
                # intraline change
                tuma _make_line(lines,'?',0), _make_line(lines,Tupu,1), Kweli
                endelea
            lasivyo s.startswith('-'):
                # delete FROM line
                num_blanks_pending -= 1
                tuma _make_line(lines,'-',0), Tupu, Kweli
                endelea
            lasivyo s.startswith('+--'):
                # kwenye add block, delete block coming: we do NOT want to get
                # caught up on blank lines yet, just process the add line
                num_blanks_pending += 1
                tuma Tupu, _make_line(lines,'+',1), Kweli
                endelea
            lasivyo s.startswith(('+ ', '+-')):
                # will be leaving an add block: tuma blanks then add line
                from_line, to_line = Tupu, _make_line(lines,'+',1)
                num_blanks_to_tuma,num_blanks_pending = num_blanks_pending+1,0
            lasivyo s.startswith('+'):
                # inside an add block, tuma the add line
                num_blanks_pending += 1
                tuma Tupu, _make_line(lines,'+',1), Kweli
                endelea
            lasivyo s.startswith(' '):
                # unchanged text, tuma it to both sides
                tuma _make_line(lines[:],Tupu,0),_make_line(lines,Tupu,1),Uongo
                endelea
            # Catch up on the blank lines so when we tuma the next from/to
            # pair, they are lined up.
            while(num_blanks_to_tuma < 0):
                num_blanks_to_tuma += 1
                tuma Tupu,('','\n'),Kweli
            while(num_blanks_to_tuma > 0):
                num_blanks_to_tuma -= 1
                tuma ('','\n'),Tupu,Kweli
            ikiwa s.startswith('X'):
                rudisha
            isipokua:
                tuma from_line,to_line,Kweli

    eleza _line_pair_iterator():
        """Yields from/to lines of text ukijumuisha a change indication.

        This function ni an iterator.  It itself pulls lines kutoka the line
        iterator.  Its difference kutoka that iterator ni that this function
        always tumas a pair of from/to text lines (ukijumuisha the change
        indication).  If necessary it will collect single from/to lines
        until it has a matching pair from/to pair to tuma.

        Note, this function ni purposefully sio defined at the module scope so
        that data it needs kutoka its parent function (within whose context it
        ni defined) does sio need to be of module scope.
        """
        line_iterator = _line_iterator()
        fromlines,tolines=[],[]
        wakati Kweli:
            # Collecting lines of text until we have a from/to pair
            wakati (len(fromlines)==0 ama len(tolines)==0):
                jaribu:
                    from_line, to_line, found_diff = next(line_iterator)
                tatizo StopIteration:
                    rudisha
                ikiwa from_line ni sio Tupu:
                    fromlines.append((from_line,found_diff))
                ikiwa to_line ni sio Tupu:
                    tolines.append((to_line,found_diff))
            # Once we have a pair, remove them kutoka the collection na tuma it
            from_line, fromDiff = fromlines.pop(0)
            to_line, to_diff = tolines.pop(0)
            tuma (from_line,to_line,fromDiff ama to_diff)

    # Handle case where user does sio want context differencing, just tuma
    # them up without doing anything isipokua ukijumuisha them.
    line_pair_iterator = _line_pair_iterator()
    ikiwa context ni Tupu:
        tuma kutoka line_pair_iterator
    # Handle case where user wants context differencing.  We must do some
    # storage of lines until we know kila sure that they are to be tumaed.
    isipokua:
        context += 1
        lines_to_write = 0
        wakati Kweli:
            # Store lines up until we find a difference, note use of a
            # circular queue because we only need to keep around what
            # we need kila context.
            index, contextLines = 0, [Tupu]*(context)
            found_diff = Uongo
            while(found_diff ni Uongo):
                jaribu:
                    from_line, to_line, found_diff = next(line_pair_iterator)
                tatizo StopIteration:
                    rudisha
                i = index % context
                contextLines[i] = (from_line, to_line, found_diff)
                index += 1
            # Yield lines that we have collected so far, but first tuma
            # the user's separator.
            ikiwa index > context:
                tuma Tupu, Tupu, Tupu
                lines_to_write = context
            isipokua:
                lines_to_write = index
                index = 0
            while(lines_to_write):
                i = index % context
                index += 1
                tuma contextLines[i]
                lines_to_write -= 1
            # Now tuma the context lines after the change
            lines_to_write = context-1
            jaribu:
                while(lines_to_write):
                    from_line, to_line, found_diff = next(line_pair_iterator)
                    # If another change within the context, extend the context
                    ikiwa found_diff:
                        lines_to_write = context-1
                    isipokua:
                        lines_to_write -= 1
                    tuma from_line, to_line, found_diff
            tatizo StopIteration:
                # Catch exception kutoka next() na rudisha normally
                rudisha


_file_template = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
          "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html>

<head>
    <meta http-equiv="Content-Type"
          content="text/html; charset=%(charset)s" />
    <title></title>
    <style type="text/css">%(styles)s
    </style>
</head>

<body>
    %(table)s%(legend)s
</body>

</html>"""

_styles = """
        table.diff {font-family:Courier; border:medium;}
        .diff_header {background-color:#e0e0e0}
        td.diff_header {text-align:right}
        .diff_next {background-color:#c0c0c0}
        .diff_add {background-color:#aaffaa}
        .diff_chg {background-color:#ffff77}
        .diff_sub {background-color:#ffaaaa}"""

_table_template = """
    <table class="diff" id="difflib_chg_%(prefix)s_top"
           cellspacing="0" cellpadding="0" rules="groups" >
        <colgroup></colgroup> <colgroup></colgroup> <colgroup></colgroup>
        <colgroup></colgroup> <colgroup></colgroup> <colgroup></colgroup>
        %(header_row)s
        <tbody>
%(data_rows)s        </tbody>
    </table>"""

_legend = """
    <table class="diff" summary="Legends">
        <tr> <th colspan="2"> Legends </th> </tr>
        <tr> <td> <table border="" summary="Colors">
                      <tr><th> Colors </th> </tr>
                      <tr><td class="diff_add">&nbsp;Added&nbsp;</td></tr>
                      <tr><td class="diff_chg">Changed</td> </tr>
                      <tr><td class="diff_sub">Deleted</td> </tr>
                  </table></td>
             <td> <table border="" summary="Links">
                      <tr><th colspan="2"> Links </th> </tr>
                      <tr><td>(f)irst change</td> </tr>
                      <tr><td>(n)ext change</td> </tr>
                      <tr><td>(t)op</td> </tr>
                  </table></td> </tr>
    </table>"""

kundi HtmlDiff(object):
    """For producing HTML side by side comparison ukijumuisha change highlights.

    This kundi can be used to create an HTML table (or a complete HTML file
    containing the table) showing a side by side, line by line comparison
    of text ukijumuisha inter-line na intra-line change highlights.  The table can
    be generated kwenye either full ama contextual difference mode.

    The following methods are provided kila HTML generation:

    make_table -- generates HTML kila a single side by side table
    make_file -- generates complete HTML file ukijumuisha a single side by side table

    See tools/scripts/diff.py kila an example usage of this class.
    """

    _file_template = _file_template
    _styles = _styles
    _table_template = _table_template
    _legend = _legend
    _default_prefix = 0

    eleza __init__(self,tabsize=8,wrapcolumn=Tupu,linejunk=Tupu,
                 charjunk=IS_CHARACTER_JUNK):
        """HtmlDiff instance initializer

        Arguments:
        tabsize -- tab stop spacing, defaults to 8.
        wrapcolumn -- column number where lines are broken na wrapped,
            defaults to Tupu where lines are sio wrapped.
        linejunk,charjunk -- keyword arguments pitaed into ndiff() (used by
            HtmlDiff() to generate the side by side HTML differences).  See
            ndiff() documentation kila argument default values na descriptions.
        """
        self._tabsize = tabsize
        self._wrapcolumn = wrapcolumn
        self._linejunk = linejunk
        self._charjunk = charjunk

    eleza make_file(self, fromlines, tolines, fromdesc='', todesc='',
                  context=Uongo, numlines=5, *, charset='utf-8'):
        """Returns HTML file of side by side comparison ukijumuisha change highlights

        Arguments:
        fromlines -- list of "from" lines
        tolines -- list of "to" lines
        fromdesc -- "from" file column header string
        todesc -- "to" file column header string
        context -- set to Kweli kila contextual differences (defaults to Uongo
            which shows full differences).
        numlines -- number of context lines.  When context ni set Kweli,
            controls number of lines displayed before na after the change.
            When context ni Uongo, controls the number of lines to place
            the "next" link anchors before the next change (so click of
            "next" link jumps to just before the change).
        charset -- charset of the HTML document
        """

        rudisha (self._file_template % dict(
            styles=self._styles,
            legend=self._legend,
            table=self.make_table(fromlines, tolines, fromdesc, todesc,
                                  context=context, numlines=numlines),
            charset=charset
        )).encode(charset, 'xmlcharrefreplace').decode(charset)

    eleza _tab_newline_replace(self,fromlines,tolines):
        """Returns from/to line lists ukijumuisha tabs expanded na newlines removed.

        Instead of tab characters being replaced by the number of spaces
        needed to fill kwenye to the next tab stop, this function will fill
        the space ukijumuisha tab characters.  This ni done so that the difference
        algorithms can identify changes kwenye a file when tabs are replaced by
        spaces na vice versa.  At the end of the HTML generation, the tab
        characters will be replaced ukijumuisha a nonkomaable space.
        """
        eleza expand_tabs(line):
            # hide real spaces
            line = line.replace(' ','\0')
            # expand tabs into spaces
            line = line.expandtabs(self._tabsize)
            # replace spaces kutoka expanded tabs back into tab characters
            # (we'll replace them ukijumuisha markup after we do differencing)
            line = line.replace(' ','\t')
            rudisha line.replace('\0',' ').rstrip('\n')
        fromlines = [expand_tabs(line) kila line kwenye fromlines]
        tolines = [expand_tabs(line) kila line kwenye tolines]
        rudisha fromlines,tolines

    eleza _split_line(self,data_list,line_num,text):
        """Builds list of text lines by splitting text lines at wrap point

        This function will determine ikiwa the input text line needs to be
        wrapped (split) into separate lines.  If so, the first wrap point
        will be determined na the first line appended to the output
        text line list.  This function ni used recursively to handle
        the second part of the split line to further split it.
        """
        # ikiwa blank line ama context separator, just add it to the output list
        ikiwa sio line_num:
            data_list.append((line_num,text))
            rudisha

        # ikiwa line text doesn't need wrapping, just add it to the output list
        size = len(text)
        max = self._wrapcolumn
        ikiwa (size <= max) ama ((size -(text.count('\0')*3)) <= max):
            data_list.append((line_num,text))
            rudisha

        # scan text looking kila the wrap point, keeping track ikiwa the wrap
        # point ni inside markers
        i = 0
        n = 0
        mark = ''
        wakati n < max na i < size:
            ikiwa text[i] == '\0':
                i += 1
                mark = text[i]
                i += 1
            lasivyo text[i] == '\1':
                i += 1
                mark = ''
            isipokua:
                i += 1
                n += 1

        # wrap point ni inside text, koma it up into separate lines
        line1 = text[:i]
        line2 = text[i:]

        # ikiwa wrap point ni inside markers, place end marker at end of first
        # line na start marker at beginning of second line because each
        # line will have its own table tag markup around it.
        ikiwa mark:
            line1 = line1 + '\1'
            line2 = '\0' + mark + line2

        # tack on first line onto the output list
        data_list.append((line_num,line1))

        # use this routine again to wrap the remaining text
        self._split_line(data_list,'>',line2)

    eleza _line_wrapper(self,diffs):
        """Returns iterator that splits (wraps) mdiff text lines"""

        # pull from/to data na flags kutoka mdiff iterator
        kila fromdata,todata,flag kwenye diffs:
            # check kila context separators na pita them through
            ikiwa flag ni Tupu:
                tuma fromdata,todata,flag
                endelea
            (fromline,fromtext),(toline,totext) = fromdata,todata
            # kila each from/to line split it at the wrap column to form
            # list of text lines.
            fromlist,tolist = [],[]
            self._split_line(fromlist,fromline,fromtext)
            self._split_line(tolist,toline,totext)
            # tuma from/to line kwenye pairs inserting blank lines as
            # necessary when one side has more wrapped lines
            wakati fromlist ama tolist:
                ikiwa fromlist:
                    fromdata = fromlist.pop(0)
                isipokua:
                    fromdata = ('',' ')
                ikiwa tolist:
                    todata = tolist.pop(0)
                isipokua:
                    todata = ('',' ')
                tuma fromdata,todata,flag

    eleza _collect_lines(self,diffs):
        """Collects mdiff output into separate lists

        Before storing the mdiff from/to data into a list, it ni converted
        into a single line of text ukijumuisha HTML markup.
        """

        fromlist,tolist,flaglist = [],[],[]
        # pull from/to data na flags kutoka mdiff style iterator
        kila fromdata,todata,flag kwenye diffs:
            jaribu:
                # store HTML markup of the lines into the lists
                fromlist.append(self._format_line(0,flag,*fromdata))
                tolist.append(self._format_line(1,flag,*todata))
            tatizo TypeError:
                # exceptions occur kila lines where context separators go
                fromlist.append(Tupu)
                tolist.append(Tupu)
            flaglist.append(flag)
        rudisha fromlist,tolist,flaglist

    eleza _format_line(self,side,flag,linenum,text):
        """Returns HTML markup of "from" / "to" text lines

        side -- 0 ama 1 indicating "from" ama "to" text
        flag -- indicates ikiwa difference on line
        linenum -- line number (used kila line number column)
        text -- line text to be marked up
        """
        jaribu:
            linenum = '%d' % linenum
            id = ' id="%s%s"' % (self._prefix[side],linenum)
        tatizo TypeError:
            # handle blank lines where linenum ni '>' ama ''
            id = ''
        # replace those things that would get confused ukijumuisha HTML symbols
        text=text.replace("&","&amp;").replace(">","&gt;").replace("<","&lt;")

        # make space non-komaable so they don't get compressed ama line wrapped
        text = text.replace(' ','&nbsp;').rstrip()

        rudisha '<td class="diff_header"%s>%s</td><td nowrap="nowrap">%s</td>' \
               % (id,linenum,text)

    eleza _make_prefix(self):
        """Create unique anchor prefixes"""

        # Generate a unique anchor prefix so multiple tables
        # can exist on the same HTML page without conflicts.
        fromprefix = "from%d_" % HtmlDiff._default_prefix
        toprefix = "to%d_" % HtmlDiff._default_prefix
        HtmlDiff._default_prefix += 1
        # store prefixes so line format method has access
        self._prefix = [fromprefix,toprefix]

    eleza _convert_flags(self,fromlist,tolist,flaglist,context,numlines):
        """Makes list of "next" links"""

        # all anchor names will be generated using the unique "to" prefix
        toprefix = self._prefix[1]

        # process change flags, generating middle column of next anchors/links
        next_id = ['']*len(flaglist)
        next_href = ['']*len(flaglist)
        num_chg, in_change = 0, Uongo
        last = 0
        kila i,flag kwenye enumerate(flaglist):
            ikiwa flag:
                ikiwa haiko kwenye_change:
                    in_change = Kweli
                    last = i
                    # at the beginning of a change, drop an anchor a few lines
                    # (the context lines) before the change kila the previous
                    # link
                    i = max([0,i-numlines])
                    next_id[i] = ' id="difflib_chg_%s_%d"' % (toprefix,num_chg)
                    # at the beginning of a change, drop a link to the next
                    # change
                    num_chg += 1
                    next_href[last] = '<a href="#difflib_chg_%s_%d">n</a>' % (
                         toprefix,num_chg)
            isipokua:
                in_change = Uongo
        # check kila cases where there ni no content to avoid exceptions
        ikiwa sio flaglist:
            flaglist = [Uongo]
            next_id = ['']
            next_href = ['']
            last = 0
            ikiwa context:
                fromlist = ['<td></td><td>&nbsp;No Differences Found&nbsp;</td>']
                tolist = fromlist
            isipokua:
                fromlist = tolist = ['<td></td><td>&nbsp;Empty File&nbsp;</td>']
        # ikiwa sio a change on first line, drop a link
        ikiwa sio flaglist[0]:
            next_href[0] = '<a href="#difflib_chg_%s_0">f</a>' % toprefix
        # redo the last link to link to the top
        next_href[last] = '<a href="#difflib_chg_%s_top">t</a>' % (toprefix)

        rudisha fromlist,tolist,flaglist,next_href,next_id

    eleza make_table(self,fromlines,tolines,fromdesc='',todesc='',context=Uongo,
                   numlines=5):
        """Returns HTML table of side by side comparison ukijumuisha change highlights

        Arguments:
        fromlines -- list of "from" lines
        tolines -- list of "to" lines
        fromdesc -- "from" file column header string
        todesc -- "to" file column header string
        context -- set to Kweli kila contextual differences (defaults to Uongo
            which shows full differences).
        numlines -- number of context lines.  When context ni set Kweli,
            controls number of lines displayed before na after the change.
            When context ni Uongo, controls the number of lines to place
            the "next" link anchors before the next change (so click of
            "next" link jumps to just before the change).
        """

        # make unique anchor prefixes so that multiple tables may exist
        # on the same page without conflict.
        self._make_prefix()

        # change tabs to spaces before it gets more difficult after we insert
        # markup
        fromlines,tolines = self._tab_newline_replace(fromlines,tolines)

        # create diffs iterator which generates side by side from/to data
        ikiwa context:
            context_lines = numlines
        isipokua:
            context_lines = Tupu
        diffs = _mdiff(fromlines,tolines,context_lines,linejunk=self._linejunk,
                      charjunk=self._charjunk)

        # set up iterator to wrap lines that exceed desired width
        ikiwa self._wrapcolumn:
            diffs = self._line_wrapper(diffs)

        # collect up from/to lines na flags into lists (also format the lines)
        fromlist,tolist,flaglist = self._collect_lines(diffs)

        # process change flags, generating middle column of next anchors/links
        fromlist,tolist,flaglist,next_href,next_id = self._convert_flags(
            fromlist,tolist,flaglist,context,numlines)

        s = []
        fmt = '            <tr><td class="diff_next"%s>%s</td>%s' + \
              '<td class="diff_next">%s</td>%s</tr>\n'
        kila i kwenye range(len(flaglist)):
            ikiwa flaglist[i] ni Tupu:
                # mdiff tumas Tupu on separator lines skip the bogus ones
                # generated kila the first line
                ikiwa i > 0:
                    s.append('        </tbody>        \n        <tbody>\n')
            isipokua:
                s.append( fmt % (next_id[i],next_href[i],fromlist[i],
                                           next_href[i],tolist[i]))
        ikiwa fromdesc ama todesc:
            header_row = '<thead><tr>%s%s%s%s</tr></thead>' % (
                '<th class="diff_next"><br /></th>',
                '<th colspan="2" class="diff_header">%s</th>' % fromdesc,
                '<th class="diff_next"><br /></th>',
                '<th colspan="2" class="diff_header">%s</th>' % todesc)
        isipokua:
            header_row = ''

        table = self._table_template % dict(
            data_rows=''.join(s),
            header_row=header_row,
            prefix=self._prefix[1])

        rudisha table.replace('\0+','<span class="diff_add">'). \
                     replace('\0-','<span class="diff_sub">'). \
                     replace('\0^','<span class="diff_chg">'). \
                     replace('\1','</span>'). \
                     replace('\t','&nbsp;')

toa re

eleza restore(delta, which):
    r"""
    Generate one of the two sequences that generated a delta.

    Given a `delta` produced by `Differ.compare()` ama `ndiff()`, extract
    lines originating kutoka file 1 ama 2 (parameter `which`), stripping off line
    prefixes.

    Examples:

    >>> diff = ndiff('one\ntwo\nthree\n'.splitlines(keepends=Kweli),
    ...              'ore\ntree\nemu\n'.splitlines(keepends=Kweli))
    >>> diff = list(diff)
    >>> andika(''.join(restore(diff, 1)), end="")
    one
    two
    three
    >>> andika(''.join(restore(diff, 2)), end="")
    ore
    tree
    emu
    """
    jaribu:
        tag = {1: "- ", 2: "+ "}[int(which)]
    tatizo KeyError:
        ashiria ValueError('unknown delta choice (must be 1 ama 2): %r'
                           % which) kutoka Tupu
    prefixes = ("  ", tag)
    kila line kwenye delta:
        ikiwa line[:2] kwenye prefixes:
            tuma line[2:]

eleza _test():
    agiza doctest, difflib
    rudisha doctest.testmod(difflib)

ikiwa __name__ == "__main__":
    _test()
