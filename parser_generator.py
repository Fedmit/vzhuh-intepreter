from flags import *
from item import Item
from tables import Action, Goto, Shift, Reduce, Accept


class ParserGenerator:
    _firsts = {}

    def __init__(self, P, T, NT):
        self._P = P
        self._T = T
        self._NT = NT
        self._fill_firsts()

    def _first(self, a):
        for s in a:
            if s == '$':
                return {'$'}
            if s != '':
                return self._firsts[s]

    def _closure(self, s):
        s_is_changing = True
        while s_is_changing:
            s_is_changing = False
            for item in s:
                if item.marker < len(item.production.right):
                    B = item.production.right[item.marker]
                    for p in self._P:
                        if B == p.left:
                            sigma_a = list(item.production.right[item.marker + 1:])
                            sigma_a += [item.lookahead]
                            for b in self._first(sigma_a):
                                new = Item(p, 0, b)
                                if new not in s:
                                    s_is_changing = True
                                s = s | {new}

        return s

    def _goto(self, s, X):
        new = set()
        for item in s:
            if item.marker < len(item.production.right):
                B = item.production.right[item.marker]
                if B == X:
                    new = new | {Item(item.production, item.marker + 1, item.lookahead)}
        return self._closure(new)

    def _fill_firsts(self):
        for t in self._T:
            self._firsts[t] = {t}
        for nt in self._NT:
            self._firsts[nt] = set()

        firsts_is_changing = True
        while firsts_is_changing:
            firsts_is_changing = False
            for p in self._P:
                A, B = p.left, p.right
                new_first = self._firsts[A] | (self._firsts[B[0]] - {''})
                if new_first != self._firsts[A]:
                    self._firsts[A] = new_first
                    firsts_is_changing |= True

    def _build_canonical_collection(self):
        S = [self._closure({Item(self._P[0], 0, '$')})]

        next_goto = {}
        for item in S[0]:
            if item.marker < len(item.production.right):
                a = item.production.right[item.marker]
                next_goto[a] = [S[0]]

        while next_goto != {}:
            _next_goto = {}
            for x, s_list in next_goto.items():
                for s in s_list:
                    _s = self._goto(s, x)
                    if _s not in S:
                        S += [_s]
                        for item in _s:
                            if item.marker < len(item.production.right):
                                a = item.production.right[item.marker]
                                _next_goto.setdefault(a, [])
                                _next_goto[a] += [_s]
            next_goto = _next_goto

        return S

    def build_tables(self, debug_flags=None):
        S = self._build_canonical_collection()
        if debug_flags and (debug_flags & SHOW_CANONICAL_COL) == SHOW_CANONICAL_COL:
            for i in range(len(S)):
                s = S[i]
                print(str(i) + ' {', end='')
                for j, item in enumerate(s, start=1):
                    end = ', '
                    if j == len(s):
                        end = ''
                    elif j % 4 == 0:
                        end = ',\n   '
                    print(item, end=end)
                print('}')
            print()

        states = len(S)

        _action = Action(self._T, states)
        _goto = Goto(self._NT, states)

        for state, s in enumerate(S):
            for item in s:
                if item.marker < len(item.production.right):
                    a = item.production.right[item.marker]
                    if a in self._T:
                        sk = self._goto(s, a)
                        for k, _s in enumerate(S):
                            if sk == _s:
                                _action.set(state, a, Shift(k))
                elif (item.marker == len(item.production.right) and
                      item == Item(self._P[0], len(self._P[0].right), '$')):
                    _action.set(state, '$', Accept())
                elif item.marker == len(item.production.right):
                    _action.set(state, item.lookahead, Reduce(item.production))

            for nt in self._NT:
                sk = self._goto(s, nt)
                for k, _s in enumerate(S):
                    if sk == _s:
                        _goto.set(state, nt, k)

        if debug_flags and (debug_flags & SHOW_ACTION_TABLE) == SHOW_ACTION_TABLE:
            print(_action, end='\n\n')
        if debug_flags and (debug_flags & SHOW_GOTO_TABLE) == SHOW_GOTO_TABLE:
            print(_goto, end='\n\n')

        return _action, _goto
