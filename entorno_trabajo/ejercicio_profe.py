import argparse
from collections import defaultdict
import csv
import glob
import os
import sys
from datetime import datetime
import requests
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

try:
    import matplotlib
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    MATPLOTLIB_DISPONIBLE = True
except ImportError:
    MATPLOTLIB_DISPONIBLE = False


class Usuario:
    def __init__(self, id_usuario, nombre, username, email, telefono, ciudad, empresa, ubicacion):
        self.id = id_usuario
        self.nombre = nombre
        self.username = username
        self.email = email
        self.telefono = telefono
        self.ciudad = ciudad
        self.empresa = empresa
        self.ubicacion = ubicacion

    @classmethod
    def from_dict(cls, data):
        address = data.get("address", {})
        geo = address.get("geo", {})
        ubicacion = f"{geo.get('lat', '')}, {geo.get('lng', '')}"
        company = data.get("company", {})
        return cls(
            id_usuario=data.get("id"),
            nombre=data.get("name", ""),
            username=data.get("username", ""),
            email=data.get("email", ""),
            telefono=data.get("phone", ""),
            ciudad=address.get("city", ""),
            empresa=company.get("name", ""),
            ubicacion=ubicacion
        )


class Transaccion:
    def __init__(self, tx_id, user_id, cliente_referencia, email_contacto, plan, monto_mensual, estado_cuenta, fecha_registro):
        self.tx_id = tx_id
        self.user_id = user_id
        self.cliente_referencia = cliente_referencia
        self.email_contacto = email_contacto
        self.plan = plan
        self.monto_mensual = monto_mensual
        self.estado_cuenta = estado_cuenta
        self.fecha_registro = fecha_registro
        self.usuario = None

    def asociar_usuario(self, usuario):
        self.usuario = usuario


class APIService:
    def __init__(self, url="https://jsonplaceholder.typicode.com/users"):
        self.url = url

    def obtener_usuarios(self):
        response = requests.get(self.url, timeout=10)
        response.raise_for_status()
        usuarios = {}
        for item in response.json():
            user = Usuario.from_dict(item)
            usuarios[user.id] = user
        return usuarios


class CSVExtractor:
    def __init__(self, ruta_archivo=None):
        self.ruta_archivo = ruta_archivo or self._buscar_archivo()

    def _buscar_archivo(self):
        if os.path.exists("facturacion.csv"):
            return "facturacion.csv"
        archivos_transacciones = glob.glob("transacciones_*.csv")
        if archivos_transacciones:
            return sorted(archivos_transacciones, key=os.path.getmtime, reverse=True)[0]
        otros_csv = [f for f in glob.glob("*.csv") if f not in ("datos.csv",)]
        if otros_csv:
            return sorted(otros_csv, key=os.path.getmtime, reverse=True)[0]
        try:
            from generar_datos import generar_csv
            generar_csv()
            archivos = glob.glob("transacciones_*.csv")
            if archivos:
                return sorted(archivos, key=os.path.getmtime, reverse=True)[0]
        except Exception:
            pass
        raise FileNotFoundError("No se encontró ningún archivo CSV para procesar.")

    def extraer(self):
        with open(self.ruta_archivo, mode="r", encoding="utf-8") as f:
            lector = csv.DictReader(f)
            return list(lector)


