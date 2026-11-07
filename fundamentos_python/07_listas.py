""" Son colecciones ordenadas y mutables de 
elementos que permiten almacenar multiples 
elementos en una sola variable. """

lista1 = [1, 2, 3, 4, 5]
lista2 = ["Python", "Rust", "TS"]
lista3 = [1, 2, 3.14, True, "Hola"]
# Orden de las listas: Inician desde 0 

""" Acceder a elementos de una lista"""
print(lista2[1])
# Output: Rust

print(lista3[-1])
# Output: Hola

""" Slicing (Rebanado) de listas """
print(lista1[1:4])
# Output: [2, 3, 4]

print(lista1[:3])
# Output: [1, 2, 4]

print(lista1[3:])
# Output: [4, 5]

print(lista1[::2]) # (Paso 2)
# Output: [1, 3, 5]

""" Modificar elementos de una lista """
lista1[4] = 10
print(lista1)
# Output: [1, 2, 3, 4, 10]

""" Agregar elementos en una lista """
lista1 = lista1 + [6,7]
print(lista1)
# Output: [1, 2, 3, 4, 10, 6, 7]

""" Obtener longitu de una lista"""
print(len(lista1))
# Output: 7

""" Métodos de lista """
lista  = ["Python"]
lista.append("Go")
print(lista)
# Output: ['Python', 'Go']

lista.insert(0, "C++")
print(lista)
# Output: ['C++', 'Python', 'Go']

lista.remove("Go")
print(lista)
# Output: ['C++', 'Python']

lista.pop(0) # Por defecto elemina al último elemento
print(lista)
# Output: ['Python']

print(lista.index("Python"))
# Output: 0

lista.append("Python")
print(lista.count("Python"))
# Output: 2

lista2 = [5, 10, 2]
lista2.sort()
print(lista2)
# Output: [2, 5, 10]

lista2.reverse()
print(lista2)
# Output: [10, 5, 2]

lista2.clear()
print(lista2)
# Output: []