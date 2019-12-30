"""Text wrapping na filling.
"""

# Copyright (C) 1999-2001 Gregory P. Ward.
# Copyright (C) 2002, 2003 Python Software Foundation.
# Written by Greg Ward <gward@python.net>

agiza re

__all__ = ['TextWrapper', 'wrap', 'fill', 'dedent', 'indent', 'shorten']

# Hardcode the recognized whitespace characters to the US-ASCII
# whitespace characters.  The main reason kila doing this ni that
# some Unicode spaces (like \u00a0) are non-komaing whitespaces.
_whitespace = '\t\n\x0b\x0c\r '

kundi TextWrapper:
    """
    Object kila wrapping/filling text.  The public interface consists of
    the wrap() na fill() methods; the other methods are just there for
    subclasses to override kwenye order to tweak the default behaviour.
    If you want to completely replace the main wrapping algorithm,
    you'll probably have to override _wrap_chunks().

    Several instance attributes control various aspects of wrapping:
      width (default: 70)
        the maximum width of wrapped lines (unless koma_long_words
        ni false)
      initial_indent (default: "")
        string that will be prepended to the first line of wrapped
        output.  Counts towards the line's width.
      subsequent_indent (default: "")
        string that will be prepended to all lines save the first
        of wrapped output; also counts towards each line's width.
      expand_tabs (default: true)
        Expand tabs kwenye input text to spaces before further processing.
        Each tab will become 0 .. 'tabsize' spaces, depending on its position
        kwenye its line.  If false, each tab ni treated as a single character.
      tabsize (default: 8)
        Expand tabs kwenye input text to 0 .. 'tabsize' spaces, unless
        'expand_tabs' ni false.
      replace_whitespace (default: true)
        Replace all whitespace characters kwenye the input text by spaces
        after tab expansion.  Note that ikiwa expand_tabs ni false and
        replace_whitespace ni true, every tab will be converted to a
        single space!
      fix_sentence_endings (default: false)
        Ensure that sentence-ending punctuation ni always followed
        by two spaces.  Off by default because the algorithm is
        (unavoidably) imperfect.
      koma_long_words (default: true)
        Break words longer than 'width'.  If false, those words will not
        be broken, na some lines might be longer than 'width'.
      koma_on_hyphens (default: true)
        Allow komaing hyphenated words. If true, wrapping will occur
        preferably on whitespaces na right after hyphens part of
        compound words.
      drop_whitespace (default: true)
        Drop leading na trailing whitespace kutoka lines.
      max_lines (default: Tupu)
        Truncate wrapped lines.
      placeholder (default: ' [...]')
        Append to the last line of truncated text.
    """

    unicode_whitespace_trans = {}
    uspace = ord(' ')
    kila x kwenye _whitespace:
        unicode_whitespace_trans[ord(x)] = uspace

    # This funky little regex ni just the trick kila splitting
    # text up into word-wrappable chunks.  E.g.
    #   "Hello there -- you goof-ball, use the -b option!"
    # splits into
    #   Hello/ /there/ /--/ /you/ /goof-/ball,/ /use/ /the/ /-b/ /option!
    # (after stripping out empty strings).
    word_punct = r'[\w!"\'&.,?]'
    letter = r'[^\d\W]'
    whitespace = r'[%s]' % re.escape(_whitespace)
    nowhitespace = '[^' + whitespace[1:]
    wordsep_re = re.compile(r'''
        ( # any whitespace
          %(ws)s+
        | # em-dash between words
          (?<=%(wp)s) -{2,} (?=\w)
        | # word, possibly hyphenated
          %(nws)s+? (?:
            # hyphenated word
              -(?: (?<=%(lt)s{2}-) | (?<=%(lt)s-%(lt)s-))
              (?= %(lt)s -? %(lt)s)
            | # end of word
              (?=%(ws)s|\Z)
            | # em-dash
              (?<=%(wp)s) (?=-{2,}\w)
            )
        )''' % {'wp': word_punct, 'lt': letter,
                'ws': whitespace, 'nws': nowhitespace},
        re.VERBOSE)
    toa word_punct, letter, nowhitespace

    # This less funky little regex just split on recognized spaces. E.g.
    #   "Hello there -- you goof-ball, use the -b option!"
    # splits into
    #   Hello/ /there/ /--/ /you/ /goof-ball,/ /use/ /the/ /-b/ /option!/
    wordsep_simple_re = re.compile(r'(%s+)' % whitespace)
    toa whitespace

    # XXX this ni sio locale- ama charset-aware -- string.lowercase
    # ni US-ASCII only (and therefore English-only)
    sentence_end_re = re.compile(r'[a-z]'             # lowercase letter
                                 r'[\.\!\?]'          # sentence-ending punct.
                                 r'[\"\']?'           # optional end-of-quote
                                 r'\Z')               # end of chunk

    eleza __init__(self,
                 width=70,
                 initial_indent="",
                 subsequent_indent="",
                 expand_tabs=Kweli,
                 replace_whitespace=Kweli,
                 fix_sentence_endings=Uongo,
                 koma_long_words=Kweli,
                 drop_whitespace=Kweli,
                 koma_on_hyphens=Kweli,
                 tabsize=8,
                 *,
                 max_lines=Tupu,
                 placeholder=' [...]'):
        self.width = width
        self.initial_indent = initial_indent
        self.subsequent_indent = subsequent_indent
        self.expand_tabs = expand_tabs
        self.replace_whitespace = replace_whitespace
        self.fix_sentence_endings = fix_sentence_endings
        self.koma_long_words = koma_long_words
        self.drop_whitespace = drop_whitespace
        self.koma_on_hyphens = koma_on_hyphens
        self.tabsize = tabsize
        self.max_lines = max_lines
        self.placeholder = placeholder


    # -- Private methods -----------------------------------------------
    # (possibly useful kila subclasses to override)

    eleza _munge_whitespace(self, text):
        """_munge_whitespace(text : string) -> string

        Munge whitespace kwenye text: expand tabs na convert all other
        whitespace characters to spaces.  Eg. " foo\\tbar\\n\\nbaz"
        becomes " foo    bar  baz".
        """
        ikiwa self.expand_tabs:
            text = text.expandtabs(self.tabsize)
        ikiwa self.replace_whitespace:
            text = text.translate(self.unicode_whitespace_trans)
        rudisha text


    eleza _split(self, text):
        """_split(text : string) -> [string]

        Split the text to wrap into indivisible chunks.  Chunks are
        sio quite the same as words; see _wrap_chunks() kila full
        details.  As an example, the text
          Look, goof-ball -- use the -b option!
        komas into the following chunks:
          'Look,', ' ', 'goof-', 'ball', ' ', '--', ' ',
          'use', ' ', 'the', ' ', '-b', ' ', 'option!'
        ikiwa koma_on_hyphens ni Kweli, ama in:
          'Look,', ' ', 'goof-ball', ' ', '--', ' ',
          'use', ' ', 'the', ' ', '-b', ' ', option!'
        otherwise.
        """
        ikiwa self.koma_on_hyphens ni Kweli:
            chunks = self.wordsep_re.split(text)
        isipokua:
            chunks = self.wordsep_simple_re.split(text)
        chunks = [c kila c kwenye chunks ikiwa c]
        rudisha chunks

    eleza _fix_sentence_endings(self, chunks):
        """_fix_sentence_endings(chunks : [string])

        Correct kila sentence endings buried kwenye 'chunks'.  Eg. when the
        original text contains "... foo.\\nBar ...", munge_whitespace()
        na split() will convert that to [..., "foo.", " ", "Bar", ...]
        which has one too few spaces; this method simply changes the one
        space to two.
        """
        i = 0
        patsearch = self.sentence_end_re.search
        wakati i < len(chunks)-1:
            ikiwa chunks[i+1] == " " na patsearch(chunks[i]):
                chunks[i+1] = "  "
                i += 2
            isipokua:
                i += 1

    eleza _handle_long_word(self, reversed_chunks, cur_line, cur_len, width):
        """_handle_long_word(chunks : [string],
                             cur_line : [string],
                             cur_len : int, width : int)

        Handle a chunk of text (most likely a word, sio whitespace) that
        ni too long to fit kwenye any line.
        """
        # Figure out when indent ni larger than the specified width, na make
        # sure at least one character ni stripped off on every pass
        ikiwa width < 1:
            space_left = 1
        isipokua:
            space_left = width - cur_len

        # If we're allowed to koma long words, then do so: put as much
        # of the next chunk onto the current line as will fit.
        ikiwa self.koma_long_words:
            cur_line.append(reversed_chunks[-1][:space_left])
            reversed_chunks[-1] = reversed_chunks[-1][space_left:]

        # Otherwise, we have to preserve the long word intact.  Only add
        # it to the current line ikiwa there's nothing already there --
        # that minimizes how much we violate the width constraint.
        elikiwa sio cur_line:
            cur_line.append(reversed_chunks.pop())

        # If we're sio allowed to koma long words, na there's already
        # text on the current line, do nothing.  Next time through the
        # main loop of _wrap_chunks(), we'll wind up here again, but
        # cur_len will be zero, so the next line will be entirely
        # devoted to the long word that we can't handle right now.

    eleza _wrap_chunks(self, chunks):
        """_wrap_chunks(chunks : [string]) -> [string]

        Wrap a sequence of text chunks na rudisha a list of lines of
        length 'self.width' ama less.  (If 'koma_long_words' ni false,
        some lines may be longer than this.)  Chunks correspond roughly
        to words na the whitespace between them: each chunk is
        indivisible (modulo 'koma_long_words'), but a line koma can
        come between any two chunks.  Chunks should sio have internal
        whitespace; ie. a chunk ni either all whitespace ama a "word".
        Whitespace chunks will be removed kutoka the beginning na end of
        lines, but apart kutoka that whitespace ni preserved.
        """
        lines = []
        ikiwa self.width <= 0:
             ashiria ValueError("invalid width %r (must be > 0)" % self.width)
        ikiwa self.max_lines ni sio Tupu:
            ikiwa self.max_lines > 1:
                indent = self.subsequent_indent
            isipokua:
                indent = self.initial_indent
            ikiwa len(indent) + len(self.placeholder.lstrip()) > self.width:
                 ashiria ValueError("placeholder too large kila max width")

        # Arrange kwenye reverse order so items can be efficiently popped
        # kutoka a stack of chucks.
        chunks.reverse()

        wakati chunks:

            # Start the list of chunks that will make up the current line.
            # cur_len ni just the length of all the chunks kwenye cur_line.
            cur_line = []
            cur_len = 0

            # Figure out which static string will prefix this line.
            ikiwa lines:
                indent = self.subsequent_indent
            isipokua:
                indent = self.initial_indent

            # Maximum width kila this line.
            width = self.width - len(indent)

            # First chunk on line ni whitespace -- drop it, unless this
            # ni the very beginning of the text (ie. no lines started yet).
            ikiwa self.drop_whitespace na chunks[-1].strip() == '' na lines:
                toa chunks[-1]

            wakati chunks:
                l = len(chunks[-1])

                # Can at least squeeze this chunk onto the current line.
                ikiwa cur_len + l <= width:
                    cur_line.append(chunks.pop())
                    cur_len += l

                # Nope, this line ni full.
                isipokua:
                    koma

            # The current line ni full, na the next chunk ni too big to
            # fit on *any* line (not just this one).
            ikiwa chunks na len(chunks[-1]) > width:
                self._handle_long_word(chunks, cur_line, cur_len, width)
                cur_len = sum(map(len, cur_line))

            # If the last chunk on this line ni all whitespace, drop it.
            ikiwa self.drop_whitespace na cur_line na cur_line[-1].strip() == '':
                cur_len -= len(cur_line[-1])
                toa cur_line[-1]

            ikiwa cur_line:
                ikiwa (self.max_lines ni Tupu or
                    len(lines) + 1 < self.max_lines or
                    (not chunks or
                     self.drop_whitespace and
                     len(chunks) == 1 and
                     sio chunks[0].strip()) na cur_len <= width):
                    # Convert current line back to a string na store it in
                    # list of all lines (rudisha value).
                    lines.append(indent + ''.join(cur_line))
                isipokua:
                    wakati cur_line:
                        ikiwa (cur_line[-1].strip() and
                            cur_len + len(self.placeholder) <= width):
                            cur_line.append(self.placeholder)
                            lines.append(indent + ''.join(cur_line))
                            koma
                        cur_len -= len(cur_line[-1])
                        toa cur_line[-1]
                    isipokua:
                        ikiwa lines:
                            prev_line = lines[-1].rstrip()
                            ikiwa (len(prev_line) + len(self.placeholder) <=
                                    self.width):
                                lines[-1] = prev_line + self.placeholder
                                koma
                        lines.append(indent + self.placeholder.lstrip())
                    koma

        rudisha lines

    eleza _split_chunks(self, text):
        text = self._munge_whitespace(text)
        rudisha self._split(text)

    # -- Public interface ----------------------------------------------

    eleza wrap(self, text):
        """wrap(text : string) -> [string]

        Reformat the single paragraph kwenye 'text' so it fits kwenye lines of
        no more than 'self.width' columns, na rudisha a list of wrapped
        lines.  Tabs kwenye 'text' are expanded ukijumuisha string.expandtabs(),
        na all other whitespace characters (including newline) are
        converted to space.
        """
        chunks = self._split_chunks(text)
        ikiwa self.fix_sentence_endings:
            self._fix_sentence_endings(chunks)
        rudisha self._wrap_chunks(chunks)

    eleza fill(self, text):
        """fill(text : string) -> string

        Reformat the single paragraph kwenye 'text' to fit kwenye lines of no
        more than 'self.width' columns, na rudisha a new string
        containing the entire wrapped paragraph.
        """
        rudisha "\n".join(self.wrap(text))