class LimpiadorDatos:
    def limpiar_monto(self, monto_str):
        if monto_str is None:
            return None
        texto = str(monto_str).replace("$", "").replace("USD", "").replace("usd", "").replace(",", "").strip()
        if not texto:
            return None
        try:
            return round(abs(float(texto)), 2)
        except ValueError:
            return None

    def limpiar_estado(self, estado_str):
        if not estado_str:
            return "Desconocido"
        val = str(estado_str).strip().capitalize()
        if val in ["Activo", "Suspendido", "Moroso", "Cancelado"]:
            return val
        return "Desconocido"

    def limpiar_fecha(self, fecha_str):
        if not fecha_str:
            return ""
        texto = str(fecha_str).strip()
        for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%b-%Y"]:
            try:
                return datetime.strptime(texto, fmt).strftime("%Y-%m-%d")
            except ValueError:
                pass
        meses = {
            "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
            "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12",
            "ene": "01", "abr": "04", "ago": "08", "dic": "12"
        }
        partes = texto.split("-")
        if len(partes) == 3 and partes[1].lower() in meses:
            dia = partes[0].zfill(2)
            mes = meses[partes[1].lower()]
            anio = partes[2]
            return f"{anio}-{mes}-{dia}"
        return texto

    def procesar(self, registros_crudos):
        metricas = {
            "total_leidos": len(registros_crudos),
            "duplicados_eliminados": 0,
            "sin_user_id": 0,
            "sin_monto": 0,
            "montos_corregidos": 0,
            "validos": 0
        }
        transacciones = []
        ids_vistos = set()

        for fila in registros_crudos:
            tx_id = fila.get("tx_id", "").strip()
            if not tx_id or tx_id in ids_vistos:
                metricas["duplicados_eliminados"] += 1
                continue
            ids_vistos.add(tx_id)

            user_id_raw = fila.get("user_id", "").strip()
            if not user_id_raw or not user_id_raw.isdigit():
                metricas["sin_user_id"] += 1
                continue
            user_id = int(user_id_raw)

            monto_raw = fila.get("monto_mensual", "")
            if "-" in str(monto_raw) or "$" in str(monto_raw) or "USD" in str(monto_raw):
                metricas["montos_corregidos"] += 1

            monto = self.limpiar_monto(monto_raw)
            if monto is None:
                metricas["sin_monto"] += 1
                continue

            estado = self.limpiar_estado(fila.get("estado_cuenta", ""))
            plan = fila.get("plan", "").strip().capitalize()
            fecha = self.limpiar_fecha(fila.get("fecha_registro", ""))
            cliente_ref = fila.get("cliente_referencia", "").strip().title()
            email_ref = fila.get("email_contacto", "").strip().lower()

            tx = Transaccion(
                tx_id=tx_id,
                user_id=user_id,
                cliente_referencia=cliente_ref,
                email_contacto=email_ref,
                plan=plan,
                monto_mensual=monto,
                estado_cuenta=estado,
                fecha_registro=fecha
            )
            transacciones.append(tx)

        metricas["validos"] = len(transacciones)
        return transacciones, metricas


class IntegradorDatos:
    def asociar(self, transacciones, usuarios):
        metricas = {
            "total_transacciones": len(transacciones),
            "asociadas_exitosas": 0,
            "usuarios_no_encontrados": 0
        }
        for tx in transacciones:
            if tx.user_id in usuarios:
                tx.asociar_usuario(usuarios[tx.user_id])
                metricas["asociadas_exitosas"] += 1
            else:
                metricas["usuarios_no_encontrados"] += 1
        return transacciones, metricas


