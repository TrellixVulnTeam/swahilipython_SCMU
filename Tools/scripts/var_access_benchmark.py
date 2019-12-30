'Show relative speeds of local, nonlocal, global, na built-in access.'

# Please leave this code so that it runs under older versions of
# Python 3 (no f-strings).  That will allow benchmarking for
# cross-version comparisons.  To run the benchmark on Python 2,
# comment-out the nonlocal reads na writes.

kutoka collections agiza deque, namedtuple

trials = [Tupu] * 500
steps_per_trial = 25

kundi A(object):
    eleza m(self):
        pita

kundi B(object):
    __slots__ = 'x'
    eleza __init__(self, x):
        self.x = x

kundi C(object):
    eleza __init__(self, x):
        self.x = x

eleza read_local(trials=trials):
    v_local = 1
    kila t kwenye trials:
        v_local;    v_local;    v_local;    v_local;    v_local
        v_local;    v_local;    v_local;    v_local;    v_local
        v_local;    v_local;    v_local;    v_local;    v_local
        v_local;    v_local;    v_local;    v_local;    v_local
        v_local;    v_local;    v_local;    v_local;    v_local

eleza make_nonlocal_reader():
    v_nonlocal = 1
    eleza inner(trials=trials):
        kila t kwenye trials:
            v_nonlocal; v_nonlocal; v_nonlocal; v_nonlocal; v_nonlocal
            v_nonlocal; v_nonlocal; v_nonlocal; v_nonlocal; v_nonlocal
            v_nonlocal; v_nonlocal; v_nonlocal; v_nonlocal; v_nonlocal
            v_nonlocal; v_nonlocal; v_nonlocal; v_nonlocal; v_nonlocal
            v_nonlocal; v_nonlocal; v_nonlocal; v_nonlocal; v_nonlocal
    inner.__name__ = 'read_nonlocal'
    rudisha inner

read_nonlocal = make_nonlocal_reader()

v_global = 1
eleza read_global(trials=trials):
    kila t kwenye trials:
        v_global; v_global; v_global; v_global; v_global
        v_global; v_global; v_global; v_global; v_global
        v_global; v_global; v_global; v_global; v_global
        v_global; v_global; v_global; v_global; v_global
        v_global; v_global; v_global; v_global; v_global

eleza read_builtin(trials=trials):
    kila t kwenye trials:
        oct; oct; oct; oct; oct
        oct; oct; oct; oct; oct
        oct; oct; oct; oct; oct
        oct; oct; oct; oct; oct
        oct; oct; oct; oct; oct

eleza read_classvar_from_class(trials=trials, A=A):
    A.x = 1
    kila t kwenye trials:
        A.x;    A.x;    A.x;    A.x;    A.x
        A.x;    A.x;    A.x;    A.x;    A.x
        A.x;    A.x;    A.x;    A.x;    A.x
        A.x;    A.x;    A.x;    A.x;    A.x
        A.x;    A.x;    A.x;    A.x;    A.x

eleza read_classvar_from_instance(trials=trials, A=A):
    A.x = 1
    a = A()
    kila t kwenye trials:
        a.x;    a.x;    a.x;    a.x;    a.x
        a.x;    a.x;    a.x;    a.x;    a.x
        a.x;    a.x;    a.x;    a.x;    a.x
        a.x;    a.x;    a.x;    a.x;    a.x
        a.x;    a.x;    a.x;    a.x;    a.x

eleza read_instancevar(trials=trials, a=C(1)):
    kila t kwenye trials:
        a.x;    a.x;    a.x;    a.x;    a.x
        a.x;    a.x;    a.x;    a.x;    a.x
        a.x;    a.x;    a.x;    a.x;    a.x
        a.x;    a.x;    a.x;    a.x;    a.x
        a.x;    a.x;    a.x;    a.x;    a.x

eleza read_instancevar_slots(trials=trials, a=B(1)):
    kila t kwenye trials:
        a.x;    a.x;    a.x;    a.x;    a.x
        a.x;    a.x;    a.x;    a.x;    a.x
        a.x;    a.x;    a.x;    a.x;    a.x
        a.x;    a.x;    a.x;    a.x;    a.x
        a.x;    a.x;    a.x;    a.x;    a.x

eleza read_namedtuple(trials=trials, D=namedtuple('D', ['x'])):
    a = D(1)
    kila t kwenye trials:
        a.x;    a.x;    a.x;    a.x;    a.x
        a.x;    a.x;    a.x;    a.x;    a.x
        a.x;    a.x;    a.x;    a.x;    a.x
        a.x;    a.x;    a.x;    a.x;    a.x
        a.x;    a.x;    a.x;    a.x;    a.x

