""" Las clases nos permiten implementar el paradigma de Programación
Orientada a Objetos (POO). Nos permite rear tipos de datos, encapsular
artributos y coportamientos, y organizar código de forma modular y reutilizable."""

class Persona:
    pass

class Vehiculo:
    def __init__(self, marca, color, modelo):
        self.marca = marca
        self.color = color
        self.modelo = modelo
        self.__codigo = "VW001"
        # Encapsulación
    def ver_datos(self):
        print(f"Ese vechiculo es de marca: {self.marca}, color: {self.color}, modelo: {self.modelo} y codigo {self.__codigo}")
        
    def __informacion_privada(self):
        print(f"Esta información es privada: {self.__codigo}")
    
camioneta = Vehiculo("Toyota", "Blanco", "Hilux")
coche = Vehiculo("VW", "Rojo", "Golf")

# coche.ver_datos()
# print(coche.__codigo)
# coche.__informacion_privada()

#Herencia
class Animal:
    def __init__(self, nombre):
        self.nombre = nombre
        
    def saltar(self):
        print(f"{self.nombre} ha saltado")
    
    @staticmethod
    def vacunas(mensaje):
        print(mensaje)


class Gato(Animal):
    def maullar(self):
        print(f"{self.nombre} dice Miau")

p1 = Animal("Otto")
p1.saltar()
p1.vacunas("Las vacunas están al día")

g1 = Gato("Hiro")
g1.maullar()
g1.saltar()