class ReporteEjecutivo:
    def __init__(self):
        self.console = Console()

    def _estilo_estado(self, estado):
        colores = {
            "Activo": "[bold green]Activo[/bold green]",
            "Moroso": "[bold red]Moroso[/bold red]",
            "Suspendido": "[bold yellow]Suspendido[/bold yellow]",
            "Cancelado": "[bold magenta]Cancelado[/bold magenta]"
        }
        return colores.get(estado, f"[dim]{estado}[/dim]")

    def _estilo_plan(self, plan):
        colores = {
            "Enterprise": "[bold cyan]Enterprise[/bold cyan]",
            "Pro": "[bold blue]Pro[/bold blue]",
            "Basic": "[white]Basic[/white]"
        }
        return colores.get(plan, plan)

    def _barra_grafica(self, valor, max_valor, ancho=16, color="green"):
        """Genera una barra visual en consola para gráficos terminales."""
        if max_valor <= 0 or valor <= 0:
            return ""
        longitud = max(1, int(round((valor / max_valor) * ancho)))
        bloques = "█" * longitud
        return f"[{color}]{bloques}[/{color}]"

    def mostrar_encabezado(self, archivo_fuente):
        titulo = "[bold white]PIPELINE DE FACTURACIÓN Y CLIENTES[/bold white]\n" \
                 f"[dim]Origen de datos:[/dim] [cyan]{archivo_fuente}[/cyan] | " \
                 f"[dim]API:[/dim] [link=https://jsonplaceholder.typicode.com/users]jsonplaceholder.typicode.com/users[/link]"
        panel = Panel.fit(
            titulo,
            box=box.DOUBLE,
            border_style="bright_blue",
            padding=(0, 2)
        )
        self.console.print(panel)

    def mostrar_metricas(self, metricas_limpieza, metricas_cruce, transacciones):
        total_facturado = sum(tx.monto_mensual for tx in transacciones)
        ticket_promedio = total_facturado / len(transacciones) if transacciones else 0.0

        tabla = Table(box=box.SIMPLE, show_header=False, border_style="dim")
        tabla.add_column(style="bold white")
        tabla.add_column(style="bold cyan", justify="right")
        tabla.add_column(style="bold white")
        tabla.add_column(style="bold green", justify="right")

        tabla.add_row(
            "Registros CSV leídos:",
            str(metricas_limpieza["total_leidos"]),
            "Total facturado:",
            f"${total_facturado:,.2f}"
        )
        tabla.add_row(
            "Duplicados descartados:",
            str(metricas_limpieza["duplicados_eliminados"]),
            "Ticket promedio:",
            f"${ticket_promedio:,.2f}"
        )
        tabla.add_row(
            "Incompletos descartados:",
            str(metricas_limpieza["sin_user_id"] + metricas_limpieza["sin_monto"]),
            "Transacciones válidas:",
            str(metricas_limpieza["validos"])
        )
        tabla.add_row(
            "Montos sanitizados:",
            str(metricas_limpieza["montos_corregidos"]),
            "Asociadas con API:",
            f"{metricas_cruce['asociadas_exitosas']} ({metricas_cruce['usuarios_no_encontrados']} sin match)"
        )

        panel = Panel(tabla, title="[bold yellow]Métricas Clave de la Ejecución[/bold yellow]", border_style="yellow", box=box.ROUNDED)
        self.console.print(panel)

    def mostrar_resumen_estados(self, transacciones):
        tabla = Table(
            title="Distribución y Gráfica por Estado de Cuenta",
            border_style="bright_blue",
            header_style="bold white on blue",
            box=box.ROUNDED,
            show_lines=True
        )

        tabla.add_column("Estado de Cuenta", style="bold")
        tabla.add_column("Transacciones", justify="right")
        tabla.add_column("Monto Total", justify="right", style="bold green")
        tabla.add_column("Participación", justify="right", style="bold yellow")
        tabla.add_column("Gráfica Visual", justify="left", no_wrap=True)

        total_general = sum(tx.monto_mensual for tx in transacciones)
        estados = {}
        for tx in transacciones:
            estados.setdefault(tx.estado_cuenta, []).append(tx)

        estados_montos = {est: sum(tx.monto_mensual for tx in txs) for est, txs in estados.items()}
        max_monto = max(estados_montos.values()) if estados_montos else 1.0

        colores_barra = {
            "Activo": "green",
            "Moroso": "red",
            "Suspendido": "yellow",
            "Cancelado": "magenta"
        }

        for estado, lista_tx in sorted(estados.items(), key=lambda item: len(item[1]), reverse=True):
            monto_estado = sum(tx.monto_mensual for tx in lista_tx)
            porcentaje = (monto_estado / total_general * 100) if total_general else 0
            color = colores_barra.get(estado, "cyan")
            barra = self._barra_grafica(monto_estado, max_monto, ancho=16, color=color)

            tabla.add_row(
                self._estilo_estado(estado),
                str(len(lista_tx)),
                f"${monto_estado:,.2f}",
                f"{porcentaje:.1f}%",
                f"{barra} {porcentaje:.1f}%"
            )

        self.console.print(tabla)

    def mostrar_grafico_planes(self, transacciones):
        tabla = Table(
            title="Distribución y Gráfica por Tipo de Plan",
            border_style="bright_cyan",
            header_style="bold white on cyan",
            box=box.ROUNDED,
            show_lines=True
        )

        tabla.add_column("Plan", style="bold")
        tabla.add_column("Transacciones", justify="right")
        tabla.add_column("Facturado Total", justify="right", style="bold green")
        tabla.add_column("% del Total", justify="right", style="bold yellow")
        tabla.add_column("Gráfica Comparativa", justify="left", no_wrap=True)

        total_general = sum(tx.monto_mensual for tx in transacciones)
        planes = defaultdict(list)
        for tx in transacciones:
            planes[tx.plan].append(tx)

        planes_montos = {p: sum(tx.monto_mensual for tx in txs) for p, txs in planes.items()}
        max_monto = max(planes_montos.values()) if planes_montos else 1.0

        colores_plan = {
            "Enterprise": "cyan",
            "Pro": "blue",
            "Basic": "bright_white"
        }

        for plan, txs in sorted(planes.items(), key=lambda x: sum(t.monto_mensual for t in x[1]), reverse=True):
            monto_plan = sum(t.monto_mensual for t in txs)
            pct = (monto_plan / total_general * 100) if total_general else 0.0
            color = colores_plan.get(plan, "white")
            barra = self._barra_grafica(monto_plan, max_monto, ancho=16, color=color)

            tabla.add_row(
                self._estilo_plan(plan),
                str(len(txs)),
                f"${monto_plan:,.2f}",
                f"{pct:.1f}%",
                f"{barra} {pct:.1f}%"
            )

        self.console.print(tabla)

    def mostrar_top_clientes(self, usuarios, transacciones, top_n=5):
        tabla = Table(
            title=f"Top {top_n} Clientes por Volumen de Facturación",
            border_style="bright_magenta",
            header_style="bold white on magenta",
            box=box.ROUNDED,
            show_lines=True
        )

        tabla.add_column("Puesto", justify="center", style="bold yellow")
        tabla.add_column("Cliente", style="bold white")
        tabla.add_column("Empresa", style="cyan")
        tabla.add_column("Tx", justify="right")
        tabla.add_column("Total Facturado", justify="right", style="bold green")
        tabla.add_column("Gráfica de Facturación", justify="left", no_wrap=True)

        clientes_data = defaultdict(lambda: {"nombre": "", "empresa": "", "txs": 0, "monto": 0.0})

        for tx in transacciones:
            uid = tx.user_id
            if uid in usuarios:
                u = usuarios[uid]
                clientes_data[uid]["nombre"] = u.nombre
                clientes_data[uid]["empresa"] = u.empresa
            else:
                clientes_data[uid]["nombre"] = tx.cliente_referencia or f"User #{uid}"
                clientes_data[uid]["empresa"] = "N/A"
            clientes_data[uid]["txs"] += 1
            clientes_data[uid]["monto"] += tx.monto_mensual

        top_lista = sorted(clientes_data.values(), key=lambda x: x["monto"], reverse=True)[:top_n]
        max_monto = top_lista[0]["monto"] if top_lista else 1.0

        for i, c in enumerate(top_lista, start=1):
            barra = self._barra_grafica(c["monto"], max_monto, ancho=14, color="bright_magenta")
            medalla = "🥇" if i == 1 else ("🥈" if i == 2 else ("🥉" if i == 3 else f"#{i}"))
            tabla.add_row(
                medalla,
                c["nombre"],
                c["empresa"],
                str(c["txs"]),
                f"${c['monto']:,.2f}",
                f"{barra} ${c['monto']:,.0f}"
            )

        self.console.print(tabla)

    def mostrar_resumen_clientes(self, usuarios, transacciones):
        tabla = Table(
            title="Consolidado de Clientes Maestros y Facturación",
            border_style="bright_blue",
            header_style="bold white on blue",
            box=box.ROUNDED,
            show_lines=True
        )

        tabla.add_column("ID", justify="right", style="dim", no_wrap=True)
        tabla.add_column("Cliente", style="bold white")
        tabla.add_column("Correo", style="blue")
        tabla.add_column("Ubicación", style="magenta")
        tabla.add_column("Empresa", style="yellow")
        tabla.add_column("Tx", justify="right", style="cyan")
        tabla.add_column("Facturado", justify="right", style="bold green")

        for user_id, usuario in sorted(usuarios.items()):
            txs_usuario = [tx for tx in transacciones if tx.user_id == user_id]
            total_monto = sum(tx.monto_mensual for tx in txs_usuario)
            tabla.add_row(
                str(usuario.id),
                usuario.nombre,
                usuario.email,
                usuario.ciudad,
                usuario.empresa,
                str(len(txs_usuario)),
                f"${total_monto:,.2f}"
            )

        self.console.print(tabla)

    def mostrar_transacciones_detalladas(self, transacciones, limite=10):
        tabla = Table(
            title=f"Muestra de Transacciones Cruzadas (Primeras {min(limite, len(transacciones))})",
            border_style="bright_blue",
            header_style="bold white on blue",
            box=box.ROUNDED,
            show_lines=True
        )

        tabla.add_column("Tx ID", style="dim", no_wrap=True)
        tabla.add_column("Cliente", style="bold white")
        tabla.add_column("Correo", style="blue")
        tabla.add_column("Ciudad", style="magenta")
        tabla.add_column("Empresa", style="yellow")
        tabla.add_column("Plan", justify="center")
        tabla.add_column("Monto", justify="right", style="bold green")
        tabla.add_column("Estado", justify="center")
        tabla.add_column("Fecha", justify="center", style="dim")

        for tx in transacciones[:limite]:
            cliente = tx.usuario.nombre if tx.usuario else tx.cliente_referencia
            correo = tx.usuario.email if tx.usuario else tx.email_contacto
            ciudad = tx.usuario.ciudad if tx.usuario else "N/A"
            empresa = tx.usuario.empresa if tx.usuario else "N/A"

            tabla.add_row(
                tx.tx_id,
                cliente,
                correo,
                ciudad,
                empresa,
                self._estilo_plan(tx.plan),
                f"${tx.monto_mensual:,.2f}",
                self._estilo_estado(tx.estado_cuenta),
                tx.fecha_registro
            )

        self.console.print(tabla)

    def mostrar_confirmacion_grafico(self, ruta_grafico):
        tamano_kb = os.path.getsize(ruta_grafico) / 1024 if os.path.exists(ruta_grafico) else 0.0
        contenido = (
            f"[bold green]✔ Dashboard de gráficos exportado exitosamente[/bold green]\n\n"
            f"[dim]Archivo:[/dim] [bold cyan]{ruta_grafico}[/bold cyan]  ([dim]{tamano_kb:.1f} KB[/dim])\n"
            f"[dim]Contenido:[/dim] 4 visualizaciones (Estado de Cuenta, Planes, Top Clientes y Línea Temporal).\n"
            f"[dim]Tip:[/dim] Para ver la ventana gráfica interactiva directamente, ejecuta con [yellow]--mostrar[/yellow]."
        )
        panel = Panel(contenido, title="[bold cyan]📊 Visualización Gráfica Exportada[/bold cyan]", border_style="cyan", box=box.ROUNDED)
        self.console.print(panel)

    def mostrar_aviso_sin_matplotlib(self):
        panel = Panel(
            "[yellow]Matplotlib no está instalado en este entorno.[/yellow]\n"
            "Se generaron los gráficos en consola con Rich. Para generar también gráficos PNG o interactivos, ejecuta:\n"
            "[bold cyan]pip install matplotlib[/bold cyan]",
            title="[bold yellow]Gráficos PNG[/bold yellow]",
            border_style="yellow",
            box=box.ROUNDED
        )
        self.console.print(panel)

    def generar_reporte(self, archivo_fuente, transacciones, usuarios, metricas_limpieza, metricas_cruce):
        self.console.print()
        self.mostrar_encabezado(archivo_fuente)
        self.console.print()
        self.mostrar_metricas(metricas_limpieza, metricas_cruce, transacciones)
        self.console.print()
        self.mostrar_resumen_estados(transacciones)
        self.console.print()
        self.mostrar_grafico_planes(transacciones)
        self.console.print()
        self.mostrar_top_clientes(usuarios, transacciones)
        self.console.print()
        self.mostrar_resumen_clientes(usuarios, transacciones)
        self.console.print()
        self.mostrar_transacciones_detalladas(transacciones)
        self.console.print()


