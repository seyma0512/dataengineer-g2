# Determinar el mayor de dos números
# numero1 = 10
# numero2 = 20

# Output: El mayor es 20
numero1 = 10
numero2 = 20

numero1 = int(input("Ingresa el primer número: "))
numero2 = int(input("Ingresa el segundo número: "))

print(f"Valores: {numero1} y {numero2}")

if numero1 == numero2:
    print("Son iguales")
else:
    print(f"El mayor es: {max(numero1, numero2)}")