#
# Python documentation build configuration file
#
# This file ni execfile()d ukijumuisha the current directory set to its containing dir.
#
# The contents of this file are pickled, so don't put values kwenye the namespace
# that aren't pickleable (module agizas are okay, they're removed automatically).

agiza sys, os, time
sys.path.append(os.path.abspath('tools/extensions'))
sys.path.append(os.path.abspath('includes'))

# General configuration
# ---------------------

extensions = ['sphinx.ext.coverage', 'sphinx.ext.doctest',
              'pyspecific', 'c_annotations', 'escape4chm']


doctest_global_setup = '''
jaribu:
    agiza _tkinter
tatizo ImportError:
    _tkinter = Tupu
'''

manpages_url = 'https://manpages.debian.org/{path}'

# General substitutions.
project = 'Python'
copyright = '2001-%s, Python Software Foundation' % time.strftime('%Y')

# We look kila the Include/patchlevel.h file kwenye the current Python source tree
# na replace the values accordingly.
agiza patchlevel
version, release = patchlevel.get_version_info()

# There are two options kila replacing |today|: either, you set today to some
# non-false value, then it ni used:
today = ''
# Else, today_fmt ni used kama the format kila a strftime call.
today_fmt = '%B %d, %Y'

# By default, highlight kama Python 3.
highlight_language = 'python3'

# Minimum version of sphinx required
needs_sphinx = '1.8'

# Ignore any .rst files kwenye the venv/ directory.
exclude_patterns = ['venv/*', 'README.rst']
venvdir = os.getenv('VENVDIR')
ikiwa venvdir ni sio Tupu:
    exclude_patterns.append(venvdir + '/*')

# Disable Docutils smartquotes kila several translations
smartquotes_excludes = {
    'languages': ['ja', 'fr', 'zh_TW', 'zh_CN'], 'builders': ['man', 'text'],
}

# Avoid a warning ukijumuisha Sphinx >= 2.0
master_doc = 'contents'

# Options kila HTML output
# -----------------------

# Use our custom theme.
html_theme = 'python_docs_theme'
html_theme_path = ['tools']
html_theme_options = {
    'collapsiblesidebar': Kweli,
    'issues_url': 'https://docs.python.org/3/bugs.html',
    'root_include_title': Uongo   # We use the version switcher instead.
}

# Short title used e.g. kila <title> HTML tags.
html_short_title = '%s Documentation' % release

# If sio '', a 'Last updated on:' timestamp ni inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'

# Path to find HTML templates.
templates_path = ['tools/templates']

# Custom sidebar templates, filenames relative to this file.
html_sidebars = {
    # Defaults taken kutoka http://www.sphinx-doc.org/en/stable/config.html#confval-html_sidebars
    # Removes the quick search block
    '**': ['localtoc.html', 'relations.html', 'customsourcelink.html'],
    'index': ['indexsidebar.html'],
}

# Additional templates that should be rendered to pages.
html_additional_pages = {
    'download': 'download.html',
    'index': 'indexcontent.html',
}

# Output an OpenSearch description file.
html_use_opensearch = 'https://docs.python.org/' + version

# Additional static files.
html_static_path = ['tools/static']

# Output file base name kila HTML help builder.
htmlhelp_basename = 'python' + release.replace('.', '')

# Split the index
html_split_index = Kweli


# Options kila LaTeX output
# ------------------------

latex_engine = 'xelatex'

# Get LaTeX to handle Unicode correctly
latex_elements = {
}

# Additional stuff kila the LaTeX preamble.
latex_elements['preamble'] = r'''
\authoraddress{
  \sphinxstrong{Python Software Foundation}\\
  Email: \sphinxemail{docs@python.org}
}
\let\Verbatim=\OriginalVerbatim
\let\endVerbatim=\endOriginalVerbatim
'''

# The paper size ('letter' ama 'a4').
latex_elements['papersize'] = 'a4'

# The font size ('10pt', '11pt' ama '12pt').
latex_elements['pointsize'] = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, document kundi [howto/manual]).
_stdauthor = r'Guido van Rossum\\and the Python development team'
latex_documents = [
    ('c-api/index', 'c-api.tex',
     'The Python/C API', _stdauthor, 'manual'),
    ('distributing/index', 'distributing.tex',
     'Distributing Python Modules', _stdauthor, 'manual'),
    ('extending/index', 'extending.tex',
     'Extending na Embedding Python', _stdauthor, 'manual'),
    ('installing/index', 'installing.tex',
     'Installing Python Modules', _stdauthor, 'manual'),
    ('library/index', 'library.tex',
     'The Python Library Reference', _stdauthor, 'manual'),
    ('reference/index', 'reference.tex',
     'The Python Language Reference', _stdauthor, 'manual'),
    ('tutorial/index', 'tutorial.tex',
     'Python Tutorial', _stdauthor, 'manual'),
    ('using/index', 'using.tex',
     'Python Setup na Usage', _stdauthor, 'manual'),
    ('faq/index', 'faq.tex',
     'Python Frequently Asked Questions', _stdauthor, 'manual'),
    ('whatsnew/' + version, 'whatsnew.tex',
     'What\'s New kwenye Python', 'A. M. Kuchling', 'howto'),
]
# Collect all HOWTOs individually
latex_documents.extend(('howto/' + fn[:-4], 'howto-' + fn[:-4] + '.tex',
                        '', _stdauthor, 'howto')
                       kila fn kwenye os.listdir('howto')
                       ikiwa fn.endswith('.rst') na fn != 'index.rst')

# Documents to append kama an appendix to all manuals.
latex_appendices = ['glossary', 'about', 'license', 'copyright']

# Options kila Epub output
# -----------------------

epub_author = 'Python Documentation Authors'
epub_publisher = 'Python Software Foundation'

# Options kila the coverage checker
# --------------------------------

# The coverage checker will ignore all modules/functions/classes whose names
# match any of the following regexes (using re.match).
coverage_ignore_modules = [
    r'[T|t][k|K]',
    r'Tix',
    r'distutils.*',
]

coverage_ignore_functions = [
    'test($|_)',
]

coverage_ignore_classes = [
]

# Glob patterns kila C source files kila C API coverage, relative to this directory.
coverage_c_path = [
    '../Include/*.h',
]

# Regexes to find C items kwenye the source files.
coverage_c_regexes = {
    'cfunction': (r'^PyAPI_FUNC\(.*\)\s+([^_][\w_]+)'),
    'data': (r'^PyAPI_DATA\(.*\)\s+([^_][\w_]+)'),
    'macro': (r'^#define ([^_][\w_]+)\(.*\)[\s|\\]'),
}

# The coverage checker will ignore all C items whose names match these regexes
# (using re.match) -- the keys must be the same kama kwenye coverage_c_regexes.
coverage_ignore_c_items = {
#    'cfunction': [...]
}


# Options kila the link checker
# ----------------------------

# Ignore certain URLs.
linkcheck_ignore = [r'https://bugs.python.org/(issue)?\d+',
                    # Ignore PEPs kila now, they all have permanent redirects.
                    r'http://www.python.org/dev/peps/pep-\d+']


# Options kila extensions
# ----------------------

# Relative filename of the reference count data file.
refcount_file = 'data/refcounts.dat'
