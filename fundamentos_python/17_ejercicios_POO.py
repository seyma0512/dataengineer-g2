""" Recuperar la información de datos.csv y construir una lista de
diccionarios con estos datos, ademas se debe ordenar por orden alfabetico
en base al o a los apellidos, tambien se les debe generar una contraseña
encriptada por defecto en base a la fecha de nacimiento """
# Outupt [{"id":1, "nombre": "...", ..., "activo": true}, {}, ..., {}]

import csv
import hashlib

class Usuario:
    def __init__(self, id, nombre, apellido, email, telefono, ciudad,
                 pais, fecha_registro, activo):
        self.id = int(id)
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.telefono = telefono
        self.ciudad = ciudad
        self.pais = pais
        self.fecha_registro = fecha_registro
        self.activo = activo.lower() == "true"
        
        self.__password = self.__encriptar_password(fecha_registro)
    
    def __encriptar_password(self, texto):
        bytes_texto = texto.encode("utf-8")
        hash_objeto = hashlib.sha256(bytes_texto)
        contrasena_password = hash_objeto.hexdigest()
        return contrasena_password
        
    def to_dict(self):
        datos = {
            "id": self.id,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email,
            "telefono": self.telefono,
            "ciudad": self.ciudad,
            "pais": self.pais,
            "fecha_registro": self.fecha_registro,
            "activo": self.activo,
            "password": self.__password
        }
        return datos
    
def main():
    lista_usuarios = []

    with open("datos.csv", "r", encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo)    
        for fila in lector:
            usuario = Usuario(**fila)
            usuario_dict = usuario.to_dict()
            lista_usuarios.append(usuario_dict)
            
    lista_usuarios.sort(key=lambda u: u["apellido"].lower())
    print(lista_usuarios)

if __name__ == "__main__":
    main()