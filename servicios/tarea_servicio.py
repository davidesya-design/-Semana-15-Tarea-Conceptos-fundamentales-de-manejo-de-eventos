"""Capa de servicios: operaciones sobre las tareas."""
from typing import Dict, List
from modelos.tarea import Tarea


class TareaServicio:
    def __init__(self) -> None:
        self._tareas: Dict[int, Tarea] = {}

    def agregar(self, descripcion: str) -> Tarea:
        """Crea y almacena una nueva tarea."""
        descripcion_limpia = descripcion.strip()
        if not descripcion_limpia:
            raise ValueError("La descripción no puede estar vacía.")
        tarea = Tarea(descripcion_limpia)
        self._tareas[tarea.id] = tarea
        return tarea

    def marcar_completada(self, tarea_id: int) -> None:
        tarea = self._obtener_existente(tarea_id)
        tarea.marcar_completada()

    def eliminar(self, tarea_id: int) -> None:
        self._obtener_existente(tarea_id)
        del self._tareas[tarea_id]

    def listar(self) -> List[Tarea]:
        """Devuelve las tareas ordenadas por id."""
        return sorted(self._tareas.values(), key=lambda t: t.id)

    def _obtener_existente(self, tarea_id: int) -> Tarea:
        if tarea_id not in self._tareas:
            raise KeyError(f"No se encontró la tarea con id {tarea_id}.")
        return self._tareas[tarea_id]
