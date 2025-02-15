

class BayesNet:

    def __init__(self, ldep=None):  # Why not ldep={}? See footnote 1.
        if not ldep:
            ldep = {}
        self.dependencies = ldep

    # The network data is stored in a dictionary that
    # associates the dependencies to each variable:
    # { v1:deps1, v2:deps2, ... }
    # These dependencies are themselves given
    # by another dictionary that associates conditional
    # probabilities to conjunctions of mother variables:
    # { mothers1:cp1, mothers2:cp2, ... }
    # The conjunctions are frozensets of pairs (mothervar,boolvalue)
    def add(self,var,mothers,prob):
        self.dependencies.setdefault(var,{})[frozenset(mothers)] = prob

    # Joint probability for a given conjunction of
    # all variables of the network
    def jointProb(self,conjunction):
        prob = 1.0
        for (var,val) in conjunction:
            for (mothers,p) in self.dependencies[var].items():
                if mothers.issubset(conjunction):
                    prob*=(p if val else 1-p)
        return prob

    def ancestors(self,a):
        pass

    def individualProb(self, variable, value):
        rows = []

        for c in self._gen_conjunctions([v for v in self.dependencies.keys() if v != variable]):
            rows.append([(variable, value)] + c)

        return sum([self.jointProb(r) for r in rows])

    def _gen_conjunctions(self, variables):
        if variables == []:
            return [[]]

        return [[(variables[0], True)] + c for c in self._gen_conjunctions(variables[1:]) ] + [[(variables[0], False)] + c for c in self._gen_conjunctions(variables[1:])]


# Footnote 1:
# Default arguments are evaluated on function definition,
# not on function evaluation.
# This creates surprising behaviour when the default argument is mutable.
# See:
# http://docs.python-guide.org/en/latest/writing/gotchas/#mutable-default-arguments

