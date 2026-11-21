from rich import box
from rich.console import Console
from rich.table import Table


COLOR_ESTADO = {"Activo": "green", "Suspendido": "yellow", "Moroso": "red", "Cancelado": "red"}


def mostrar_tabla(cruzadas, sin_usuario, duplicados):
    console = Console()
    tabla = Table(title="Transacciones cruzadas", box=box.ROUNDED,
                  header_style="bold white on grey30", border_style="white")
    tabla.add_column("TX", style="bold yellow", no_wrap=True)
    tabla.add_column("Cliente", style="bold white")
    tabla.add_column("Empresa", style="magenta")
    tabla.add_column("Ciudad", style="cyan")
    tabla.add_column("Plan", style="bright_yellow")
    tabla.add_column("Monto", justify="right", style="green")
    tabla.add_column("Estado", justify="center")
    tabla.add_column("Fecha", justify="center", style="dim")
    for tx, u in cruzadas:
        estado = tx["estado"] or "-"
        color = COLOR_ESTADO.get(estado, "white")
        tabla.add_row(tx["tx_id"], tx["cliente"], u["company"]["name"],
                      u["address"]["city"], tx["plan"],
                      f"{tx['monto']:,.2f}" if tx["monto"] is not None else "-",
                      f"[{color}]{estado}[/{color}]", tx["fecha"] or "-")
    console.print(tabla)
    console.print(f"Cruzadas: {len(cruzadas)} | Sin usuario en API: {sin_usuario} "
                  f"| Duplicados eliminados: {duplicados}")
