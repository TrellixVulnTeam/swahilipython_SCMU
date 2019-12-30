#! /usr/bin/env python3

"""Transform gprof(1) output into useful HTML."""

agiza html
agiza os
agiza re
agiza sys
agiza webbrowser

header = """\
<html>
<head>
  <title>gprof output (%s)</title>
</head>
<body>
<pre>
"""

trailer = """\
</pre>
</body>
</html>
"""

eleza add_escapes(filename):
    ukijumuisha open(filename) kama fp:
        kila line kwenye fp:
            tuma html.escape(line)

eleza gprof2html(input, output, filename):
    output.write(header % filename)
    kila line kwenye input:
        output.write(line)
        ikiwa line.startswith(" time"):
            koma
    labels = {}
    kila line kwenye input:
        m = re.match(r"(.*  )(\w+)\n", line)
        ikiwa sio m:
            output.write(line)
            koma
        stuff, fname = m.group(1, 2)
        labels[fname] = fname
        output.write('%s<a name="flat:%s" href="#call:%s">%s</a>\n' %
                     (stuff, fname, fname, fname))
    kila line kwenye input:
        output.write(line)
        ikiwa line.startswith("index % time"):
            koma
    kila line kwenye input:
        m = re.match(r"(.*  )(\w+)(( &lt;cycle.*&gt;)? \[\d+\])\n", line)
        ikiwa sio m:
            output.write(line)
            ikiwa line.startswith("Index by function name"):
                koma
            endelea
        prefix, fname, suffix = m.group(1, 2, 3)
        ikiwa fname haiko kwenye labels:
            output.write(line)
            endelea
        ikiwa line.startswith("["):
            output.write('%s<a name="call:%s" href="#flat:%s">%s</a>%s\n' %
                         (prefix, fname, fname, fname, suffix))
        isipokua:
            output.write('%s<a href="#call:%s">%s</a>%s\n' %
                         (prefix, fname, fname, suffix))
    kila line kwenye input:
        kila part kwenye re.findall(r"(\w+(?:\.c)?|\W+)", line):
            ikiwa part kwenye labels:
                part = '<a href="#call:%s">%s</a>' % (part, part)
            output.write(part)
    output.write(trailer)


eleza main():
    filename = "gprof.out"
    ikiwa sys.argv[1:]:
        filename = sys.argv[1]
    outputfilename = filename + ".html"
    input = add_escapes(filename)
    ukijumuisha open(outputfilename, "w") kama output:
        gprof2html(input, output, filename)
    webbrowser.open("file:" + os.path.abspath(outputfilename))

ikiwa __name__ == '__main__':
    main()
