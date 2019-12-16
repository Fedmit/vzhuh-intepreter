class Item:
    def __init__(self, p, marker, lookahead):
        self.p = p
        self.marker = marker
        self.lookahead = lookahead

    def __key__(self):
        return self.p, self.marker, self.lookahead

    def __hash__(self):
        return hash(self.__key__())

    def __eq__(self, other):
        if isinstance(other, Item):
            return self.__key__() == other.__key__()
        return NotImplemented

    def __str__(self):
        rhs = list(self.p.rhs)
        rhs.insert(self.marker, '•')
        return '[' + self.p.lhs + ' → ' + ' '.join(rhs) + ', ' + self.lookahead + ']'
