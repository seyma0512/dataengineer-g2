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
        
camioneta = Vehiculo("Toyota", "Blanco", "Hilux")
print(camioneta.color)

coche = Vehiculo("VW", "Rojo", "Golf")
print(coche.color)

# Camioneta
# Auto
# Minibus

# VW
# Mitsubishi
# Toyota