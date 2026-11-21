from fuentes import leer_csv, obtener_usuarios
from funciones import cruzar, limpiar_transacciones
from tabla import mostrar_tabla

ARCHIVO_CSV = "transacciones_sebastian_paredes.csv"


def main():
    filas = leer_csv(ARCHIVO_CSV)
    transacciones, duplicados = limpiar_transacciones(filas)
    usuarios = obtener_usuarios(limite=10)
    cruzadas, sin_usuario = cruzar(transacciones, usuarios)
    mostrar_tabla(cruzadas, sin_usuario, duplicados)


if __name__ == "__main__":
    main()
