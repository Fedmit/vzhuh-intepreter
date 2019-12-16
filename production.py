class Production:
    def __init__(self, lhs, rhs, process):
        self.lhs = lhs
        self.rhs = tuple(rhs.split(' '))
        self.process = process

    def __key__(self):
        return self.lhs, self.rhs

    def __hash__(self):
        return hash(self.__key__())

    def __eq__(self, other):
        if isinstance(other, Production):
            return self.__key__() == other.__key__()
        return NotImplemented

    def __str__(self):
        return self.lhs + ' → ' + ' '.join(self.rhs)
