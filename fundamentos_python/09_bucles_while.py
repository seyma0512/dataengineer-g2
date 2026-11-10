from time import sleep

contador = 0

while contador < 10:
    contador = contador + 1
    sleep(1)
    print(contador)
else:
    print("El bucle termino 😢")

""" Salir de un bucle While con break """
while True:
    print(contador)
    contador +=1
    if contador == 15:
        break   # Rompe el bucle cuando [Variable] == 15

""" Saltar una iteración con continue"""
while True:
    contador += 1
    if contador == 5:
        continue # Salta la iteración cuando es 5
    print(contador)
    
    if contador == 10:
        break