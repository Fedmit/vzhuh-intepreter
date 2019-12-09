from tabulate import tabulate


class Table:
    _data = {}

    def __init__(self, name, columns, states):
        self.name = name
        self.states = states
        self.columns = columns
        for c in columns:
            self._data[c] = states * [None]

    def get(self, state, column):
        return self._data[column][state]

    def set(self, state, column, value):
        self._data[column][state] = value

    def __str__(self):
        header = ['state']
        header += self.columns
        rows = []
        for state in range(self.states):
            row = [str(state)]
            for c in self.columns:
                d = self.get(state, c)
                if d is None:
                    row += ['']
                else:
                    row += [str(d)]
            rows += [row]

        return self.name.upper() + '\n' + tabulate(rows, headers=header, tablefmt='psql')


class Shift:
    def __init__(self, state):
        self.state = state

    def __str__(self):
        return 's(' + str(self.state) + ')'


class Accept:
    def __str__(self):
        return 'acc'


class Reduce:
    def __init__(self, p):
        self.p = p

    def __str__(self):
        return 'r(' + str(self.p) + ')'