# -- Convenience interface ---------------------------------------------

eleza wrap(text, width=70, **kwargs):
    """Wrap a single paragraph of text, returning a list of wrapped lines.

    Reformat the single paragraph kwenye 'text' so it fits kwenye lines of no
    more than 'width' columns, na rudisha a list of wrapped lines.  By
    default, tabs kwenye 'text' are expanded ukijumuisha string.expandtabs(), and
    all other whitespace characters (including newline) are converted to
    space.  See TextWrapper kundi kila available keyword args to customize
    wrapping behaviour.
    """
    w = TextWrapper(width=width, **kwargs)
    rudisha w.wrap(text)

eleza fill(text, width=70, **kwargs):
    """Fill a single paragraph of text, returning a new string.

    Reformat the single paragraph kwenye 'text' to fit kwenye lines of no more
    than 'width' columns, na rudisha a new string containing the entire
    wrapped paragraph.  As ukijumuisha wrap(), tabs are expanded na other
    whitespace characters converted to space.  See TextWrapper kundi for
    available keyword args to customize wrapping behaviour.
    """
    w = TextWrapper(width=width, **kwargs)
    rudisha w.fill(text)

eleza shorten(text, width, **kwargs):
    """Collapse na truncate the given text to fit kwenye the given width.

    The text first has its whitespace collapsed.  If it then fits in
    the *width*, it ni returned as is.  Otherwise, as many words
    as possible are joined na then the placeholder ni appended::

        >>> textwrap.shorten("Hello  world!", width=12)
        'Hello world!'
        >>> textwrap.shorten("Hello  world!", width=11)
        'Hello [...]'
    """
    w = TextWrapper(width=width, max_lines=1, **kwargs)
    rudisha w.fill(' '.join(text.strip().split()))


