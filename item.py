class Item:
    def __init__(self, p, marker, lookahead):
        self.p = p
        self.marker = marker
        self.lookahead = lookahead

    def __key(self):
        return self.p, self.marker, self.lookahead

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Item):
            return self.__key() == other.__key()
        return NotImplemented

    def __str__(self):
        rhs = list(self.p.rhs)
        rhs.insert(self.marker, '•')
        return '[' + self.p.lhs + ' → ' + ' '.join(rhs) + ', ' + self.lookahead + ']'
