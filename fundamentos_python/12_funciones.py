""" Definición de funciones"""
def saludar():
    print("Hola")


""" Llamada a la función"""
saludar()


""" Función con parámetros"""
def sumar(a, b):
    c = a + b
    return c

resultado = sumar(3, 5)
print(resultado)


""" Función con parámetros y valor por defecto """
def saludar_persona(nombre="Invitado"):
    print(f"Hola, {nombre}")

saludar_persona()


""" Funciones con número variable de argumentos """
""" *args """
def mostrar_numeros(*args):
    for numero in args:
        print(numero)

mostrar_numeros(3, 1, 2)


""" *kwargs """
def mostrar_información(**kwargs):
    # kwargs: {'nombre': 'Eduardo', 'edad': '30'}
    for clave in kwargs:
        print(clave, kwargs[clave])

mostrar_información(nombre="Eduardo", edad=30)