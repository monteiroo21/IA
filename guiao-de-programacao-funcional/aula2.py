import math

#Exercicio 4.1
impar = lambda x: x%2 == 1

#Exercicio 4.2
positivo = lambda x : x > 0

#Exercicio 4.3
comparar_modulo = lambda x,y : abs(x) < abs(y)

#Exercicio 4.4
cart2pol = lambda x,y : (math.hypot(x,y), math.atan2(y,x))

#Exercicio 4.5
ex5 = lambda f,g,h : lambda x,y,z : h(f(x,y), g(y,z))

#Exercicio 4.6
def quantificador_universal(lista, f):
    if lista == []:
        return True
    return f(lista[0]) and quantificador_universal(lista[1:], f)

#Exercicio 4.8
def subconjunto(lista1, lista2):
    if lista1 == []:
        return True

    return lista1[0] in lista2 and subconjunto(lista1[1:], lista2)

#Exercicio 4.9
def menor_ordem(lista, f):
    if lista == []:
        return None
    menor = menor_ordem(lista[1:], f)
    if menor == None or f(lista[0], menor):
        return lista[0]
    return menor

#Exercicio 4.10
def menor_e_resto_ordem(lista, f):
    if lista == []:
        return None, []
    menor, resto = menor_e_resto_ordem(lista[1:], f)
    if menor == None or f(lista[0], menor):
        return lista[0], lista[1:]
    return menor, [lista[0]] + resto

#Exercicio 5.2
def ordenar_seleccao(lista, ordem):
    if lista == []:
        return []
    menor, resto = menor_e_resto_ordem(lista, ordem)
    return [menor] + ordenar_seleccao(resto, ordem)
