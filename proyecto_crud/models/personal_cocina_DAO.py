import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.personal_cocina import PersonalCocina


class PersonalCocinaDAO:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def crear_personal_cocina(self, nombre, usuario, contrasena):
        try:
            personal = PersonalCocina(
                nombre=nombre, usuario=usuario, contrasena=contrasena
            )
            personal.validar()
            self.sesion.add(personal)
            self.sesion.commit()
            logging.info("Personal de cocina creado: %s", personal.usuario)
            return personal.id_cocina
        except ValueError:
            self.sesion.rollback()
            raise
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al crear personal de cocina")
            raise

    def obtener_personal_cocina(self):
        consulta = select(PersonalCocina).order_by(PersonalCocina.id_cocina)
        return list(self.sesion.scalars(consulta).all())

    def obtener_por_id(self, id_cocina):
        return self.sesion.get(PersonalCocina, id_cocina)

    def actualizar(self, id_cocina, **datos):
        try:
            personal = self.obtener_por_id(id_cocina)
            if personal is None:
                self.sesion.rollback()
                return False
            personal.actualizar(**datos)
            self.sesion.commit()
            return True
        except ValueError:
            self.sesion.rollback()
            raise
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al actualizar personal de cocina")
            raise

    def eliminar(self, id_cocina):
        try:
            personal = self.obtener_por_id(id_cocina)
            if personal is None:
                self.sesion.rollback()
                return False
            self.sesion.delete(personal)
            self.sesion.commit()
            return True
        except Exception:
            self.sesion.rollback()
            logging.exception("Error al eliminar personal de cocina")
            raise
