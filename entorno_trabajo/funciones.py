import re
from datetime import datetime
import logging

def limpiar_monto(valor):
    numero = re.sub(r"[^\d.\-]", "", valor) # re.sub reemplaza por patrón
    return abs(float(numero)) if numero.strip("-.") else None


def limpiar_estado(valor):
    estado = valor.strip().capitalize()
    return None if estado.upper() in ("", "N/A") else estado


def limpiar_fecha(valor):
    for formato in ("%Y-%m-%d", "%d/%m/%Y", "%d-%b-%Y"):
        try:
            return datetime.strptime(valor.strip(), formato).date().isoformat() # strptime lee el texto por formato
        except ValueError:
            pass
    return None


def limpiar_transacciones(filas):
    limpias, vistos = [], set()
    for fila in filas:
        if fila["tx_id"] in vistos:
            continue
        vistos.add(fila["tx_id"])
        limpias.append({
            "tx_id": fila["tx_id"],
            "user_id": int(fila["user_id"]) if fila["user_id"].strip().isdigit() else None,
            "cliente": " ".join(fila["cliente_referencia"].split()).title(),
            "plan": fila["plan"].strip().capitalize(),
            "monto": limpiar_monto(fila["monto_mensual"]),
            "estado": limpiar_estado(fila["estado_cuenta"]),
            "fecha": limpiar_fecha(fila["fecha_registro"]),
        })
    return limpias, len(filas) - len(limpias)


def cruzar(transacciones, usuarios):
    cruzadas, sin_usuario = [], 0
    for tx in transacciones:
        usuario = usuarios.get(tx["user_id"])
        if usuario:
            cruzadas.append((tx, usuario))
        else:
            sin_usuario += 1
    return cruzadas, sin_usuario
