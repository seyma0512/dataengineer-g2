users = [
    ["Juan", 25 , "m", "juan@email.com"],
    ["María", 30, "f", "maria@email.com"],
    ["Pedro", 28, "m", "pedro@email.com"],
    ["Ana", 22, "f", "ana@email.com"]
]

new_users=[]
i = 1
for user in users:
    user_dic = {
        "id": i,
        "name": user[0],
        "age": user[1],
        "gender": user[2],
        "email": user[3]
    }
    i += 1
    new_users.append(user_dic)

# print(new_users)

vehiculo = {
    "marca": "Toyota",
    "modelo": "Corola",
    "año": 2020,
}


""" Modificar y agregar elementos """
vehiculo["marca"] = "Honda"
vehiculo["color"] = "Rojo"
print(vehiculo)

""" Eliminar elementos """
del vehiculo["color"]
vehiculo.pop("año")
print(vehiculo)

""" Métodos útiles """
print(vehiculo.keys())      # Devuelve las claves del diccionario
print(vehiculo.values())    # Devuelve los valores del diccionario
print(vehiculo.items())     # Devuelve una lista de tuplas con las claves y valores del diccionario

""" Iterar sobre un diccionario """
print("Iterar 1: ")
for clave in vehiculo:
    print(clave, vehiculo[clave])
print("Iterar 2: ")
for clave, valor in vehiculo.items():
    print(clave, valor)