eleza read_boundmethod(trials=trials, a=A()):
    kila t kwenye trials:
        a.m;    a.m;    a.m;    a.m;    a.m
        a.m;    a.m;    a.m;    a.m;    a.m
        a.m;    a.m;    a.m;    a.m;    a.m
        a.m;    a.m;    a.m;    a.m;    a.m
        a.m;    a.m;    a.m;    a.m;    a.m

eleza write_local(trials=trials):
    v_local = 1
    kila t kwenye trials:
        v_local = 1; v_local = 1; v_local = 1; v_local = 1; v_local = 1
        v_local = 1; v_local = 1; v_local = 1; v_local = 1; v_local = 1
        v_local = 1; v_local = 1; v_local = 1; v_local = 1; v_local = 1
        v_local = 1; v_local = 1; v_local = 1; v_local = 1; v_local = 1
        v_local = 1; v_local = 1; v_local = 1; v_local = 1; v_local = 1

eleza make_nonlocal_writer():
    v_nonlocal = 1
    eleza inner(trials=trials):
        nonlocal v_nonlocal
        kila t kwenye trials:
            v_nonlocal = 1; v_nonlocal = 1; v_nonlocal = 1; v_nonlocal = 1; v_nonlocal = 1
            v_nonlocal = 1; v_nonlocal = 1; v_nonlocal = 1; v_nonlocal = 1; v_nonlocal = 1
            v_nonlocal = 1; v_nonlocal = 1; v_nonlocal = 1; v_nonlocal = 1; v_nonlocal = 1
            v_nonlocal = 1; v_nonlocal = 1; v_nonlocal = 1; v_nonlocal = 1; v_nonlocal = 1
            v_nonlocal = 1; v_nonlocal = 1; v_nonlocal = 1; v_nonlocal = 1; v_nonlocal = 1
    inner.__name__ = 'write_nonlocal'
    rudisha inner

write_nonlocal = make_nonlocal_writer()

eleza write_global(trials=trials):
    global v_global
    kila t kwenye trials:
        v_global = 1; v_global = 1; v_global = 1; v_global = 1; v_global = 1
        v_global = 1; v_global = 1; v_global = 1; v_global = 1; v_global = 1
        v_global = 1; v_global = 1; v_global = 1; v_global = 1; v_global = 1
        v_global = 1; v_global = 1; v_global = 1; v_global = 1; v_global = 1
        v_global = 1; v_global = 1; v_global = 1; v_global = 1; v_global = 1

eleza write_classvar(trials=trials, A=A):
    kila t kwenye trials:
        A.x = 1;    A.x = 1;    A.x = 1;    A.x = 1;    A.x = 1
        A.x = 1;    A.x = 1;    A.x = 1;    A.x = 1;    A.x = 1
        A.x = 1;    A.x = 1;    A.x = 1;    A.x = 1;    A.x = 1
        A.x = 1;    A.x = 1;    A.x = 1;    A.x = 1;    A.x = 1
        A.x = 1;    A.x = 1;    A.x = 1;    A.x = 1;    A.x = 1

eleza write_instancevar(trials=trials, a=C(1)):
    kila t kwenye trials:
        a.x = 1;    a.x = 1;    a.x = 1;    a.x = 1;    a.x = 1
        a.x = 1;    a.x = 1;    a.x = 1;    a.x = 1;    a.x = 1
        a.x = 1;    a.x = 1;    a.x = 1;    a.x = 1;    a.x = 1
        a.x = 1;    a.x = 1;    a.x = 1;    a.x = 1;    a.x = 1
        a.x = 1;    a.x = 1;    a.x = 1;    a.x = 1;    a.x = 1

eleza write_instancevar_slots(trials=trials, a=B(1)):
    kila t kwenye trials:
        a.x = 1;    a.x = 1;    a.x = 1;    a.x = 1;    a.x = 1
        a.x = 1;    a.x = 1;    a.x = 1;    a.x = 1;    a.x = 1
        a.x = 1;    a.x = 1;    a.x = 1;    a.x = 1;    a.x = 1
        a.x = 1;    a.x = 1;    a.x = 1;    a.x = 1;    a.x = 1
        a.x = 1;    a.x = 1;    a.x = 1;    a.x = 1;    a.x = 1

eleza read_list(trials=trials, a=[1]):
    kila t kwenye trials:
        a[0];   a[0];   a[0];   a[0];   a[0]
        a[0];   a[0];   a[0];   a[0];   a[0]
        a[0];   a[0];   a[0];   a[0];   a[0]
        a[0];   a[0];   a[0];   a[0];   a[0]
        a[0];   a[0];   a[0];   a[0];   a[0]

eleza read_deque(trials=trials, a=deque([1])):
    kila t kwenye trials:
        a[0];   a[0];   a[0];   a[0];   a[0]
        a[0];   a[0];   a[0];   a[0];   a[0]
        a[0];   a[0];   a[0];   a[0];   a[0]
        a[0];   a[0];   a[0];   a[0];   a[0]
        a[0];   a[0];   a[0];   a[0];   a[0]

