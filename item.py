from enum import Enum


class Item:
    def __init__(self, production, marker, lookahead):
        self.production = production
        self.marker = marker
        self.lookahead = lookahead

    def __key(self):
        return self.production, self.marker, self.lookahead

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Item):
            return self.__key() == other.__key()
        return NotImplemented

    def __str__(self):
        lhs = self.production.left.name
        rhs = []
        for s in self.production.right:
            if isinstance(s, Enum):
                rhs += [s.name]
            else:
                rhs += [s]
        rhs.insert(self.marker, '•')
        lookahead = self.lookahead
        if isinstance(self.lookahead, Enum):
            lookahead = self.lookahead.name
        return '[' + lhs + ' → ' + ' '.join(rhs) + ', ' + lookahead + ']'
