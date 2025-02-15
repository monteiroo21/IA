from constraintsearch import *

region = ['A', 'B', 'C', 'D', 'E']
colors = ['red', 'blue', 'green', 'yellow', 'white']

mapa_a = {
    'A': ['B', 'E', 'D'],
    'B': 'AEC',
    'C': 'BED',
    'D': 'AEC',
    'E': 'ABCD'
}

def constraint(r1, c1, r2, c2):
    return c1 != c2

def make_constraint_graph(mapa):
    return { (X,Y): constraint for X in mapa for Y in mapa[X] }

def make_domain(region, colors):
    return {r: colors for r in region}

cs = ConstraintSearch(make_domain(region, colors), make_constraint_graph(mapa_a))

print(cs.search())