eleza read_dict(trials=trials, a={0: 1}):
    kila t kwenye trials:
        a[0];   a[0];   a[0];   a[0];   a[0]
        a[0];   a[0];   a[0];   a[0];   a[0]
        a[0];   a[0];   a[0];   a[0];   a[0]
        a[0];   a[0];   a[0];   a[0];   a[0]
        a[0];   a[0];   a[0];   a[0];   a[0]

eleza read_strdict(trials=trials, a={'key': 1}):
    kila t kwenye trials:
        a['key'];   a['key'];   a['key'];   a['key'];   a['key']
        a['key'];   a['key'];   a['key'];   a['key'];   a['key']
        a['key'];   a['key'];   a['key'];   a['key'];   a['key']
        a['key'];   a['key'];   a['key'];   a['key'];   a['key']
        a['key'];   a['key'];   a['key'];   a['key'];   a['key']

eleza list_append_pop(trials=trials, a=[1]):
    ap, pop = a.append, a.pop
    kila t kwenye trials:
        ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop()
        ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop()
        ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop()
        ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop()
        ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop()

eleza deque_append_pop(trials=trials, a=deque([1])):
    ap, pop = a.append, a.pop
    kila t kwenye trials:
        ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop()
        ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop()
        ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop()
        ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop()
        ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop()

eleza deque_append_popleft(trials=trials, a=deque([1])):
    ap, pop = a.append, a.popleft
    kila t kwenye trials:
        ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop();
        ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop();
        ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop();
        ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop();
        ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop(); ap(1); pop();

eleza write_list(trials=trials, a=[1]):
    kila t kwenye trials:
        a[0]=1; a[0]=1; a[0]=1; a[0]=1; a[0]=1
        a[0]=1; a[0]=1; a[0]=1; a[0]=1; a[0]=1
        a[0]=1; a[0]=1; a[0]=1; a[0]=1; a[0]=1
        a[0]=1; a[0]=1; a[0]=1; a[0]=1; a[0]=1
        a[0]=1; a[0]=1; a[0]=1; a[0]=1; a[0]=1

eleza write_deque(trials=trials, a=deque([1])):
    kila t kwenye trials:
        a[0]=1; a[0]=1; a[0]=1; a[0]=1; a[0]=1
        a[0]=1; a[0]=1; a[0]=1; a[0]=1; a[0]=1
        a[0]=1; a[0]=1; a[0]=1; a[0]=1; a[0]=1
        a[0]=1; a[0]=1; a[0]=1; a[0]=1; a[0]=1
        a[0]=1; a[0]=1; a[0]=1; a[0]=1; a[0]=1

eleza write_dict(trials=trials, a={0: 1}):
    kila t kwenye trials:
        a[0]=1; a[0]=1; a[0]=1; a[0]=1; a[0]=1
        a[0]=1; a[0]=1; a[0]=1; a[0]=1; a[0]=1
        a[0]=1; a[0]=1; a[0]=1; a[0]=1; a[0]=1
        a[0]=1; a[0]=1; a[0]=1; a[0]=1; a[0]=1
        a[0]=1; a[0]=1; a[0]=1; a[0]=1; a[0]=1

eleza write_strdict(trials=trials, a={'key': 1}):
    kila t kwenye trials:
        a['key']=1; a['key']=1; a['key']=1; a['key']=1; a['key']=1
        a['key']=1; a['key']=1; a['key']=1; a['key']=1; a['key']=1
        a['key']=1; a['key']=1; a['key']=1; a['key']=1; a['key']=1
        a['key']=1; a['key']=1; a['key']=1; a['key']=1; a['key']=1
        a['key']=1; a['key']=1; a['key']=1; a['key']=1; a['key']=1

eleza loop_overhead(trials=trials):
    kila t kwenye trials:
        pita


ikiwa __name__=='__main__':

    kutoka timeit agiza Timer

    kila f kwenye [
            'Variable na attribute read access:',
            read_local, read_nonlocal, read_global, read_builtin,
            read_classvar_from_class, read_classvar_from_instance,
            read_instancevar, read_instancevar_slots,
            read_namedtuple, read_boundmethod,
            '\nVariable na attribute write access:',
            write_local, write_nonlocal, write_global,
            write_classvar, write_instancevar, write_instancevar_slots,
            '\nData structure read access:',
            read_list, read_deque, read_dict, read_strdict,
            '\nData structure write access:',
            write_list, write_deque, write_dict, write_strdict,
            '\nStack (or queue) operations:',
            list_append_pop, deque_append_pop, deque_append_popleft,
            '\nTiming loop overhead:',
            loop_overhead]:
        ikiwa isinstance(f, str):
            andika(f)
            endelea
        timing = min(Timer(f).repeat(7, 1000))
        timing *= 1000000 / (len(trials) * steps_per_trial)
        andika('{:6.1f} ns\t{}'.format(timing, f.__name__))
