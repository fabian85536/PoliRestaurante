import logging
from datetime import datetime

from models.detalle_pedido_DAO import DetallePedidoDAO
from models.pedido_DAO import PedidoDAO


def _completar_datos_pedido(pedido, detalle_dao: DetallePedidoDAO) -> None:
    detalle_dao.recalcular_total_pedido(pedido.id_pedido)
    if not pedido.estado:
        pedido.estado = "Pendiente"
    if not pedido.fecha_creacion:
        pedido.fecha_creacion = datetime.now().astimezone().isoformat(
            timespec="seconds"
        )


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
        datos_pedido = dict(datos_pedido)
        datos_pedido.setdefault("estado", "Pendiente")
        datos_pedido.setdefault(
            "fecha_creacion",
            datetime.now().astimezone().isoformat(timespec="seconds"),
        )
        pedido_id = pedido_dao.agregar_pedido(**datos_pedido)
        for detalle in detalles:
            detalle_dao.agregar_detalle(id_pedido=pedido_id, **detalle)
        pedido = pedido_dao.obtener_por_id(pedido_id)
        _completar_datos_pedido(pedido, detalle_dao)
        sesion.commit()
        logging.info(
            "Pedido %s creado con %s detalle(s)", pedido_id, len(detalles)
        )
        return pedido_id
    except Exception:
        sesion.rollback()
        logging.exception("No se pudo crear el pedido con sus detalles")
        raise


def agregar_detalles_a_pedido(
    pedido_dao: PedidoDAO,
    detalle_dao: DetallePedidoDAO,
    pedido,
    detalles: list[dict],
    *,
    tipo_pedido: str | None = None,
    nombre_cliente: str | None = None,
) -> int:
    if pedido_dao.sesion is not detalle_dao.sesion:
        raise ValueError("Los dos DAO deben compartir la misma sesión.")
    if not detalles:
        raise ValueError("El pedido debe incluir al menos un detalle.")

    sesion = pedido_dao.sesion
    try:
        for detalle in detalles:
            detalle_dao.agregar_detalle(
                id_pedido=pedido.id_pedido, **detalle
            )
        if not pedido.tipo_pedido and tipo_pedido:
            pedido.tipo_pedido = tipo_pedido
        if not pedido.nombre_cliente and nombre_cliente:
            pedido.nombre_cliente = nombre_cliente
        _completar_datos_pedido(pedido, detalle_dao)
        sesion.commit()
        logging.info(
            "Se agregaron %s detalle(s) al pedido %s",
            len(detalles),
            pedido.id_pedido,
        )
        return pedido.id_pedido
    except Exception:
        sesion.rollback()
        logging.exception(
            "No se pudieron agregar productos al pedido %s", pedido.id_pedido
        )
        raise
