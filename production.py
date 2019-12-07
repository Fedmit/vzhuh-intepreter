from enum import Enum


class Production:
    def __init__(self, left, right, process):
        self.left = left
        self.right = right
        self.process = process

    def __key(self):
        return self.left, self.right

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Production):
            return self.__key() == other.__key()
        return NotImplemented

    def __str__(self):
        lhs = self.left.name
        rhs = []
        for s in self.right:
            if isinstance(s, Enum):
                rhs += [s.name]
            else:
                rhs += [s]
        return lhs + ' → ' + ' '.join(rhs)
