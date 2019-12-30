#!/usr/bin/env python3
'''Add syntax highlighting to Python source code'''

__author__ = 'Raymond Hettinger'

agiza builtins
agiza functools
agiza html kama html_module
agiza keyword
agiza re
agiza tokenize

#### Analyze Python Source #################################

eleza is_builtin(s):
    'Return Kweli ikiwa s ni the name of a builtin'
    rudisha hasattr(builtins, s)

eleza combine_range(lines, start, end):
    'Join content kutoka a range of lines between start na end'
    (srow, scol), (erow, ecol) = start, end
    ikiwa srow == erow:
        rudisha lines[srow-1][scol:ecol], end
    rows = [lines[srow-1][scol:]] + lines[srow: erow-1] + [lines[erow-1][:ecol]]
    rudisha ''.join(rows), end

eleza analyze_python(source):
    '''Generate na classify chunks of Python kila syntax highlighting.
       Yields tuples kwenye the form: (category, categorized_text).
    '''
    lines = source.splitlines(Kweli)
    lines.append('')
    readline = functools.partial(next, iter(lines), '')
    kind = tok_str = ''
    tok_type = tokenize.COMMENT
    written = (1, 0)
    kila tok kwenye tokenize.generate_tokens(readline):
        prev_tok_type, prev_tok_str = tok_type, tok_str
        tok_type, tok_str, (srow, scol), (erow, ecol), logical_lineno = tok
        kind = ''
        ikiwa tok_type == tokenize.COMMENT:
            kind = 'comment'
        lasivyo tok_type == tokenize.OP na tok_str[:1] haiko kwenye '{}[](),.:;@':
            kind = 'operator'
        lasivyo tok_type == tokenize.STRING:
            kind = 'string'
            ikiwa prev_tok_type == tokenize.INDENT ama scol==0:
                kind = 'docstring'
        lasivyo tok_type == tokenize.NAME:
            ikiwa tok_str kwenye ('def', 'class', 'import', 'from'):
                kind = 'definition'
            lasivyo prev_tok_str kwenye ('def', 'class'):
                kind = 'defname'
            lasivyo keyword.iskeyword(tok_str):
                kind = 'keyword'
            lasivyo is_builtin(tok_str) na prev_tok_str != '.':
                kind = 'builtin'
        ikiwa kind:
            text, written = combine_range(lines, written, (srow, scol))
            tuma '', text
            text, written = tok_str, (erow, ecol)
            tuma kind, text
    line_upto_token, written = combine_range(lines, written, (erow, ecol))
    tuma '', line_upto_token

#### Raw Output  ###########################################

eleza raw_highlight(classified_text):
    'Straight text display of text classifications'
    result = []
    kila kind, text kwenye classified_text:
        result.append('%15s:  %r\n' % (kind ama 'plain', text))
    rudisha ''.join(result)

#### ANSI Output ###########################################

default_ansi = {
    'comment': ('\033[0;31m', '\033[0m'),
    'string': ('\033[0;32m', '\033[0m'),
    'docstring': ('\033[0;32m', '\033[0m'),
    'keyword': ('\033[0;33m', '\033[0m'),
    'builtin': ('\033[0;35m', '\033[0m'),
    'definition': ('\033[0;33m', '\033[0m'),
    'defname': ('\033[0;34m', '\033[0m'),
    'operator': ('\033[0;33m', '\033[0m'),
}

eleza ansi_highlight(classified_text, colors=default_ansi):
    'Add syntax highlighting to source code using ANSI escape sequences'
    # http://en.wikipedia.org/wiki/ANSI_escape_code
    result = []
    kila kind, text kwenye classified_text:
        opener, closer = colors.get(kind, ('', ''))
        result += [opener, text, closer]
    rudisha ''.join(result)

#### HTML Output ###########################################

eleza html_highlight(classified_text,opener='<pre class="python">\n', closer='</pre>\n'):
    'Convert classified text to an HTML fragment'
    result = [opener]
    kila kind, text kwenye classified_text:
        ikiwa kind:
            result.append('<span class="%s">' % kind)
        result.append(html_module.escape(text))
        ikiwa kind:
            result.append('</span>')
    result.append(closer)
    rudisha ''.join(result)

default_css = {
    '.comment': '{color: crimson;}',
    '.string':  '{color: forestgreen;}',
    '.docstring': '{color: forestgreen; font-style:italic;}',
    '.keyword': '{color: darkorange;}',
    '.builtin': '{color: purple;}',
    '.definition': '{color: darkorange; font-weight:bold;}',
    '.defname': '{color: blue;}',
    '.operator': '{color: brown;}',
}

default_html = '''\
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
          "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<meta http-equiv="Content-type" content="text/html;charset=UTF-8">
<title> {title} </title>
<style type="text/css">
{css}
</style>
</head>
<body>
{body}
</body>
</html>
'''

