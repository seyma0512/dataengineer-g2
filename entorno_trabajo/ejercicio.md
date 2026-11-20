# Ejercicio

## Contexto

El área comercial tiene un archivo facturacion.csv con lo montos facturados y el estado de cuenta de cada cleinte, pero no tiene sus datos de contacto ni ubicación. Por otro lado, el sistema central expone los datos maestros de los usuarios a trvpes de una API REST.

# Objetivo

Construir un pipeline ETL en Python aplicando POO para cruzar ambas fuentes de datos, limpiar inconsistencais y generar un reporte jecutivo en consola usando 'rich'

1. Generar una lista de datos CSV ejecutando ´python generar_datos.py´
2. Recuperar una lista de 10 usuarios de [jsonplaceholder]('https://jsonplaceholder.typicode.com/')
3. Limpiar los datos
4. Asociar estos datos con los registros del documento .CSV