class GeneradorGraficos:
    """Genera gráficos de alta resolución con matplotlib para el pipeline."""
    def __init__(self, ruta_salida="reporte_facturacion.png", mostrar_interactivo=False):
        self.ruta_salida = ruta_salida
        self.mostrar_interactivo = mostrar_interactivo

    def generar(self, transacciones, usuarios):
        if not MATPLOTLIB_DISPONIBLE:
            return None

        # 1. Agrupación por Estado
        estados_montos = defaultdict(float)
        for tx in transacciones:
            estados_montos[tx.estado_cuenta] += tx.monto_mensual
        estados_ordenados = sorted(estados_montos.items(), key=lambda x: x[1], reverse=True)

        # 2. Agrupación por Plan
        planes_montos = defaultdict(float)
        for tx in transacciones:
            planes_montos[tx.plan] += tx.monto_mensual
        planes_ordenados = sorted(planes_montos.items(), key=lambda x: x[1], reverse=True)

        # 3. Agrupación Top Clientes
        clientes_montos = defaultdict(float)
        for tx in transacciones:
            if tx.user_id in usuarios:
                nombre = usuarios[tx.user_id].nombre
            else:
                nombre = tx.cliente_referencia or f"User #{tx.user_id}"
            clientes_montos[nombre] += tx.monto_mensual
        top_clientes = sorted(clientes_montos.items(), key=lambda x: x[1], reverse=True)[:6]

        # 4. Agrupación por Mes
        meses_montos = defaultdict(float)
        for tx in transacciones:
            if tx.fecha_registro and len(tx.fecha_registro) >= 7:
                mes = tx.fecha_registro[:7]
            else:
                mes = "Sin fecha"
            meses_montos[mes] += tx.monto_mensual
        meses_ordenados = sorted([m for m in meses_montos.items() if m[0] != "Sin fecha"])

        # Configuración visual
        estilo_usar = 'seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default'
        plt.style.use(estilo_usar)

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.patch.set_facecolor('#f8fafc')

        # Subplot 1: Facturación por Estado
        ax1 = axes[0, 0]
        ax1.set_facecolor('#ffffff')
        colores_estado = {
            "Activo": "#10b981",
            "Moroso": "#ef4444",
            "Suspendido": "#f59e0b",
            "Cancelado": "#8b5cf6",
            "Desconocido": "#64748b"
        }
        nombres_est = [e[0] for e in estados_ordenados]
        montos_est = [e[1] for e in estados_ordenados]
        colores_barras_est = [colores_estado.get(e, "#3b82f6") for e in nombres_est]
        barras1 = ax1.bar(nombres_est, montos_est, color=colores_barras_est, width=0.55, edgecolor='#334155', linewidth=0.8)
        ax1.set_title("Facturación Total por Estado de Cuenta", fontsize=12, fontweight='bold', pad=10, color='#1e293b')
        ax1.set_ylabel("Monto Facturado (USD)", fontsize=10, color='#475569')
        ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
        max_val_est = max(montos_est) if montos_est else 1
        for bar in barras1:
            h = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                h + (max_val_est * 0.02),
                f"${h:,.0f}",
                ha='center',
                va='bottom',
                fontsize=9,
                fontweight='bold',
                color='#1e293b'
            )
        ax1.set_ylim(0, max_val_est * 1.15)

        # Subplot 2: Participación de Facturación por Plan (Donut)
        ax2 = axes[0, 1]
        ax2.set_facecolor('#ffffff')
        colores_plan = {
            "Enterprise": "#0284c7",
            "Pro": "#6366f1",
            "Basic": "#14b8a6"
        }
        nombres_plan = [p[0] for p in planes_ordenados]
        montos_plan = [p[1] for p in planes_ordenados]
        colores_pie = [colores_plan.get(p, "#94a3b8") for p in nombres_plan]

        wedges, texts, autotexts = ax2.pie(
            montos_plan,
            labels=nombres_plan,
            autopct='%1.1f%%',
            startangle=140,
            colors=colores_pie,
            wedgeprops=dict(width=0.42, edgecolor='white', linewidth=2.5),
            pctdistance=0.78,
            textprops=dict(color='#1e293b', fontweight='bold')
        )
        for at in autotexts:
            at.set_fontsize(9)
            at.set_color('white')
            at.set_weight('bold')
        ax2.set_title("Participación de Facturación por Plan", fontsize=12, fontweight='bold', pad=10, color='#1e293b')

        # Subplot 3: Top Clientes por Facturación
        ax3 = axes[1, 0]
        ax3.set_facecolor('#ffffff')
        top_nombres = [c[0] for c in top_clientes][::-1]
        top_montos = [c[1] for c in top_clientes][::-1]
        barras3 = ax3.barh(top_nombres, top_montos, color='#3b82f6', height=0.55, edgecolor='#1d4ed8', linewidth=0.8)
        ax3.set_title("Top Clientes con Mayor Facturación", fontsize=12, fontweight='bold', pad=10, color='#1e293b')
        ax3.set_xlabel("Monto Facturado (USD)", fontsize=10, color='#475569')
        ax3.xaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
        max_top = max(top_montos) if top_montos else 1
        for bar in barras3:
            w = bar.get_width()
            ax3.text(
                w + (max_top * 0.015),
                bar.get_y() + bar.get_height() / 2,
                f"${w:,.0f}",
                ha='left',
                va='center',
                fontsize=9,
                fontweight='bold',
                color='#1e293b'
            )
        ax3.set_xlim(0, max_top * 1.22)

        # Subplot 4: Evolución Mensual
        ax4 = axes[1, 1]
        ax4.set_facecolor('#ffffff')
        if meses_ordenados:
            meses_labels = [m[0] for m in meses_ordenados]
            meses_vals = [m[1] for m in meses_ordenados]
            ax4.plot(meses_labels, meses_vals, marker='o', linewidth=2.5, markersize=6, color='#0f766e')
            ax4.fill_between(meses_labels, meses_vals, color='#0f766e', alpha=0.15)
            ax4.set_xticks(range(len(meses_labels)))
            ax4.set_xticklabels(meses_labels, rotation=45, ha='right', fontsize=8)
            ax4.yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
            ax4.set_ylim(0, max(meses_vals) * 1.15 if meses_vals else 1)
        ax4.set_title("Evolución Temporal de Facturación", fontsize=12, fontweight='bold', pad=10, color='#1e293b')
        ax4.set_ylabel("Monto Mensual (USD)", fontsize=10, color='#475569')

        plt.suptitle("Dashboard Ejecutivo de Facturación y Clientes", fontsize=16, fontweight='bold', color='#0f172a', y=0.98)
        plt.tight_layout(rect=[0, 0, 1, 0.96])

        ruta_abs = os.path.abspath(self.ruta_salida)
        fig.savefig(ruta_abs, dpi=180, facecolor=fig.get_facecolor(), bbox_inches='tight')

        if self.mostrar_interactivo:
            plt.show()

        plt.close(fig)
        return ruta_abs


