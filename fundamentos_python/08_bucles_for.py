lista = ["Python", "Rust", "Java", "C++", "TS"]

""" Recorrer (Iterar) sobre esta lista """

for lenguaje in lista:
    print(lenguaje)

""" Recorrer (Iterar) cadenas de texto """
texto = "I love Python"
for letra in texto:
    print(letra)

""" Recorrer (Iterar) una lista con un índice """
for index, lenguaje in enumerate(lista):
    print(index,lenguaje)