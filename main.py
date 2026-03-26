"""Punto de entrada de la aplicación Lista de Tareas."""
from servicios.tarea_servicio import TareaServicio
from ui.app_tkinter import ListaTareasApp


def main() -> None:
    """Configura dependencias y lanza la interfaz Tkinter."""
    servicio = TareaServicio()
    app = ListaTareasApp(servicio)
    app.iniciar()


if __name__ == "__main__":
    main()
