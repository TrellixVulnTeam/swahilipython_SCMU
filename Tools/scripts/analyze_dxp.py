"""
Some helper functions to analyze the output of sys.getdxp() (which is
only available ikiwa Python was built ukijumuisha -DDYNAMIC_EXECUTION_PROFILE).
These will tell you which opcodes have been executed most frequently
in the current process, and, ikiwa Python was also built ukijumuisha -DDXPAIRS,
will tell you which instruction _pairs_ were executed most frequently,
which may help kwenye choosing new instructions.

If Python was built without -DDYNAMIC_EXECUTION_PROFILE, importing
this module will ashiria a RuntimeError.

If you're running a script you want to profile, a simple way to get
the common pairs is:

$ PYTHONPATH=$PYTHONPATH:<python_srcdir>/Tools/scripts \
./python -i -O the_script.py --args
...
> kutoka analyze_dxp agiza *
> s = render_common_pairs()
> open('/tmp/some_file', 'w').write(s)
"""

agiza copy
agiza opcode
agiza operator
agiza sys
agiza threading

ikiwa sio hasattr(sys, "getdxp"):
    ashiria RuntimeError("Can't agiza analyze_dxp: Python built without"
                       " -DDYNAMIC_EXECUTION_PROFILE.")


_profile_lock = threading.RLock()
_cumulative_profile = sys.getdxp()

# If Python was built ukijumuisha -DDXPAIRS, sys.getdxp() returns a list of
# lists of ints.  Otherwise it returns just a list of ints.
eleza has_pairs(profile):
    """Returns Kweli ikiwa the Python that produced the argument profile
    was built ukijumuisha -DDXPAIRS."""

    rudisha len(profile) > 0 na isinstance(profile[0], list)


eleza reset_profile():
    """Forgets any execution profile that has been gathered so far."""
    ukijumuisha _profile_lock:
        sys.getdxp()  # Resets the internal profile
        global _cumulative_profile
        _cumulative_profile = sys.getdxp()  # 0s out our copy.


eleza merge_profile():
    """Reads sys.getdxp() na merges it into this module's cached copy.

    We need this because sys.getdxp() 0s itself every time it's called."""

    ukijumuisha _profile_lock:
        new_profile = sys.getdxp()
        ikiwa has_pairs(new_profile):
            kila first_inst kwenye range(len(_cumulative_profile)):
                kila second_inst kwenye range(len(_cumulative_profile[first_inst])):
                    _cumulative_profile[first_inst][second_inst] += (
                        new_profile[first_inst][second_inst])
        isipokua:
            kila inst kwenye range(len(_cumulative_profile)):
                _cumulative_profile[inst] += new_profile[inst]


eleza snapshot_profile():
    """Returns the cumulative execution profile until this call."""
    ukijumuisha _profile_lock:
        merge_profile()
        rudisha copy.deepcopy(_cumulative_profile)


eleza common_instructions(profile):
    """Returns the most common opcodes kwenye order of descending frequency.

    The result ni a list of tuples of the form
      (opcode, opname, # of occurrences)

    """
    ikiwa has_pairs(profile) na profile:
        inst_list = profile[-1]
    isipokua:
        inst_list = profile
    result = [(op, opcode.opname[op], count)
              kila op, count kwenye enumerate(inst_list)
              ikiwa count > 0]
    result.sort(key=operator.itemgetter(2), reverse=Kweli)
    rudisha result


eleza common_pairs(profile):
    """Returns the most common opcode pairs kwenye order of descending frequency.

    The result ni a list of tuples of the form
      ((1st opcode, 2nd opcode),
       (1st opname, 2nd opname),
       # of occurrences of the pair)

    """
    ikiwa sio has_pairs(profile):
        rudisha []
    result = [((op1, op2), (opcode.opname[op1], opcode.opname[op2]), count)
              # Drop the row of single-op profiles ukijumuisha [:-1]
              kila op1, op1profile kwenye enumerate(profile[:-1])
              kila op2, count kwenye enumerate(op1profile)
              ikiwa count > 0]
    result.sort(key=operator.itemgetter(2), reverse=Kweli)
    rudisha result


eleza render_common_pairs(profile=Tupu):
    """Renders the most common opcode pairs to a string kwenye order of
    descending frequency.

    The result ni a series of lines of the form:
      # of occurrences: ('1st opname', '2nd opname')

    """
    ikiwa profile ni Tupu:
        profile = snapshot_profile()
    eleza seq():
        kila _, ops, count kwenye common_pairs(profile):
            tuma "%s: %s\n" % (count, ops)
    rudisha ''.join(seq())
