package com.polirestaurante.crudpostgresqlorm.usuario;

import java.util.List;

import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional
public class UsuarioService {

    private final UsuarioRepository repository;

    public UsuarioService(UsuarioRepository repository) {
        this.repository = repository;
    }

    public UsuarioResponse crear(UsuarioRequest request) {
        if (repository.existsByEmailIgnoreCase(request.email())) {
            throw new EmailDuplicadoException();
        }

        try {
            Usuario usuario = repository.saveAndFlush(
                    new Usuario(request.nombre().trim(), request.email().trim()));
            return UsuarioResponse.desde(usuario);
        } catch (DataIntegrityViolationException exception) {
            throw new EmailDuplicadoException(exception);
        }
    }

    @Transactional(readOnly = true)
    public List<UsuarioResponse> listar() {
        return repository.findAll().stream().map(UsuarioResponse::desde).toList();
    }

    @Transactional(readOnly = true)
    public UsuarioResponse obtener(Long id) {
        return UsuarioResponse.desde(buscar(id));
    }

    public UsuarioResponse actualizar(Long id, UsuarioRequest request) {
        Usuario usuario = buscar(id);
        if (repository.existsByEmailIgnoreCaseAndIdNot(request.email(), id)) {
            throw new EmailDuplicadoException();
        }

        usuario.setNombre(request.nombre().trim());
        usuario.setEmail(request.email().trim());
        try {
            return UsuarioResponse.desde(repository.saveAndFlush(usuario));
        } catch (DataIntegrityViolationException exception) {
            throw new EmailDuplicadoException(exception);
        }
    }

    public void eliminar(Long id) {
        repository.delete(buscar(id));
    }

    private Usuario buscar(Long id) {
        return repository.findById(id).orElseThrow(() -> new UsuarioNoEncontradoException(id));
    }
}
