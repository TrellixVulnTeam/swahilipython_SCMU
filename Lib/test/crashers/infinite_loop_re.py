
# This was taken kutoka http://python.org/sf/1541697
# It's sio technically a crasher.  It may sio even truly be infinite,
# however, I haven't waited a long time to see the result.  It takes
# 100% of CPU wakati running this na should be fixed.

agiza re
starttag = re.compile(r'<[a-zA-Z][-_.:a-zA-Z0-9]*\s*('
        r'\s*([a-zA-Z_][-:.a-zA-Z_0-9]*)(\s*=\s*'
        r'(\'[^\']*\'|"[^"]*"|[-a-zA-Z0-9./,:;+*%?!&$\(\)_#=~@]'
        r'[][\-a-zA-Z0-9./,:;+*%?!&$\(\)_#=~\'"@]*(?=[\s>/<])))?'
    r')*\s*/?\s*(?=[<>])')

ikiwa __name__ == '__main__':
    foo = '<table cellspacing="0" cellpadding="0" style="border-collapse'
    starttag.match(foo)
