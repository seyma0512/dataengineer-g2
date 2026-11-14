# r: Modo lectura
# encoding="utf-8": Evita errores con tildes y caracteres especiales
# with: Gestiona recursos de forma segura y automatica
with open("archivo.txt", "r", encoding="utf-8") as archivo:
    contenido = archivo.read()
    # print(contenido)

""" Leer línea por línea"""
with open("archivo.txt", "r", encoding="utf-8") as archivo:
    
    fila = 0
    for linea in archivo:
        fila += 1
        if fila == 1:
            continue
        
        linea_sin_espacios = linea.strip()
        lenguaje = linea_sin_espacios.split(",")[-1]
        # print(lenguaje)

        
""" Guardar las lineas en una lista"""
with open("archivo.txt", "r", encoding="utf-8") as archivo:
    lineas = archivo.readlines()

# print(lineas[0].strip())

""" Formatos estructurados comunes (CSV y JSON) """
import json

with open("datos.json", "r", encoding="utf-8") as archivo:
    datos = json.load(archivo)
    # print(datos)
    
with open("datos_1.json", "r", encoding="utf-8") as archivo:
    datos = json.load(archivo)
    # print(datos)
    
import csv
with open("datos.csv", "r", encoding="utf-8") as archivo:
    lector = csv.reader(archivo)
    for fila in lector:
        print(fila)