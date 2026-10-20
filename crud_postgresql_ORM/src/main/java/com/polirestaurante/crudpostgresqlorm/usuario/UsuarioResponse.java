package com.polirestaurante.crudpostgresqlorm.usuario;

public record UsuarioResponse(Long id, String nombre, String email) {
    public static UsuarioResponse desde(Usuario usuario) {
        return new UsuarioResponse(usuario.getId(), usuario.getNombre(), usuario.getEmail());
    }
}
