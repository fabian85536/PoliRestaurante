package com.polirestaurante.crudpostgresqlorm.usuario;

public class EmailDuplicadoException extends RuntimeException {

    public EmailDuplicadoException() {
        super("Ya existe un usuario con ese email.");
    }

    public EmailDuplicadoException(Throwable cause) {
        super("Ya existe un usuario con ese email.", cause);
    }
}
