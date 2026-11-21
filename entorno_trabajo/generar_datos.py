import csv
import hashlib
import random
from faker import Faker

TOTAL_REGISTROS = 100

def obtener_semilla(nombre: str) -> int:
    nombre_normalizado = " ".join(nombre.strip().lower().split())
    hash_hex = hashlib.sha256(nombre_normalizado.encode('utf-8')).hexdigest()
    return int(hash_hex[:8], 16)

def ensuciar_monto(monto: float) -> str:
    caso = random.random()
    if caso < 0.10:
        return ""
    elif caso < 0.25:
        return f"${monto:,.2f}"
    elif caso < 0.40:
        return f"  {monto:.2f} USD "
    elif caso < 0.45:
        return f"-{monto:.2f}"
    return f"{monto:.2f}"

def ensuciar_estado(estado: str) -> str:
    variaciones = [
        estado.lower(),
        estado.upper(),
        f"  {estado} ",
        estado.capitalize(),
        "N/A" if random.random() < 0.08 else estado
    ]
    return random.choice(variaciones)

def ensuciar_fecha(fake: Faker) -> str:
    fecha = fake.date_between(start_date="-1y", end_date="today")
    formatos = ["%Y-%m-%d", "%d/%m/%Y", "%d-%b-%Y"]
    return fecha.strftime(random.choice(formatos))

def generar_csv():
    nombre_estudiante = ""
    while not nombre_estudiante.strip():
        nombre_estudiante = input("Ingresa tu nombre completo para generar tu dataset: ")

    semilla = obtener_semilla(nombre_estudiante)
    fake = Faker('es_ES')
    Faker.seed(semilla)
    random.seed(semilla)

    slug = "_".join(nombre_estudiante.strip().lower().split())
    archivo_salida = f"transacciones_{slug}.csv"

    planes = ["Basic", "Pro", "Enterprise", "basic ", " PRO", "enterprise"]
    estados_base = ["Activo", "Suspendido", "Moroso", "Cancelado"]
    ids_posibles = list(range(1, 14))

    registros = []

    for i in range(1, TOTAL_REGISTROS + 1):
        user_id = random.choice(ids_posibles)
        plan = random.choice(planes)
        monto_base = round(random.uniform(99.0, 2500.0), 2)
        
        fila = {
            "tx_id": f"TX-{1000 + i}",
            "user_id": user_id if random.random() > 0.05 else "",
            "cliente_referencia": fake.name().upper() if random.random() < 0.3 else fake.name(),
            "email_contacto": fake.email().upper() if random.random() < 0.4 else f" {fake.email()} ",
            "plan": plan,
            "monto_mensual": ensuciar_monto(monto_base),
            "estado_cuenta": ensuciar_estado(random.choice(estados_base)),
            "fecha_registro": ensuciar_fecha(fake)
        }
        registros.append(fila)

    registros.extend(random.sample(registros, 5))
    random.shuffle(registros)

    columnas = [
        "tx_id", "user_id", "cliente_referencia", "email_contacto",
        "plan", "monto_mensual", "estado_cuenta", "fecha_registro"
    ]

    with open(archivo_salida, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columnas)
        writer.writeheader()
        writer.writerows(registros)

    print(f"\n¡Listo, {nombre_estudiante.strip()}!")
    print(f"Tu semilla asignada es: {semilla}")
    print(f"Se ha generado tu archivo '{archivo_salida}' con {len(registros)} registros.")

if __name__ == "__main__":
    generar_csv()