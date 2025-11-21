import pytest
import tempfile
import os
from datetime import datetime, timedelta
from app.managers.cita_manager import CitaManager

class TestCitaManager:
    
    @pytest.fixture
    def temp_dir(self):
        """Crea un directorio temporal para las pruebas"""
        with tempfile.TemporaryDirectory() as tmpdirname:
            yield tmpdirname
    
    @pytest.fixture
    def cita_manager(self, temp_dir):
        """Crea una instancia de CitaManager con directorio temporal"""
        return CitaManager(base_path=temp_dir)
    
    def test_agendar_cita_exito(self, cita_manager):
        """Prueba que se pueda agendar una cita correctamente"""
        documento = "123456789"
        cita = cita_manager.agendar_cita(
            paciente="Juan Perez",
            medico="Dr. Smith",
            fecha=(datetime.now() + timedelta(days=1)).isoformat(),
            documento=documento,
            tipoCita="Consulta",
            motivoPaciente="Dolor de cabeza"
        )
        
        # Verificar que la cita tenga todos los campos requeridos
        assert cita["paciente"] == "Juan Perez"
        assert cita["medico"] == "Dr. Smith"
        assert cita["documento"] == documento
        assert cita["tipoCita"] == "Consulta"
        assert cita["motivoPaciente"] == "Dolor de cabeza"
        assert "codigo_cita" in cita
        assert "registrado" in cita
        assert "prioridad" in cita
        
        # Verificar que la cita se haya guardado
        citas_guardadas = cita_manager.obtener_citas_paciente(documento)
        assert len(citas_guardadas) == 1
        assert citas_guardadas[0]["codigo_cita"] == cita["codigo_cita"]
    
    def test_obtener_citas_paciente(self, cita_manager):
        """Prueba que se puedan obtener las citas de un paciente"""
        documento = "987654321"
        
        # Agendar varias citas
        cita1 = cita_manager.agendar_cita(
            paciente="Maria Garcia",
            medico="Dr. Jones",
            fecha=(datetime.now() + timedelta(days=2)).isoformat(),
            documento=documento,
            tipoCita="Control",
            motivoPaciente="Chequeo general"
        )
        
        cita2 = cita_manager.agendar_cita(
            paciente="Maria Garcia",
            medico="Dr. Wilson",
            fecha=(datetime.now() + timedelta(days=3)).isoformat(),
            documento=documento,
            tipoCita="Examen",
            motivoPaciente="Examen de sangre"
        )
        
        # Obtener citas
        citas = cita_manager.obtener_citas_paciente(documento)
        
        # Verificar que se obtengan las citas correctamente
        assert len(citas) == 2
        codigos_citas = [cita["codigo_cita"] for cita in citas]
        assert cita1["codigo_cita"] in codigos_citas
        assert cita2["codigo_cita"] in codigos_citas
    
    def test_eliminar_cita(self, cita_manager):
        """Prueba que se pueda eliminar una cita"""
        documento = "456789123"
        
        # Agendar una cita
        cita = cita_manager.agendar_cita(
            paciente="Carlos Lopez",
            medico="Dr. Brown",
            fecha=(datetime.now() + timedelta(days=1)).isoformat(),
            documento=documento,
            tipoCita="Consulta",
            motivoPaciente="Revision"
        )
        
        # Verificar que la cita se haya guardado
        citas = cita_manager.obtener_citas_paciente(documento)
        assert len(citas) == 1
        
        # Eliminar la cita
        resultado = cita_manager.eliminar_cita(
            paciente="Carlos Lopez",
            medico="Dr. Brown",
            fecha=cita["fecha"],
            documento=documento
        )
        
        # Verificar que se eliminó correctamente
        assert resultado is True
        
        # Verificar que ya no hay citas
        citas_restantes = cita_manager.obtener_citas_paciente(documento)
        assert len(citas_restantes) == 0
    
    def test_eliminar_cita_no_existente(self, cita_manager):
        """Prueba que eliminar una cita que no existe retorne False"""
        documento = "111111111"
        
        resultado = cita_manager.eliminar_cita(
            paciente="Paciente Fantasma",
            medico="Dr. Fantasma",
            fecha=datetime.now().isoformat(),
            documento=documento
        )
        
        assert resultado is False
    
    def test_verificar_fecha_pasada_lanza_error(self, cita_manager):
        """Prueba que no se puedan agendar citas en el pasado"""
        with pytest.raises(ValueError, match="No se puede agendar una cita en una fecha pasada"):
            cita_manager.agendar_cita(
                paciente="Pedro Martinez",
                medico="Dr. Johnson",
                fecha="2020-01-01T10:00:00",
                documento="222222222",
                tipoCita="Consulta",
                motivoPaciente="Dolor"
            )
    
    def test_verificar_formato_fecha_invalido(self, cita_manager):
        """Prueba que se lance error con formato de fecha inválido"""
        with pytest.raises(ValueError, match="Formato de fecha inválido"):
            cita_manager.agendar_cita(
                paciente="Pedro Martinez",
                medico="Dr. Johnson",
                fecha="fecha-invalida",
                documento="333333333",
                tipoCita="Consulta",
                motivoPaciente="Dolor"
            )
    
    def test_calcular_prioridad(self, cita_manager):
        """Prueba que se calcule correctamente la prioridad según el tipo de cita"""
        # Probar diferentes tipos de citas
        assert cita_manager._calcular_prioridad("Emergencia") == 1
        assert cita_manager._calcular_prioridad("Urgencia") == 2
        assert cita_manager._calcular_prioridad("Consulta") == 3
        assert cita_manager._calcular_prioridad("Control") == 4
        assert cita_manager._calcular_prioridad("Reevaluacion") == 5
        assert cita_manager._calcular_prioridad("Revaloracion") == 6
        assert cita_manager._calcular_prioridad("Revision") == 7
        assert cita_manager._calcular_prioridad("Examen") == 8
        assert cita_manager._calcular_prioridad("Otro") == 9
        
        # Probar tipo de cita desconocido
        assert cita_manager._calcular_prioridad("TipoDesconocido") == -1
    
    def test_generar_codigo_cita(self, cita_manager):
        """Prueba que se genere un código de cita válido"""
        codigo1 = cita_manager._generar_codigo_cita()
        codigo2 = cita_manager._generar_codigo_cita()
        
        # Verificar que ambos códigos tengan 6 caracteres
        assert len(codigo1) == 6
        assert len(codigo2) == 6
        
        # Verificar que sean diferentes (muy poco probable que sean iguales)
        assert codigo1 != codigo2
        
        # Verificar que solo contengan caracteres válidos (letras mayúsculas y dígitos)
        for char in codigo1:
            assert char.isupper() or char.isdigit()