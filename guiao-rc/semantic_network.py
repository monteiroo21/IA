

# Guiao de representacao do conhecimento
# -- Redes semanticas
# 
# Inteligencia Artificial & Introducao a Inteligencia Artificial
# DETI / UA
#
# (c) Luis Seabra Lopes, 2012-2020
# v1.9 - 2019/10/20
#


# Classe Relation, com as seguintes classes derivadas:
#     - Association - uma associacao generica entre duas entidades
#     - Subtype     - uma relacao de subtipo entre dois tipos
#     - Member      - uma relacao de pertenca de uma instancia a um tipo
#

from collections import Counter
from statistics import fmean


class Relation:
    def __init__(self,e1,rel,e2):
        self.entity1 = e1
#       self.relation = rel  # obsoleto
        self.name = rel
        self.entity2 = e2
    def __str__(self):
        return self.name + "(" + str(self.entity1) + "," + \
               str(self.entity2) + ")"
    def __repr__(self):
        return str(self)


# Subclasse Association
class Association(Relation):
    def __init__(self,e1,assoc,e2):
        Relation.__init__(self,e1,assoc,e2)

class AssocOne(Relation):
    def __init__(self, e1, assoc, e2):
        super().__init__(e1, assoc, e2)

class AssocNum(Relation):
    def __init__(self, e1, assoc, e2):
        super().__init__(e1, assoc, e2)

#   Exemplo:
#   a = Association('socrates','professor','filosofia')

# Subclasse Subtype
class Subtype(Relation):
    def __init__(self,sub,super):
        Relation.__init__(self,sub,"subtype",super)


#   Exemplo:
#   s = Subtype('homem','mamifero')

# Subclasse Member
class Member(Relation):
    def __init__(self,obj,type):
        Relation.__init__(self,obj,"member",type)

#   Exemplo:
#   m = Member('socrates','homem')

# classe Declaration
# -- associa um utilizador a uma relacao por si inserida
#    na rede semantica
#
class Declaration:
    def __init__(self,user,rel):
        self.user = user
        self.relation = rel
    def __str__(self):
        return "decl("+str(self.user)+","+str(self.relation)+")"
    def __repr__(self):
        return str(self)

#   Exemplos:
#   da = Declaration('descartes',a)
#   ds = Declaration('darwin',s)
#   dm = Declaration('descartes',m)

