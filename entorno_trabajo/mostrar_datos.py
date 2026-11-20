from rich.console import Console
from rich.table import Table

from modulos_externos import data


def show_table(users):
    console = Console()
    
    table = Table(
        title="Directorio de clientes registrados",
        show_lines=True
    )
    
    table.add_column("ID", justify="right", style="dim", no_wrap=True)
    table.add_column("Apellidos y Nombres", style="bold white")
    table.add_column("Correo", style="blue")
    table.add_column("Ubicación", style="magenta")
    table.add_column("Empresa", justify="center", style="yellow")
    table.add_column("Estado", justify="center")
    
    for user in data:
        table.add_row(
            str(user['id']),
            user['name'],
            user['email'],
            f"{user['address']['geo']['lat']}, {user['address']['geo']['lng']}",
            user['company']['name'],
            'Activo'
        )
    console.print(table)

def main():
    show_table(data)

if __name__ == '__main__':
    main()