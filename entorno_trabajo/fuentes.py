import csv
import requests

API_URL = "https://jsonplaceholder.typicode.com/users"


def leer_csv(ruta):
    with open(ruta, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def obtener_usuarios(limite=10):
    respuesta = requests.get(API_URL, timeout=10)
    respuesta.raise_for_status()
    return {u["id"]: u for u in respuesta.json()[:limite]}
