from dataclasses import dataclass


@dataclass
class Usuario:
    id: int
    nombre: str
    email: str
