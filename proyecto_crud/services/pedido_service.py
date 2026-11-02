import logging

from models.detalle_pedido_DAO import DetallePedidoDAO
from models.pedido_DAO import PedidoDAO


def crear_pedido_con_detalles(
    pedido_dao: PedidoDAO,
    detalle_dao: DetallePedidoDAO,
    datos_pedido: dict,
    detalles: list[dict],
) -> int:
    if pedido_dao.sesion is not detalle_dao.sesion:
        raise ValueError("Los dos DAO deben compartir la misma sesión.")
    if not detalles:
        raise ValueError("El pedido debe incluir al menos un detalle.")

    sesion = pedido_dao.sesion
    try:
        pedido_id = pedido_dao.agregar_pedido(**datos_pedido)
        for detalle in detalles:
            detalle_dao.agregar_detalle(id_pedido=pedido_id, **detalle)
        sesion.commit()
        logging.info(
            "Pedido %s creado con %s detalle(s)", pedido_id, len(detalles)
        )
        return pedido_id
    except Exception:
        sesion.rollback()
        logging.exception("No se pudo crear el pedido con sus detalles")
        raise