class PipelineFacturacion:
    def __init__(self, ruta_archivo=None, generar_graficos=True, mostrar_graficos=False, ruta_salida_grafico="reporte_facturacion.png"):
        self.extractor = CSVExtractor(ruta_archivo)
        self.api_service = APIService()
        self.limpiador = LimpiadorDatos()
        self.integrador = IntegradorDatos()
        self.reporte = ReporteEjecutivo()
        self.generar_graficos = generar_graficos
        self.graficador = GeneradorGraficos(ruta_salida=ruta_salida_grafico, mostrar_interactivo=mostrar_graficos)

    def ejecutar(self):
        registros_crudos = self.extractor.extraer()
        usuarios = self.api_service.obtener_usuarios()
        transacciones, metricas_limpieza = self.limpiador.procesar(registros_crudos)
        transacciones, metricas_cruce = self.integrador.asociar(transacciones, usuarios)

        self.reporte.generar_reporte(
            self.extractor.ruta_archivo,
            transacciones,
            usuarios,
            metricas_limpieza,
            metricas_cruce
        )

        if self.generar_graficos:
            ruta_imagen = self.graficador.generar(transacciones, usuarios)
            if ruta_imagen:
                self.reporte.mostrar_confirmacion_grafico(ruta_imagen)
            else:
                self.reporte.mostrar_aviso_sin_matplotlib()


def main():
    parser = argparse.ArgumentParser(
        description="Pipeline ETL y Reporte Ejecutivo de Facturación y Clientes con Gráficos"
    )
    parser.add_argument(
        "archivo",
        nargs="?",
        default=None,
        help="Ruta opcional al archivo CSV de facturación (si se omite, se detecta automáticamente)"
    )
    parser.add_argument(
        "--mostrar", "-m",
        action="store_true",
        help="Abre una ventana interactiva con las gráficas de matplotlib"
    )
    parser.add_argument(
        "--no-png",
        action="store_true",
        help="Desactiva la generación y guardado del archivo PNG de gráficas"
    )
    parser.add_argument(
        "--salida-grafico", "-o",
        default="reporte_facturacion.png",
        help="Nombre/ruta del archivo PNG donde se guardará el dashboard de gráficas (por defecto: reporte_facturacion.png)"
    )

    args = parser.parse_args()

    pipeline = PipelineFacturacion(
        ruta_archivo=args.archivo,
        generar_graficos=not args.no_png,
        mostrar_graficos=args.mostrar,
        ruta_salida_grafico=args.salida_grafico
    )
    pipeline.ejecutar()


if __name__ == "__main__":
    main()
