package com.polirestaurante.crudpostgresqlorm.usuario;

import static org.hamcrest.Matchers.containsString;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
class UsuarioControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private UsuarioRepository repository;

    @BeforeEach
    void limpiarBaseDeDatos() {
        repository.deleteAll();
    }

    @Test
    void realizaOperacionesCrud() throws Exception {
        String crearResponse = mockMvc.perform(post("/api/usuarios")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {"nombre":"Ana","email":"ana@example.com"}
                                """))
                .andExpect(status().isCreated())
                .andExpect(header().string("Location", containsString("/api/usuarios/")))
                .andExpect(jsonPath("$.nombre").value("Ana"))
                .andReturn()
                .getResponse()
                .getContentAsString();

        Long id = com.fasterxml.jackson.databind.json.JsonMapper.builder()
                .build()
                .readTree(crearResponse)
                .get("id")
                .asLong();

        mockMvc.perform(get("/api/usuarios"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].email").value("ana@example.com"));

        mockMvc.perform(get("/api/usuarios/{id}", id))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(id));

        mockMvc.perform(put("/api/usuarios/{id}", id)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {"nombre":"Ana María","email":"ana.maria@example.com"}
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.nombre").value("Ana María"));

        mockMvc.perform(delete("/api/usuarios/{id}", id))
                .andExpect(status().isNoContent());

        mockMvc.perform(get("/api/usuarios/{id}", id))
                .andExpect(status().isNotFound());
    }

    @Test
    void rechazaEmailDuplicado() throws Exception {
        String usuario = """
                {"nombre":"Ana","email":"ana@example.com"}
                """;
        mockMvc.perform(post("/api/usuarios")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(usuario))
                .andExpect(status().isCreated());

        mockMvc.perform(post("/api/usuarios")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {"nombre":"Otra Ana","email":"ana@example.com"}
                                """))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.error").value(containsString("email")));
    }

    @Test
    void validaNombreYEmail() throws Exception {
        mockMvc.perform(post("/api/usuarios")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {"nombre":" ","email":"incorrecto"}
                                """))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error").exists());
    }

    @Test
    void buscaUsuariosPorNombreYEmailConMetodosDerivados() {
        repository.save(new Usuario("Ana", "ana@example.com"));
        repository.save(new Usuario("Ana", "ana.otra@example.com"));
        repository.save(new Usuario("Luis", "luis@example.com"));
        repository.flush();

        assertEquals(2, repository.findByNombre("Ana").size());
        assertEquals(
                "Ana",
                repository.findByEmail("ana@example.com").getNombre());
        assertNull(repository.findByEmail("inexistente@example.com"));
    }
}
