ventas_crudas = [
    {
        "id_venta": 1001,
        "cliente": "   mArÍa fErNaNdA lÓpEz  ",
        "email": "maria.lopez@techcorp.pe",
        "subtotal": 250.0,
        "impuesto": 0.18,
        "moneda": "PEN",
        "estado": "COMPLETADO",
        "tarjeta": "4557-8890-1234",
    },
    {
        "id_venta": 1002,
        "cliente": "carlos_ruiz",
        "email": "cruiz_sin_arroba.com",
        "subtotal": 120.0,
        "impuesto": 0.0,
        "moneda": "USD",
        "estado": "COMPLETADO",
        "tarjeta": "5120-4432-9981",
    },
    {
        "id_venta": 1003,
        "cliente": None,
        "email": "contacto@startup.io",
        "subtotal": -50.0,  # Error de registro (monto negativo)
        "impuesto": 0.18,
        "moneda": "PEN",
        "estado": "COMPLETADO",
        "tarjeta": "4111-2222-3333",
    },
    {
        "id_venta": 1004,
        "cliente": "  ROBERTO GÓMEZ ",
        "email": "rgomez@gmail.com",
        "subtotal": 500.0,
        "impuesto": 0.18,
        "moneda": "PEN",
        "estado": "CANCELADO",  # Debe filtrarse
        "tarjeta": "4916-0098-7765",
    },
    {
        "id_venta": 1005,
        "cliente": "",
        "email": "ventas@logistica.com",
        "subtotal": 80.0,
        "impuesto": 0.18,
        "moneda": "USD",
        "estado": "COMPLETADO",
        "tarjeta": "5412-7500-8812",
    },
    {
        "id_venta": 1006,
        "cliente": "  lucía mendieta",
        "email": "lucia@finanzas.pe",
        "subtotal": 5.0,  # Debajo del monto mínimo
        "impuesto": 0.18,
        "moneda": "EUR",  # Moneda no soportada
        "estado": "COMPLETADO",
        "tarjeta": "4000-1234-5678",
    },
]


""" Ejercicio 1: Eliminar los espacios extra y aplica formato título """
def limpiar_nombre(nombre_crudo : str | None):
    if not nombre_crudo or not nombre_crudo.strip():
        return "Desconocido"
    return nombre_crudo.replace("_"," ").strip().title()
    
resultado=limpiar_nombre(ventas_crudas[1]["cliente"])
print(resultado)


""" Ejercicio 2: Extractor de dominio de correo"""
def extraer_dominio(email: str | None):
    if not email or "@" not in email:
        return "Dominio Inválido"
    
    dominio = email.split("@")[1].strip().lower()
    return dominio

print(extraer_dominio(ventas_crudas[1]["email"]))


""" Ejercicio 3: Validador de divisas, solo se permite PEN, USD y montos """

def es_transaccion_valida(monto: float, moneda: str):
    moneda_permitidas = ("PEN", "USD")
    if monto >= 0 and moneda.upper() in moneda_permitidas:
        return True
    return False

resultado = es_transaccion_valida(ventas_crudas[0]["subtotal"], ventas_crudas[0]["moneda"])
print(resultado)


""" Ejercicio 4: Conversor de divisas con tasa configurable"""

def convertir_usd(monto: float, moneda: str, tasa: float = 3.75):
    moneda_limpia = moneda.strip().upper()
    
    if moneda_limpia == "PEN":
        resultado = monto / tasa
        return round(resultado, 2)
    if moneda_limpia == "USD":
        return round(monto, 2)

total_usd = convertir_usd(ventas_crudas[0]["subtotal"], ventas_crudas[0]["moneda"])
print(total_usd)


""" Ejercicio 5: Orquestador del pipeline """
#1. Filtrar por el estado del negocio, tiene que estar COMPLETADO
#2. Limpiar los nombres
#3. Determinar el dominio
#4. Validar la transaccion
#5. Convertir a USD
#6. Construir un diccionario de salida

def ejecutar_pipeline(datos_ventas: list, tasa_cambio: float = 3.75):
    ventas_limpias = []
    
    for venta in datos_ventas:
        if venta["estado"] != "COMPLETADO":
            continue
        
        if not es_transaccion_valida(venta["subtotal"], venta["moneda"]):
            continue
        
        cliente_limpio = limpiar_nombre(venta["cliente"])
        dominio_correo = extraer_dominio(venta["email"])
        monto_usd = convertir_usd(venta["subtotal"], venta["moneda"], tasa_cambio)
        
        registro_limpio = {
            "id_venta": venta["id_venta"],
            "cliente": cliente_limpio,
            "dominio": dominio_correo,
            "total_usd": monto_usd
        }
        ventas_limpias.append(registro_limpio)
    return ventas_limpias

resultado_final = ejecutar_pipeline(ventas_crudas)
for item in resultado_final:
    print(item)
    
    
    
def ejecutar_pipeline2(datos_crudos: list[dict]):
    
    registros_limpios2 = []
    descartados =0
    monto_total = 0
    
    for fila in datos_crudos:
        
        if fila["estado"] != "COMPLETADO":
            descartados = descartados + 1
            continue
        
        if not es_transaccion_valida(fila["subtotal"], fila["moneda"]):
            descartados = descartados + 1
            continue
        
        fila["cliente"] = limpiar_nombre(fila["cliente"])
        fila["dominio"] = extraer_dominio(fila["email"])
        fila["subtotal"] = convertir_usd(fila["subtotal"], fila["moneda"], 3.5)
        monto_total = monto_total + fila["subtotal"]
        fila["moneda"] = "USD"
        
        registros_limpios2.append(fila)

    return {
        "data_final": registros_limpios2,
        "registros_procesados": len(datos_crudos),
        "registros_descartados": descartados,
        "monto_total_usd": monto_total
    }
    
from pprint import pprint   
resultado = ejecutar_pipeline2(ventas_crudas)
pprint(resultado)