# classe SemanticNetwork
# -- composta por um conjunto de declaracoes
#    armazenado na forma de uma lista
#
class SemanticNetwork:
    def __init__(self,ldecl=None):
        self.declarations = [] if ldecl==None else ldecl

    def __str__(self):
        return str(self.declarations)
    
    def insert(self,decl):
        self.declarations.append(decl)

    def query_local(self,user=None,e1=None,rel=None,e2=None,rel_type=None):
        self.query_result = \
            [ d for d in self.declarations
                if  (user == None or d.user==user)
                and (e1 == None or d.relation.entity1 == e1)
                and (rel == None or d.relation.name == rel)
                and (e2 == None or d.relation.entity2 == e2)
                and (rel_type == None or isinstance(d.relation, rel_type)) ]
        return self.query_result
    
    def show_query_result(self):
        for d in self.query_result:
            print(str(d))

    def list_associations(self):
        assoc = self.query_local(rel_type=Association)
        return {d.relation.name for d in assoc}
    
    def list_objects(self):
        obj = self.query_local(rel_type=Member)
        return {d.relation.entity1 for d in obj}
    
    def list_users(self):
        return {d.user for d in self.declarations}
    
    def list_types(self):
        # types = self.query_local(rel_type=(Member,Subtype))
        # return set(
        #     [d.relation.entity2 for d in types]
        #     + [d.relation.entity1 for d in types if isinstance(d.relation, Subtype)]
        # )

        types = set()
        for d in self.declarations:
            if isinstance(d.relation, (Member, Subtype)):
                types.add(d.relation.entity2)
                if isinstance(d.relation, Subtype):
                    types.add(d.relation.entity1)
        return types
    
    def list_local_associations(self, e):
        local_assoc = self.query_local(e1=e, rel_type=Association)
        return {d.relation.name for d in local_assoc}
    
    def list_relations_by_user(self, u):
        rel = self.query_local(user=u, rel_type=Relation)
        return {d.relation.name for d in rel}
    
    def associations_by_user(self, u):
        user_assoc = self.query_local(user=u, rel_type=Association)
        return len({d.relation.name for d in user_assoc})
    
    def list_local_associations_by_entity(self, e):
        ent_assoc = self.query_local(e1=e, rel_type=Association)
        return {(d.relation.name, d.user) for d in ent_assoc}
    
    def predecessor(self, a, b):
        local_predecessor = [d.relation.entity2 for d in self.query_local(e1=b, rel_type=(Member, Subtype))]
        if a in local_predecessor:
            return True
        return any(self.predecessor(a, l) for l in local_predecessor)
    
    def predecessor_path(self, a, b):
        local_predecessor = [d.relation.entity2 for d in self.query_local(e1=b, rel_type=(Member, Subtype))]
        if a in local_predecessor:
            return [a, b]
        for path in [self.predecessor_path(a, l) for l in local_predecessor]:
            if path:
                return path + [b]
            
    def query(self, e, assoc=None):
        local_declarations = self.query_local(e1=e, rel=assoc, rel_type=Association)
        local_predecessor = [d.relation.entity2 for d in self.query_local(e1=e, rel_type=(Member, Subtype))]
        
        for predecessor in local_predecessor:
            local_declarations.extend(self.query(predecessor, assoc))

        return local_declarations
    
    def query2(self, e, assoc=None):
        local_declarations = self.query_local(e1=e, rel=assoc)
        local_predecessor = [d.relation.entity2 for d in self.query_local(e1=e, rel_type=(Member, Subtype))]
        
        for predecessor in local_predecessor:
            local_declarations.extend(self.query(predecessor, assoc))
        return local_declarations
    
    def query_cancel(self, e, assoc=None):
        local_declarations = self.query_local(e1=e, rel=assoc)
        local_predecessor = [d.relation.entity2 for d in self.query_local(e1=e, rel_type=(Member, Subtype))]
        local_assoc = [d.relation.name for d in local_declarations]

        for predecessor in local_predecessor:
            local_declarations.extend(
                [h for h in self.query_cancel(predecessor, assoc) if h.relation.name not in local_assoc]
            )

        return local_declarations
    
    def query_down(self, e, assoc, first=True):
        local_declarations = [] if first else self.query_local(e1=e, rel=assoc)

        local_descendent = [d.relation.entity1 for d in self.query_local(e2=e, rel_type=(Member,Subtype))]

        for descendent in local_descendent:
            local_declarations.extend(
                [
                    child
                    for child in self.query_down(descendent, assoc, False)
                ]
            )
        return local_declarations

    def query_induce(self, entity, assoc):
        decl = self.query_down(entity, assoc)

        r = Counter([d.relation.entity2 for d in decl]).most_common(1)

        if len(r):
            return r[0][0]
        
    def query_local_assoc(self, entity, assoc):
        decl = self.query_local(e1=entity, rel=assoc)

        hist = Counter([d.relation.entity2 for d in decl]).most_common()

        for d in decl:
            if isinstance(d.relation, AssocOne):
                v,t = hist[0]
                return v, t/len(decl)
            elif isinstance(d.relation, AssocNum):
                return fmean([d.relation.entity2 for d in decl])
            elif isinstance(d.relation, Association):

                def lim_gen(assoc):
                    lim = 0
                    for a,f in assoc:
                        yield a,f
                        lim += f
                        if lim > 0.75:
                            return
                return list(lim_gen([(v,t/len(decl)) for v,t in hist]))
            
                '''
                lim = 0
                r = []

                for v,f in [(v,t/len(decl)) for v,t in hist]:
                    lim += f
                    r.append((v,f))
                    if lim > 0.75:
                        return r  
                '''

    def query_assoc_value(self, E, A):
        local_decl = self.query_local(e1=E,rel=A)

        local_hist = Counter([d.relation.entity2 for d in local_decl]).most_common()

        if local_hist and local_hist[0][1] == len(local_decl):
            return local_hist[0][0]

        inher_decl = [h for h in self.query(E,A) if h not in local_decl]

        inher_hist = Counter([d.relation.entity2 for d in inher_decl]).most_common()

        if not local_decl:
            return inher_hist[0][0]
        if not inher_decl:
            return local_hist[0][0]
        
        f = {v: t for v,t in local_hist}
        for v,t in inher_hist:
            f[v] = f.get(v,0) + t

        return [k for k,v in sorted(f.items(), key=lambda x: -x[1])][0]