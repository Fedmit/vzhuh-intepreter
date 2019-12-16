import functools
from datetime import datetime

import dill
import os

from flags import *
from tables import *
from item import Item


class ParserGenerator:
    _first = {}

    def __init__(self, P, T, NT):
        self._P = P
        self._T = T
        self._NT = NT
        self._build_first()

    def _closure(self, s):
        s_is_changing = True
        while s_is_changing:
            s_is_changing = False
            for item in s:
                if item.marker < len(item.p.rhs):
                    for p in self._P:
                        if item.p.rhs[item.marker] == p.lhs:
                            sigma_a = list(item.p.rhs[item.marker + 1:])
                            sigma_a += [item.lookahead]
                            for b in self._first[sigma_a[0]]:
                                new = Item(p, 0, b)
                                if new not in s:
                                    s_is_changing = True
                                s = s | {new}

        return frozenset(s)

    @functools.lru_cache(maxsize=4096)
    def _goto(self, s, X):
        new = set()
        for item in s:
            if item.marker < len(item.p.rhs):
                B = item.p.rhs[item.marker]
                if B == X:
                    new = new | {Item(item.p, item.marker + 1, item.lookahead)}
        return self._closure(new)

    def _build_first(self):
        for t in self._T:
            self._first[t] = {t}
        for nt in self._NT:
            self._first[nt] = set()
        self._first['$'] = {'$'}

        firsts_is_changing = True
        while firsts_is_changing:
            firsts_is_changing = False
            for p in self._P:
                A, B = p.lhs, p.rhs
                new_first = self._first[A] | self._first[B[0]]
                if new_first != self._first[A]:
                    self._first[A] = new_first
                    firsts_is_changing |= True

    def _build_canonical_collection(self):
        S = [self._closure({Item(self._P[0], 0, '$')})]

        next_goto = {}
        for item in S[0]:
            if item.marker < len(item.p.rhs):
                a = item.p.rhs[item.marker]
                next_goto[a] = [S[0]]

        while next_goto != {}:
            _next_goto = {}
            for x, s_list in next_goto.items():
                for s in s_list:
                    _s = self._goto(s, x)
                    if _s not in S:
                        S += [_s]
                        for item in _s:
                            if item.marker < len(item.p.rhs):
                                a = item.p.rhs[item.marker]
                                _next_goto.setdefault(a, [])
                                _next_goto[a] += [_s]
            next_goto = _next_goto

        return S

    def load_or_build_tables(self):
        if os.path.isfile('action') and os.path.isfile('goto'):
            with open('action', 'rb') as file:
                action = dill.load(file)
            with open('goto', 'rb') as file:
                goto = dill.load(file)
            return action, goto
        return self.build_tables()

    def _dump_tables(self, action, goto):
        with open('action', 'wb') as file:
            dill.dump(action, file)
        with open('goto', 'wb') as file:
            dill.dump(goto, file)

    def build_tables(self, debug_flags=None):
        t_start = datetime.now()

        S = self._build_canonical_collection()
        if debug_flags and (debug_flags & SHOW_CANONICAL_COL) == SHOW_CANONICAL_COL:
            _show_canonical_collection(S)

        states = len(S)

        _action = Table('action', list(self._T), states)
        _goto = Table('goto', list(self._NT), states)

        for state, s in enumerate(S):
            for item in s:
                if item.marker < len(item.p.rhs):
                    a = item.p.rhs[item.marker]
                    if a in self._T:
                        sk = self._goto(s, a)
                        for k, _s in enumerate(S):
                            if sk == _s:
                                _action.set(state, a, Shift(k))

                elif (item.marker == len(item.p.rhs) and
                      item == Item(self._P[0], len(self._P[0].rhs), '$')):
                    _action.set(state, '$', Accept())

                elif item.marker == len(item.p.rhs):
                    _action.set(state, item.lookahead, Reduce(item.p))

            for nt in self._NT:
                sk = self._goto(s, nt)
                for k, _s in enumerate(S):
                    if sk == _s:
                        _goto.set(state, nt, k)

        if debug_flags and (debug_flags & SHOW_ACTION_TABLE) == SHOW_ACTION_TABLE:
            print(_action, end='\n\n')
        if debug_flags and (debug_flags & SHOW_GOTO_TABLE) == SHOW_GOTO_TABLE:
            print(_goto, end='\n\n')

        t_end = datetime.now()
        if debug_flags and (debug_flags & SHOW_STATISTICS) == SHOW_STATISTICS:
            print('Table generation took ' + Color.UNDERLINE +
                  '{:f}s'.format((t_end - t_start).microseconds / 1e6) + Color.ENDC)
            # noinspection PyUnresolvedReferences
            print(self._goto.cache_info(), end='\n\n')

        self._dump_tables(_action, _goto)

        return _action, _goto


def _show_canonical_collection(S):
    ident = len(str(len(S) - 1))
    for i in range(len(S)):
        s = S[i]
        print('{:<{}} {{'.format(i, ident), end='')
        for j, item in enumerate(s, start=1):
            end = ', '
            if j == len(s):
                end = ''
            elif j % 4 == 0:
                end = ',\n  ' + ' ' * ident
            print(item, end=end)
        print(' }')
    print()
