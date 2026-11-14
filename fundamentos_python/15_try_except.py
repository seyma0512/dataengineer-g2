# resultado = 5 / 0

# Dentro de este bloque se ejecuta el código en el que puede ocurrir un error
# try:
#     numero = int(input("Ingresa un número: "))
#     resultado = 10 / numero
#     print(f"El resultado es {resultado}")
# # Este bloque solo se ejecuta cuando ocurre un error
# except ZeroDivisionError:
#     print("Error: No puedes dividir entre cero.")
# except ValueError:
#     print("Error: Debes ingresar un número válido, no texto.")
# except Exception:
#     print("Error: Ha ocurrido un error desconocido.")
    
# # Se ejecuta SOLO SI NO HUBO NINGÚN ERROR en el bloque try
# else:
#     print("Proceso finalizado con éxito")
#     print(resultado)

# # Se ejecuta SIEMPRE (con sin error)
# finally:
#     print("Proceso finalizado")
    
    
try:
    with open("file.txt", "r", encoding="utf-8") as archivo:
        contenido = archivo.read()
except FileNotFoundError:
    print("El archivo no existe")
else:
    print("Archivo leido con exito")
    print(contenido)
finally:
    print("Proceso de lectura finalizado")