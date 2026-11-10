""" 1. Validar una contraseña que tenga al menos 8 caracteres """

# password = input("Escribe tu contraseña (8 caracteres como minimo): ")

# if len(password) >= 8:
#     print("Password valida")
# else:    
#     print("Debe tener 8 caracteres como minimo")


while True:
    password = input("Introduce una contraseña: ")
    if len(password) < 8:
        print("Minimo 8 caracteres")
    else:
        print("Contraseña valida")
        break

""" 2. Ingresar un número y crear una tabla de multiplicar hasta el 10 """

# number = int(input("Ingresa un número: "))
# multi = 1

# while True:
#     if multi <= 10:
#         resultado = number * multi
#         print (f"{number} x {multi} = {resultado}")
#         multi += 1
#     else:
#         break


while True:
    number = int(input("Ingresa un número: "))

    i = 1
    while i <=10:
        print(f"{number} x {i} = {number * i}")
        i += 1