# tk common message boxes
#
# this module provides an interface to the native message boxes
# available kwenye Tk 4.2 na newer.
#
# written by Fredrik Lundh, May 1997
#

#
# options (all have default values):
#
# - default: which button to make default (one of the reply codes)
#
# - icon: which icon to display (see below)
#
# - message: the message to display
#
# - parent: which window to place the dialog on top of
#
# - title: dialog title
#
# - type: dialog type; that is, which buttons to display (see below)
#

kutoka tkinter.commondialog agiza Dialog

#
# constants

# icons
ERROR = "error"
INFO = "info"
QUESTION = "question"
WARNING = "warning"

# types
ABORTRETRYIGNORE = "abortretryignore"
OK = "ok"
OKCANCEL = "okcancel"
RETRYCANCEL = "retrycancel"
YESNO = "yesno"
YESNOCANCEL = "yesnocancel"

# replies
ABORT = "abort"
RETRY = "retry"
IGNORE = "ignore"
OK = "ok"
CANCEL = "cancel"
YES = "yes"
NO = "no"


#
# message dialog class

kundi Message(Dialog):
    "A message box"

    command  = "tk_messageBox"


#
# convenience stuff

# Rename _icon na _type options to allow overriding them kwenye options
eleza _show(title=Tupu, message=Tupu, _icon=Tupu, _type=Tupu, **options):
    ikiwa _icon na "icon" sio kwenye options:    options["icon"] = _icon
    ikiwa _type na "type" sio kwenye options:    options["type"] = _type
    ikiwa title:   options["title"] = title
    ikiwa message: options["message"] = message
    res = Message(**options).show()
    # In some Tcl installations, yes/no ni converted into a boolean.
    ikiwa isinstance(res, bool):
        ikiwa res:
            rudisha YES
        rudisha NO
    # In others we get a Tcl_Obj.
    rudisha str(res)


eleza showinfo(title=Tupu, message=Tupu, **options):
    "Show an info message"
    rudisha _show(title, message, INFO, OK, **options)


eleza showwarning(title=Tupu, message=Tupu, **options):
    "Show a warning message"
    rudisha _show(title, message, WARNING, OK, **options)


eleza showerror(title=Tupu, message=Tupu, **options):
    "Show an error message"
    rudisha _show(title, message, ERROR, OK, **options)


eleza askquestion(title=Tupu, message=Tupu, **options):
    "Ask a question"
    rudisha _show(title, message, QUESTION, YESNO, **options)


eleza askokcancel(title=Tupu, message=Tupu, **options):
    "Ask ikiwa operation should proceed; rudisha true ikiwa the answer ni ok"
    s = _show(title, message, QUESTION, OKCANCEL, **options)
    rudisha s == OK


eleza askyesno(title=Tupu, message=Tupu, **options):
    "Ask a question; rudisha true ikiwa the answer ni yes"
    s = _show(title, message, QUESTION, YESNO, **options)
    rudisha s == YES


eleza askyesnocancel(title=Tupu, message=Tupu, **options):
    "Ask a question; rudisha true ikiwa the answer ni yes, Tupu ikiwa cancelled."
    s = _show(title, message, QUESTION, YESNOCANCEL, **options)
    # s might be a Tcl index object, so convert it to a string
    s = str(s)
    ikiwa s == CANCEL:
        rudisha Tupu
    rudisha s == YES


eleza askretrycancel(title=Tupu, message=Tupu, **options):
    "Ask ikiwa operation should be retried; rudisha true ikiwa the answer ni yes"
    s = _show(title, message, WARNING, RETRYCANCEL, **options)
    rudisha s == RETRY


# --------------------------------------------------------------------
# test stuff

ikiwa __name__ == "__main__":

    andika("info", showinfo("Spam", "Egg Information"))
    andika("warning", showwarning("Spam", "Egg Warning"))
    andika("error", showerror("Spam", "Egg Alert"))
    andika("question", askquestion("Spam", "Question?"))
    andika("proceed", askokcancel("Spam", "Proceed?"))
    andika("yes/no", askyesno("Spam", "Got it?"))
    andika("yes/no/cancel", askyesnocancel("Spam", "Want it?"))
    andika("try again", askretrycancel("Spam", "Try again?"))
