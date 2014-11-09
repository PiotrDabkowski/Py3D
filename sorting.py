from collections import defaultdict
from itertools import combinations


def sort_sorted(a, b, is_greater):
    res = []
    i, j = 0, 0
    while i<len(a) and j<len(b):
        if is_greater(a[i], b[j]):
            res.append(b[j])
            j+=1
        else:
            res.append(a[i])
            i+=1
    return res+a[i:]+b[j:]

def expand_children(cdic, p, done={}, forbidden=[]):
    forbidden.append(p)
    new = set()
    for c in cdic[p]:
          if c in forbidden:
              raise Exception('Impossible to resolve!')
          if c in done:
              new = new.union(done[c])
          else:
              new= new.union(expand_children(cdic, c, done, forbidden[:]))
    done[p] = cdic[p].union(new)
    return done[p]


def expand_all_children(cdic):
    done = {}
    for p in cdic.keys():
        expand_children(cdic, p, done, [])
    return done

def merge_pattern(p1, p2):
    last_sync= 0
    pat = []
    p1poses = {v:k for k, v in enumerate(p1)}
    for e in p2:
        try:
            sync = p1poses[e]
            pat.extend(p1[last_sync:sync])
            last_sync = sync+1
        except:
            pass
        pat.append(e)
    pat.extend(p1[last_sync:])
    return pat
            
def check_conditions(res, gr, sm):
    dd = {v:k for k,v in enumerate(res)}
    for now in gr:
        inow = dd[now]
        if not all([inow<dd[e] for e in gr[now]]):
            raise Exception('Wrong')
        if not all([inow>dd[e] for e in sm[now]]):
            raise Exception('Wrong')
    print 'Correct!!!'

def gr_to_sm(gr):
    sm = defaultdict(set)
    for e in gr:
        for k in gr[e]:
            sm[k].add(e)
    return sm

def rc(gr):
    gr = expand_all_children(gr)
    sm = gr_to_sm(gr)
    r = resolve_children(gr, sm)
    print r
    check_conditions(r, gr, sm)


def resolve_children(gr, sm=None, poll=None):
    if sm is None:
        sm = gr_to_sm(gr)
    if poll is None:
        poll = set(sm.keys()+gr.keys())
    parentless = []
    for k in poll:
        if not gr[k].intersection(poll):
            parentless.append(k)
    if not parentless:
        raise Exception('Impossible to resolve!')
    left = []
    for p in parentless:
        children = sm[p]
        if len(children)>1:
            left.append(resolve_children(gr, sm, children))
        else:
            left.append(list(children))
    res = left[0]
    for e in left[1:]:
        res = merge_pattern(e, res)
    return res+parentless
        
    
            
def ssort(x, bigger):
    greater_than = defaultdict(set)
    smaller_than = defaultdict(set)
    for a,b in combinations(x, 2):
        det = bigger(a,b)
        if det==0:
            greater_than[b].add(a)
            smaller_than[a].add(b)
        elif det==1:
            greater_than[a].add(b)
            smaller_than[b].add(a)
    greater_than = expand_all_children(greater_than)
    smaller_than = expand_all_children(smaller_than)
    return greater_than, smaller_than

def dumb_sort(x, bigger=lambda a,b: 0 if a>b else (1 if b>a else -1)):
    gr, sm = ssort(x, bigger)
    return resolve_children(gr, sm, set(x))
    
    
def sort_groups(x, is_greater):
    while len(x)>1:
        s = [x[n:n+2] for n in xrange(0, len(x), 2)]
        n=0
        while n<len(s):
            if len(s[n])>1:
                s[n] = sort_sorted(s[n][0], s[n][1], is_greater)
            else:
                s[n] = s[n][0]
            n+=1
        x = s
    return x[0]

cmps = defaultdict(set)
def cmp_rec(a,b):
    global cmps
    if a>b:
        cmps[b].add(a)
        return True
    else:
        cmps[a].add(b)
        return False
    
def msort(x, is_greater=lambda a,b: a>b):
    s = [x[n:n+2] for n in xrange(0, len(x), 2)]
    for e in s:
        if len(e)>1 and not is_greater(e[1], e[0]):
            e.reverse()
    return sort_groups(s, is_greater)
