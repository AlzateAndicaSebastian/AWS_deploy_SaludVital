import pytest
import tempfile
import os
from app.managers.paciente_manager import PacienteManager
from app.config import BASE_DATA_DIR

@pytest.fixture(autouse=True)
def aislamiento_tmpDirectory(monkeypatch,tmp_path):
    monkeypatch.setattr("app.config.BASE_DATA_DIR", tmp_path)

class TestPacienteManager:
    
    @pytest.fixture
    def paciente_manager(self):
        """Crea una instancia de PacienteManager"""
        return PacienteManager()
    
    def test_registrar_paciente(self, paciente_manager):
        """Prueba que se pueda registrar un paciente correctamente"""
        documento = "123456789"
        resultado = paciente_manager.registrar_paciente(
            documento=documento,
            nombre_completo="Juan Perez",
            contraseña="password123",
            telefono="3001234567",
            email="juan@example.com",
            edad=30,
            sexo="Masculino"
        )
        
        assert resultado is True
        
        # Verificar que el paciente fue registrado
        assert paciente_manager.existe_paciente(documento) is True
        
        # Verificar que se pueden obtener los datos del paciente
        datos = paciente_manager.obtener_datos_paciente(documento)
        assert datos is not None
        assert datos["documento"] == documento
        assert datos["nombre_completo"] == "Juan Perez"
        assert datos["telefono"] == "3001234567"
        assert datos["email"] == "juan@example.com"
        assert datos["edad"] == 30
        assert datos["sexo"] == "Masculino"
        assert "contraseña" not in datos  # La contraseña no debe estar en los datos devueltos
    
    def test_registrar_paciente_duplicado(self, paciente_manager):
        """Prueba que no se pueda registrar un paciente duplicado"""
        documento = "987654321"
        
        # Registrar el paciente por primera vez
        paciente_manager.registrar_paciente(
            documento=documento,
            nombre_completo="Maria Garcia",
            contraseña="password456",
            telefono="3007654321",
            email="maria@example.com",
            edad=25,
            sexo="Femenino"
        )
        
        # Intentar registrar el mismo paciente nuevamente
        with pytest.raises(ValueError, match="Ya existe un paciente con ese documento"):
            paciente_manager.registrar_paciente(
                documento=documento,
                nombre_completo="Maria Garcia",
                contraseña="otracontraseña",
                telefono="3007654321",
                email="maria@example.com",
                edad=25,
                sexo="Femenino"
            )
    
    def test_autenticar_paciente_correcto(self, paciente_manager):
        """Prueba que se pueda autenticar un paciente con credenciales correctas"""
        documento = "111111111"
        contraseña = "miclave123"
        
        # Registrar un paciente
        paciente_manager.registrar_paciente(
            documento=documento,
            nombre_completo="Pedro Lopez",
            contraseña=contraseña,
            telefono="3001111111",
            email="pedro@example.com",
            edad=35,
            sexo="Masculino"
        )
        
        # Autenticar con credenciales correctas
        resultado = paciente_manager.autenticar_paciente(documento, contraseña)
        assert resultado is True
    
    def test_autenticar_paciente_incorrecto(self, paciente_manager):
        """Prueba que no se pueda autenticar un paciente con credenciales incorrectas"""
        documento = "222222222"
        contraseña_correcta = "clavecorrecta"
        contraseña_incorrecta = "claveincorrecta"
        
        # Registrar un paciente
        paciente_manager.registrar_paciente(
            documento=documento,
            nombre_completo="Ana Martinez",
            contraseña=contraseña_correcta,
            telefono="3002222222",
            email="ana@example.com",
            edad=28,
            sexo="Femenino"
        )
        
        # Intentar autenticar con contraseña incorrecta
        resultado = paciente_manager.autenticar_paciente(documento, contraseña_incorrecta)
        assert resultado is False
        
        # Intentar autenticar un paciente que no existe
        resultado = paciente_manager.autenticar_paciente("333333333", "cualquierclave")
        assert resultado is False
    
    def test_obtener_datos_paciente_no_existente(self, paciente_manager):
        """Prueba que devuelva None al buscar datos de un paciente que no existe"""
        datos = paciente_manager.obtener_datos_paciente("999999999")
        assert datos is None
    
    def test_hash_contraseña(self, paciente_manager):
        """Prueba que el hash de la contraseña funcione correctamente"""
        contraseña1 = "password123"
        contraseña2 = "password123"
        contraseña3 = "password456"
        
        hash1 = paciente_manager._hash_contraseña(contraseña1)
        hash2 = paciente_manager._hash_contraseña(contraseña2)
        hash3 = paciente_manager._hash_contraseña(contraseña3)
        
        # Las mismas contraseñas deben generar el mismo hash
        assert hash1 == hash2
        
        # Contraseñas diferentes deben generar hashes diferentes
        assert hash1 != hash3