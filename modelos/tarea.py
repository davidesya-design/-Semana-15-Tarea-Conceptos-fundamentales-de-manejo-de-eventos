"""Modelo de dominio para representar una tarea."""
from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class Tarea:
    descripcion: str
    completada: bool = False
    id: int = field(init=False)

    # contador simple para generar ids únicos en memoria
    _contador: ClassVar[int] = 1

    def __post_init__(self) -> None:
        self.id = Tarea._contador
        Tarea._contador += 1

    def marcar_completada(self) -> None:
        """Cambia el estado de completada."""
        self.completada = True
