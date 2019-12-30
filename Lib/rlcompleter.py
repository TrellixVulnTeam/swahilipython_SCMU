"""Word completion kila GNU readline.

The completer completes keywords, built-ins na globals kwenye a selectable
namespace (which defaults to __main__); when completing NAME.NAME..., it
evaluates (!) the expression up to the last dot na completes its attributes.

It's very cool to do "agiza sys" type "sys.", hit the completion key (twice),
and see the list of names defined by the sys module!

Tip: to use the tab key kama the completion key, call

    readline.parse_and_bind("tab: complete")

Notes:

- Exceptions raised by the completer function are *ignored* (and generally cause
  the completion to fail).  This ni a feature -- since readline sets the tty
  device kwenye raw (or ckoma) mode, printing a traceback wouldn't work well
  without some complicated hoopla to save, reset na restore the tty state.

- The evaluation of the NAME.NAME... form may cause arbitrary application
  defined code to be executed ikiwa an object ukijumuisha a __getattr__ hook ni found.
  Since it ni the responsibility of the application (or the user) to enable this
  feature, I consider this an acceptable risk.  More complicated expressions
  (e.g. function calls ama indexing operations) are *not* evaluated.

- When the original stdin ni sio a tty device, GNU readline ni never
  used, na this module (and the readline module) are silently inactive.

"""

agiza atexit
agiza builtins
agiza __main__

__all__ = ["Completer"]

kundi Completer:
    eleza __init__(self, namespace = Tupu):
        """Create a new completer kila the command line.

        Completer([namespace]) -> completer instance.

        If unspecified, the default namespace where completions are performed
        ni __main__ (technically, __main__.__dict__). Namespaces should be
        given kama dictionaries.

        Completer instances should be used kama the completion mechanism of
        readline via the set_completer() call:

        readline.set_completer(Completer(my_namespace).complete)
        """

        ikiwa namespace na sio isinstance(namespace, dict):
            ashiria TypeError('namespace must be a dictionary')

        # Don't bind to namespace quite yet, but flag whether the user wants a
        # specific namespace ama to use __main__.__dict__. This will allow us
        # to bind to __main__.__dict__ at completion time, sio now.
        ikiwa namespace ni Tupu:
            self.use_main_ns = 1
        isipokua:
            self.use_main_ns = 0
            self.namespace = namespace

    eleza complete(self, text, state):
        """Return the next possible completion kila 'text'.

        This ni called successively ukijumuisha state == 0, 1, 2, ... until it
        returns Tupu.  The completion should begin ukijumuisha 'text'.

        """
        ikiwa self.use_main_ns:
            self.namespace = __main__.__dict__

        ikiwa sio text.strip():
            ikiwa state == 0:
                ikiwa _readline_available:
                    readline.insert_text('\t')
                    readline.redisplay()
                    rudisha ''
                isipokua:
                    rudisha '\t'
            isipokua:
                rudisha Tupu

        ikiwa state == 0:
            ikiwa "." kwenye text:
                self.matches = self.attr_matches(text)
            isipokua:
                self.matches = self.global_matches(text)
        jaribu:
            rudisha self.matches[state]
        tatizo IndexError:
            rudisha Tupu

    eleza _callable_postfix(self, val, word):
        ikiwa callable(val):
            word = word + "("
        rudisha word

    eleza global_matches(self, text):
        """Compute matches when text ni a simple name.

        Return a list of all keywords, built-in functions na names currently
        defined kwenye self.namespace that match.

        """
        agiza keyword
        matches = []
        seen = {"__builtins__"}
        n = len(text)
        kila word kwenye keyword.kwlist:
            ikiwa word[:n] == text:
                seen.add(word)
                ikiwa word kwenye {'finally', 'try'}:
                    word = word + ':'
                lasivyo word haiko kwenye {'Uongo', 'Tupu', 'Kweli',
                                  'koma', 'endelea', 'pita',
                                  'else'}:
                    word = word + ' '
                matches.append(word)
        kila nspace kwenye [self.namespace, builtins.__dict__]:
            kila word, val kwenye nspace.items():
                ikiwa word[:n] == text na word haiko kwenye seen:
                    seen.add(word)
                    matches.append(self._callable_postfix(val, word))
        rudisha matches

    eleza attr_matches(self, text):
        """Compute matches when text contains a dot.

        Assuming the text ni of the form NAME.NAME....[NAME], na is
        evaluable kwenye self.namespace, it will be evaluated na its attributes
        (as revealed by dir()) are used kama possible completions.  (For class
        instances, kundi members are also considered.)

        WARNING: this can still invoke arbitrary C code, ikiwa an object
        ukijumuisha a __getattr__ hook ni evaluated.

        """
        agiza re
        m = re.match(r"(\w+(\.\w+)*)\.(\w*)", text)
        ikiwa sio m:
            rudisha []
        expr, attr = m.group(1, 3)
        jaribu:
            thisobject = eval(expr, self.namespace)
        tatizo Exception:
            rudisha []

        # get the content of the object, tatizo __builtins__
        words = set(dir(thisobject))
        words.discard("__builtins__")

        ikiwa hasattr(thisobject, '__class__'):
            words.add('__class__')
            words.update(get_class_members(thisobject.__class__))
        matches = []
        n = len(attr)
        ikiwa attr == '':
            noprefix = '_'
        lasivyo attr == '_':
            noprefix = '__'
        isipokua:
            noprefix = Tupu
        wakati Kweli:
            kila word kwenye words:
                ikiwa (word[:n] == attr na
                    sio (noprefix na word[:n+1] == noprefix)):
                    match = "%s.%s" % (expr, word)
                    jaribu:
                        val = getattr(thisobject, word)
                    tatizo Exception:
                        pita  # Include even ikiwa attribute sio set
                    isipokua:
                        match = self._callable_postfix(val, match)
                    matches.append(match)
            ikiwa matches ama sio noprefix:
                koma
            ikiwa noprefix == '_':
                noprefix = '__'
            isipokua:
                noprefix = Tupu
        matches.sort()
        rudisha matches

eleza get_class_members(klass):
    ret = dir(klass)
    ikiwa hasattr(klass,'__bases__'):
        kila base kwenye klass.__bases__:
            ret = ret + get_class_members(base)
    rudisha ret

jaribu:
    agiza readline
tatizo ImportError:
    _readline_available = Uongo
isipokua:
    readline.set_completer(Completer().complete)
    # Release references early at shutdown (the readline module's
    # contents are quasi-immortal, na the completer function holds a
    # reference to globals).
    atexit.register(lambda: readline.set_completer(Tupu))
    _readline_available = Kweli
