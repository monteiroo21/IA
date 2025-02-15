#encoding: utf8

# YOUR NAME: João Pedro Ferreira Monteiro
# YOUR NUMBER: 114547

# COLLEAGUES WITH WHOM YOU DISCUSSED THIS ASSIGNMENT (names, numbers):

from semantic_network import *
from constraintsearch import *
from bayes_net import *
from itertools import product

class MySN(SemanticNetwork):

    def __init__(self):
        SemanticNetwork.__init__(self)
        pass

    def get_most_frequent_type(self, relname):
        type_counts = {}
        for d in self.declarations:
            if d.relation.name == relname:
                rel_type = type(d.relation)
                type_counts[rel_type] = type_counts.get(rel_type, 0) + 1
        return max(type_counts, key=type_counts.get) if type_counts else None
    
    def get_predecessors(self, entity):
        return set([d.relation.entity2 
                for d in self.declarations 
                if d.relation.entity1 == entity and (isinstance(d.relation, Member) or isinstance(d.relation, Subtype))])

    # General query method, processing different types of
    # relations according to their specificities
    def query(self,entity,relname):
        local_declarations = self.query_local(e1=entity, relname=relname)

        most_frequent = self.get_most_frequent_type(relname)
        
        if relname in [d.relation.name for d in local_declarations if (isinstance(d.relation, Member) or isinstance(d.relation, Subtype))]:
            return [d.relation.entity2 for d in local_declarations if isinstance(d.relation, Member) or isinstance(d.relation, Subtype)]
        
        if most_frequent == AssocOne:
            values = [d.relation.entity2 for d in local_declarations if isinstance(d.relation, AssocOne)]
            if values:
                frequency = {}
                for v in values:
                    if v in frequency:
                        frequency[v] += 1
                    else:
                        frequency[v] = 1
                return [max(frequency, key=frequency.get)]
                
            predecessors = self.get_predecessors(entity)
            for p in predecessors:
                result = self.query(p, relname)
                if result:
                    return result
        
        if most_frequent == AssocNum:
            values = [d.relation.entity2 for d in local_declarations if isinstance(d.relation, AssocNum) and isinstance(d.relation.entity2, (int, float))]
            if values: 
                return [sum(values) / len(values)]

            predecessors = self.get_predecessors(entity)
            all_values = []
            for p in predecessors:
                result = self.query(p, relname)
                if result:
                    all_values.extend(result)
            return [sum(all_values) / len(all_values)] if all_values else None
        
        if most_frequent == AssocSome:
            values = [d.relation.entity2 for d in local_declarations if isinstance(d.relation, AssocSome)]

            predecessors = self.get_predecessors(entity)
            for p in predecessors:
                result = self.query(p, relname)
                if result:
                    values.extend(result)
            return values if values else None

class MyBN(BayesNet):

    def __init__(self):
        BayesNet.__init__(self)
        pass
    
    def test_independence(self,v1,v2,given):
        var = [v1, v2] + given
        ancestors = set()
        for v in var:
            ancestors.update(self.get_ancestors(v, ancestors))

        graph = self.get_graph(ancestors)

        for g in given:
            graph = self.remove_node(graph,g)

        return graph, not self.has_path(graph,v1,v2)

    def get_ancestors(self, variable, ancestors):
        if variable in ancestors:
            return ancestors
        ancestors.add(variable)
        for (mtrue, mfalse, p) in self.dependencies[variable]:
            for v in (mtrue + mfalse):
                self.get_ancestors(v, ancestors)
        return ancestors
    
    def get_graph(self,ancestores):
        edges = set()
        for var in ancestores:
            mothers = []
            for (mtrue, mfalse, p) in self.dependencies[var]:
                mothers.extend(mtrue + mfalse)

            for m in mothers:
                if var != m:
                    edge = tuple(sorted((var, m)))
                    edges.add(edge)

            for i in range(len(mothers)):
                for j in range(i+1,len(mothers)):
                    if mothers[i] != mothers[j]:
                        edge = tuple(sorted((mothers[i], mothers[j])))
                        edges.add(edge)

        return list(edges)
    
    def remove_node(self,graph,node):
        return[(x,y) for (x,y) in graph if x != node and y != node]

    def has_path(self, graph, v1, v2):
        nodes = set()
        for (x,y) in graph:
            nodes.add(x)
            nodes.add(y)

        if v1 not in nodes or v2 not in nodes:
            return False
        if v1 == v2:
            return True

        visited = set([v1])
        stack = [v1]

        while stack:
            current = stack.pop()
            if current == v2:
                return True
            for (x, y) in graph:
                if x == current and y not in visited:
                    stack.append(y)
                    visited.add(y)
                elif y == current and x not in visited:
                    stack.append(x)
                    visited.add(x)

        return False

    
class MyCS(ConstraintSearch):

    def __init__(self,domains,constraints):
        ConstraintSearch.__init__(self,domains,constraints)
        pass

    def search_all(self,domains=None):
        if domains is None:
            domains = {var: vals[:] for var, vals in self.domains.items()}

        if any(len(lv) == 0 for lv in domains.values()):
            return []

        if all(len(lv) == 1 for lv in domains.values()):
            return [{v: lv[0] for (v, lv) in domains.items()}]

        var = min((v for v in domains if len(domains[v]) > 1), key=lambda x: len(domains[x]))

        solutions = []
        for val in domains[var]:
            newdomains = {v: vals[:] for v, vals in domains.items()}
            newdomains[var] = [val]
            self.propagate(newdomains, var)
            if not any(len(lv) == 0 for lv in newdomains.values()):
                sols = self.search_all(newdomains)
                solutions.extend(sols)

        return solutions

def handle_ho_constraint(domains,constraints,variables,constraint):
    A = "".join(variables)
    ho_domains = [domains[v] for v in variables]
    A_domain = []
    for combo in product(*ho_domains):
        if constraint(combo):
            A_domain.append(combo)
    domains[A] = A_domain
    variables.append(A)
    for i, v in enumerate(variables):
        if v == A:
            continue
        def make_constraint(index, aux=A, var=v):
            def binary_constraint(varA, valA, varV, valV):
                if varA == aux:
                    return valA[index] == valV
                if varV == aux:
                    return valV[index] == valA
                return True
            return binary_constraint
        c_fn = make_constraint(i)
        constraints[(A,v)] = c_fn
        constraints[(v,A)] = c_fn