eleza build_html_page(classified_text, title='python',
                    css=default_css, html=default_html):
    'Create a complete HTML page ukijumuisha colorized source code'
    css_str = '\n'.join(['%s %s' % item kila item kwenye css.items()])
    result = html_highlight(classified_text)
    title = html_module.escape(title)
    rudisha html.format(title=title, css=css_str, body=result)

#### LaTeX Output ##########################################

default_latex_commands = {
    'comment': r'{\color{red}#1}',
    'string': r'{\color{ForestGreen}#1}',
    'docstring': r'{\emph{\color{ForestGreen}#1}}',
    'keyword': r'{\color{orange}#1}',
    'builtin': r'{\color{purple}#1}',
    'definition': r'{\color{orange}#1}',
    'defname': r'{\color{blue}#1}',
    'operator': r'{\color{brown}#1}',
}

default_latex_document = r'''
\documentclass{article}
\usepackage{alltt}
\usepackage{upquote}
\usepackage{color}
\usepackage[usenames,dvipsnames]{xcolor}
\usepackage[cm]{fullpage}
%(macros)s
\begin{document}
\center{\LARGE{%(title)s}}
\begin{alltt}
%(body)s
\end{alltt}
\end{document}
'''

eleza alltt_escape(s):
    'Replace backslash na braces ukijumuisha their escaped equivalents'
    xlat = {'{': r'\{', '}': r'\}', '\\': r'\textbackslash{}'}
    rudisha re.sub(r'[\\{}]', lambda mo: xlat[mo.group()], s)

eleza latex_highlight(classified_text, title = 'python',
                    commands = default_latex_commands,
                    document = default_latex_document):
    'Create a complete LaTeX document ukijumuisha colorized source code'
    macros = '\n'.join(r'\newcommand{\py%s}[1]{%s}' % c kila c kwenye commands.items())
    result = []
    kila kind, text kwenye classified_text:
        ikiwa kind:
            result.append(r'\py%s{' % kind)
        result.append(alltt_escape(text))
        ikiwa kind:
            result.append('}')
    rudisha default_latex_document % dict(title=title, macros=macros, body=''.join(result))


ikiwa __name__ == '__main__':
    agiza argparse
    agiza os.path
    agiza sys
    agiza textwrap
    agiza webbrowser

    parser = argparse.ArgumentParser(
            description = 'Add syntax highlighting to Python source code',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog = textwrap.dedent('''
                examples:

                  # Show syntax highlighted code kwenye the terminal window
                  $ ./highlight.py myfile.py

                  # Colorize myfile.py na display kwenye a browser
                  $ ./highlight.py -b myfile.py

                  # Create an HTML section to embed kwenye an existing webpage
                  ./highlight.py -s myfile.py

                  # Create a complete HTML file
                  $ ./highlight.py -c myfile.py > myfile.html

                  # Create a PDF using LaTeX
                  $ ./highlight.py -l myfile.py | pdflatex

            '''))
    parser.add_argument('sourcefile', metavar = 'SOURCEFILE',
            help = 'file containing Python sourcecode')
    parser.add_argument('-b', '--browser', action = 'store_true',
            help = 'launch a browser to show results')
    parser.add_argument('-c', '--complete', action = 'store_true',
            help = 'build a complete html webpage')
    parser.add_argument('-l', '--latex', action = 'store_true',
            help = 'build a LaTeX document')
    parser.add_argument('-r', '--raw', action = 'store_true',
            help = 'raw parse of categorized text')
    parser.add_argument('-s', '--section', action = 'store_true',
            help = 'show an HTML section rather than a complete webpage')
    args = parser.parse_args()

    ikiwa args.section na (args.browser ama args.complete):
        parser.error('The -s/--section option ni incompatible ukijumuisha '
                     'the -b/--browser ama -c/--complete options')

    sourcefile = args.sourcefile
    ukijumuisha open(sourcefile) kama f:
        source = f.read()
    classified_text = analyze_python(source)

    ikiwa args.raw:
        encoded = raw_highlight(classified_text)
    lasivyo args.complete ama args.browser:
        encoded = build_html_page(classified_text, title=sourcefile)
    lasivyo args.section:
        encoded = html_highlight(classified_text)
    lasivyo args.latex:
        encoded = latex_highlight(classified_text, title=sourcefile)
    isipokua:
        encoded = ansi_highlight(classified_text)

    ikiwa args.browser:
        htmlfile = os.path.splitext(os.path.basename(sourcefile))[0] + '.html'
        ukijumuisha open(htmlfile, 'w') kama f:
            f.write(encoded)
        webbrowser.open('file://' + os.path.abspath(htmlfile))
    isipokua:
        sys.stdout.write(encoded)