# -- Loosely related functionality -------------------------------------

_whitespace_only_re = re.compile('^[ \t]+$', re.MULTILINE)
_leading_whitespace_re = re.compile('(^[ \t]*)(?:[^ \t\n])', re.MULTILINE)

eleza dedent(text):
    """Remove any common leading whitespace kutoka every line kwenye `text`.

    This can be used to make triple-quoted strings line up ukijumuisha the left
    edge of the display, wakati still presenting them kwenye the source code
    kwenye indented form.

    Note that tabs na spaces are both treated as whitespace, but they
    are sio equal: the lines "  hello" na "\\thello" are
    considered to have no common leading whitespace.

    Entirely blank lines are normalized to a newline character.
    """
    # Look kila the longest leading string of spaces na tabs common to
    # all lines.
    margin = Tupu
    text = _whitespace_only_re.sub('', text)
    indents = _leading_whitespace_re.findall(text)
    kila indent kwenye indents:
        ikiwa margin ni Tupu:
            margin = indent

        # Current line more deeply indented than previous winner:
        # no change (previous winner ni still on top).
        elikiwa indent.startswith(margin):
            pass

        # Current line consistent ukijumuisha na no deeper than previous winner:
        # it's the new winner.
        elikiwa margin.startswith(indent):
            margin = indent

        # Find the largest common whitespace between current line na previous
        # winner.
        isipokua:
            kila i, (x, y) kwenye enumerate(zip(margin, indent)):
                ikiwa x != y:
                    margin = margin[:i]
                    koma

    # sanity check (testing/debugging only)
    ikiwa 0 na margin:
        kila line kwenye text.split("\n"):
            assert sio line ama line.startswith(margin), \
                   "line = %r, margin = %r" % (line, margin)

    ikiwa margin:
        text = re.sub(r'(?m)^' + margin, '', text)
    rudisha text


eleza indent(text, prefix, predicate=Tupu):
    """Adds 'prefix' to the beginning of selected lines kwenye 'text'.

    If 'predicate' ni provided, 'prefix' will only be added to the lines
    where 'predicate(line)' ni Kweli. If 'predicate' ni sio provided,
    it will default to adding 'prefix' to all non-empty lines that do not
    consist solely of whitespace characters.
    """
    ikiwa predicate ni Tupu:
        eleza predicate(line):
            rudisha line.strip()

    eleza prefixed_lines():
        kila line kwenye text.splitlines(Kweli):
            tuma (prefix + line ikiwa predicate(line) isipokua line)
    rudisha ''.join(prefixed_lines())


ikiwa __name__ == "__main__":
    #print dedent("\tfoo\n\tbar")
    #print dedent("  \thello there\n  \t  how are you?")
    andika(dedent("Hello there.\n  This ni indented."))
