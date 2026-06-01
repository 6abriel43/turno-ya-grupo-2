"""Pruebas unitarias del modelo Medico."""

from django.test import TestCase
from app.models import Medico, Turno, Paciente , Ausencia , Recordatorio , Especialidad , ObraSocial  #Agregar imports de modelos faltantes
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User


class MedicoModelTest(TestCase):
    """Verifica comportamiento básico y validaciones del modelo."""

    def setUp(self):
        
        self.user = User.objects.create_user(username="lromero", password="test1234")  # Usuario para el médico
        self.especialidad = Especialidad.objects.create(nombre="Pediatría")  # Especialidad para el médico
        self.obra_social = ObraSocial.objects.create(nombre="OSDE")  # Obra social para el médico

        self.medico = Medico.objects.create(
            usuario=self.user,
            nombre="Laura",
            apellido="Romero",
            matricula="MP-9999",
            especialidad=self.especialidad,
            obra_social=self.obra_social
        )

    # --- __str__ y métodos simples ---

    def test_str_incluye_apellido_y_nombre(self):
        self.assertIn("Romero", str(self.medico))
        self.assertIn("Laura", str(self.medico))

    def test_nombre_completo(self):
        self.assertEqual(self.medico.nombre_completo(), "Laura Romero")

    def test_cantidad_turnos_inicial_es_cero(self):
        self.assertEqual(self.medico.cantidad_turnos(), 0)

    # --- validate ---

    def test_validate_datos_correctos_retorna_lista_vacia(self):
        medico_test = Medico(
            usuario=self.user,
            nombre="Ana",
            apellido="García",
            matricula="MP-0001",
            especialidad=self.especialidad,
            obra_social=self.obra_social
        )
        errors = medico_test.validate()
        self.assertEqual(errors, [])

    def test_validate_nombre_vacio_retorna_error(self):
        medico_test = Medico(
            usuario=self.user,
            nombre="",
            apellido="García",
            matricula="MP-0001",
            especialidad=self.especialidad,
            obra_social=self.obra_social
        )
        errors = medico_test.validate()
        self.assertIn("El nombre es obligatorio.", errors)

    def test_validate_matricula_vacia_retorna_error(self):
        medico_test = Medico(
            usuario=self.user,
            nombre="Ana",
            apellido="García",
            matricula="",
            especialidad=self.especialidad,
            obra_social=self.obra_social
        )
        errors = medico_test.validate()
        self.assertIn("La matrícula es obligatoria.", errors)

    # --- new ---

    def test_new_crea_medico_con_datos_validos(self):
        medico, errors = Medico.new(
            usuario=self.user,
            nombre="Carlos",
            apellido="López",
            matricula="MP-1234",
            especialidad=self.especialidad,
            obra_social=self.obra_social
        )
        self.assertEqual(errors, [])
        self.assertIsNotNone(medico)
        self.assertEqual(medico.apellido, "López")
        self.assertTrue(Medico.objects.filter(matricula="MP-1234").exists())

    def test_new_con_datos_invalidos_retorna_errores_y_no_crea(self):
        count_antes = Medico.objects.count()
        medico, errors = Medico.new(
            usuario=self.user,
            nombre="",
            apellido="",
            matricula="",
            especialidad=self.especialidad,
            obra_social=self.obra_social
        )
        self.assertIsNone(medico)
        self.assertTrue(len(errors) > 0)
        self.assertEqual(Medico.objects.count(), count_antes)

    # --- update ---

    def test_update_modifica_datos_correctamente(self):
        nueva_especialidad = Especialidad.objects.create(nombre="Cardiología")
        errors = self.medico.update(
            nombre= "Laura",
            apellido= "Romero",
            matricula= "MP-9999",
            especialidad= nueva_especialidad,
            obra_social= self.obra_social
        )
        self.assertEqual(errors, [])
        self.medico.refresh_from_db()
        self.assertEqual(self.medico.especialidad.nombre, "Cardiología")

    def test_update_con_datos_invalidos_no_modifica(self):
        errors = self.medico.update(nombre="")
        self.assertTrue(len(errors) > 0)
        self.medico.refresh_from_db()
        self.assertEqual(self.medico.nombre, "Laura")  # El nombre no debería haber cambiado

class TurnoModelTest(TestCase):
    """TESTS DE MODELO TURNO"""
    def setUp(self):
        # Creamos las dependencias completas para que no tire IntegrityError
        self.user_med = User.objects.create_user(username="med_turno", password="123")
        self.user_pac = User.objects.create_user(username="pac_turno", password="123")
        self.especialidad = Especialidad.objects.create(nombre="Cardiología")
        self.obra_social = ObraSocial.objects.create(nombre="OSDE")

        self.medico = Medico.objects.create(usuario=self.user_med, nombre="Juan", apellido="Perez", matricula="MP-1", especialidad=self.especialidad, obra_social=self.obra_social)
        self.paciente = Paciente.objects.create(usuario=self.user_pac, nombre="Maria", apellido="Gomez", dni="111", email="a@a.com", obra_social=self.obra_social)

    # --- Tests validate, new y update ---
    def test_validate_datos_incompletos_retorna_error(self):
        turno_malo = Turno(motivo="Falta medico y paciente")
        errors = turno_malo.validate()
        self.assertIn("Datos incompletos.", errors)

    def test_new_crea_turno_valido(self):
        fecha = timezone.now() + timedelta(days=2)
        turno, errors = Turno.new(fecha_hora=fecha, medico=self.medico, paciente=self.paciente)
        self.assertEqual(errors, [])
        self.assertEqual(turno.estado, "PENDIENTE")

    def test_update_modifica_datos_correctamente(self):
        fecha = timezone.now() + timedelta(days=2)
        turno, _ = Turno.new(fecha_hora=fecha, medico=self.medico, paciente=self.paciente, motivo="Viejo motivo")
        errors = turno.update(motivo="Nuevo motivo")
        self.assertEqual(errors, [])
        turno.refresh_from_db()
        self.assertEqual(turno.motivo, "Nuevo motivo")

    # --- Tests Métodos de Negocio ---
    def test_esta_pendiente(self):
        fecha = timezone.now() + timedelta(days=2)
        turno, _ = Turno.new(fecha_hora=fecha, medico=self.medico, paciente=self.paciente)
        self.assertTrue(turno.esta_pendiente())

    def test_cancelar_turno_exitoso(self):
        fecha = timezone.now() + timedelta(days=1)
        turno, _ = Turno.new(fecha_hora=fecha, medico=self.medico, paciente=self.paciente)
        errors = turno.cancelar()
        self.assertEqual(len(errors), 0)
        self.assertEqual(turno.estado, "CANCELADO")

    def test_confirmar_turno_exitoso(self):
        turno, _ = Turno.new(fecha_hora=timezone.now() + timedelta(days=1), medico=self.medico, paciente=self.paciente)
        errores = turno.confirmar()
        self.assertEqual(len(errores), 0)
        self.assertEqual(turno.estado, "CONFIRMADO")


class PacienteModelTest(TestCase):
    """TESTS DE MODELO PACIENTE"""

    def setUp(self):
        self.user = User.objects.create_user(username="mgomez", password="test1234")
        self.obra_social = ObraSocial.objects.create(nombre="OSDE")
        
        self.paciente = Paciente.objects.create(
            usuario=self.user,
            nombre="Maria", 
            apellido="Gomez",
            dni="12345678",
            email="maria.gomez@mail.com",
            telefono="123456789",
            obra_social=self.obra_social
        )

    def test_str_incluye_apellido_y_nombre(self):
        self.assertIn("Gomez", str(self.paciente))
        self.assertIn("Maria", str(self.paciente))

    # --- Métodos de Negocio  ---

    def test_obtener_nombre_completo(self):
        """Verifica que el método de negocio concatene el nombre real de manera natural."""
        self.assertEqual(self.paciente.obtener_nombre_completo(), "Maria Gomez")

    # --- validate ---

    def test_validate_datos_correctos_retorna_lista_vacia(self):
        paciente_test = Paciente(
            usuario=self.user,
            nombre="Carlos", 
            apellido="López",
            dni="87654321",
            email="carlos.lopez@mail.com",
            telefono="987654321",
            obra_social=self.obra_social
        )
        errors = paciente_test.validate()
        self.assertEqual(errors, [])

    def test_validate_dni_con_letras_retorna_error(self):
        paciente_test = Paciente(
            usuario=self.user,
            nombre="Carlos", 
            apellido="López",
            dni="ABC12345",
            email="carlos.lopez@mail.com",
            telefono="987654321",
            obra_social=self.obra_social
        )
        errors = paciente_test.validate()
        self.assertIn("El DNI debe contener solo números.", errors)

    def test_validate_campos_obligatorios_vacios_retorna_errores(self):
        paciente_test = Paciente(
            usuario=self.user,
            nombre="", 
            apellido="", 
            dni="", 
            email="", 
            telefono="", 
            obra_social=self.obra_social
        )
        errors = paciente_test.validate()
        self.assertIn("El nombre es obligatorio.", errors)
        self.assertIn("El apellido es obligatorio.", errors)
        self.assertIn("El DNI es obligatorio.", errors)
        self.assertIn("La obra social es obligatoria.", errors)

    # --- new ---

    def test_new_crea_paciente_y_limpiamos_campos(self):
        paciente, errors = Paciente.new(
            usuario=self.user,
            nombre="Carlos", 
            apellido="López",
            dni="87654321",
            email="carlos.lopez@mail.com",
            telefono="987654321",
            obra_social=self.obra_social
        )
        self.assertEqual(errors, [])
        self.assertIsNotNone(paciente)
        self.assertEqual(paciente.nombre, "Carlos")
        self.assertEqual(paciente.apellido, "López")
        self.assertTrue(Paciente.objects.filter(dni="87654321").exists())

    def test_new_invalido_retorna_errores_y_no_persiste(self):
        user_falla = User.objects.create_user(username="cfalla", password="test1234")
        count_antes = Paciente.objects.count()

        paciente, errors = Paciente.new(
            usuario=user_falla,
            nombre="", 
            apellido="", 
            dni="ABC12345",
            email="", 
            telefono="", 
            obra_social=self.obra_social
        )
        self.assertIsNone(paciente)
        self.assertTrue(len(errors) >= 2)
        self.assertEqual(Paciente.objects.count(), count_antes)

    # --- update ---

    def test_update_modifica_datos_correctamente(self):
        errors = self.paciente.update(
            nombre="Carlos", 
            apellido="López",
            dni="87654321",
            email="carlos.lopez@mail.com",
            telefono="987654321",
            obra_social=self.obra_social
        )
        self.assertEqual(errors, [])
        self.paciente.refresh_from_db()
        self.assertEqual(self.paciente.nombre, "Carlos")

    def test_update_invalido_retiene_datos_originales(self):
        errors = self.paciente.update(dni="ABC12345")
        self.assertIn("El DNI debe contener solo números.", errors)
        self.paciente.refresh_from_db()
        self.assertEqual(self.paciente.dni, "12345678")

        ''''Test Modelos Ausencia + Recordatorio'''

class AusenciaModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="laura_ausencia", password="123")
        self.especialidad = Especialidad.objects.create(nombre="Pediatría")
        self.obra_social = ObraSocial.objects.create(nombre="OSDE")
        
        self.medico = Medico.objects.create(
            usuario=self.user,
            nombre="Laura",
            apellido="Romero",
            matricula="MP-9999",
            especialidad=self.especialidad,
            obra_social=self.obra_social
        )
        
        self.fecha_i = timezone.now().date()
        self.fecha_f = timezone.now().date() + timedelta(days=2)
        
        self.ausencia, _ = Ausencia.new(
            medico=self.medico,
            motivo="Congreso",
            fecha_inicio=self.fecha_i,
            fecha_fin=self.fecha_f
        )

        # --- __str__ y métodos de negocio ---

    def test_str_incluye_medico_y_fecha(self):
        self.assertIn("Laura", str(self.ausencia))
        self.assertIn("Romero", str(self.ausencia))

    def test_es_vigente_hoy_retorna_true(self):
        """Método de negocio: caso exitoso (está ocurriendo hoy)."""
        self.assertTrue(self.ausencia.es_vigente())

    def test_es_vigente_pasada_retorna_false(self):
        """Método de negocio: caso alternativo (ausencia antigua)."""
        hace_cinco_dias = timezone.now().date() - timedelta(days=5)
        hace_dos_dias = timezone.now().date() - timedelta(days=2)
        ausencia_vieja, _ = Ausencia.new(
            medico=self.medico, motivo="Licencia", fecha_inicio=hace_cinco_dias, fecha_fin=hace_dos_dias
        )
        self.assertFalse(ausencia_vieja.es_vigente())

        # --- validate ---

    def test_validate_datos_correctos_retorna_lista_vacia(self):
        errors = self.ausencia.validate()
        self.assertEqual(errors, [])

    def test_validate_fechas_invertidas_retorna_error(self):
        self.ausencia.fecha_inicio = timezone.now().date() + timedelta(days=5)
        self.ausencia.fecha_fin = timezone.now().date()  # Fin antes que inicio
        errors = self.ausencia.validate()
        self.assertTrue(len(errors) > 0)

    # --- new ---

    def test_new_crea_ausencia_con_datos_validos(self):
        inicio = timezone.now().date() + timedelta(days=10)
        fin = timezone.now().date() + timedelta(days=12)
        ausencia, errors = Ausencia.new(medico=self.medico, motivo="Vacaciones", fecha_inicio=inicio, fecha_fin=fin)
        self.assertEqual(errors, [])
        self.assertIsNotNone(ausencia)
        self.assertEqual(ausencia.motivo, "Vacaciones")
        self.assertTrue(Ausencia.objects.filter(motivo="Vacaciones").exists())

    # --- update ---

    def test_update_modifica_datos_correctamente(self):
        errors = self.ausencia.update(motivo="Enfermedad")
        self.assertEqual(errors, [])
        self.ausencia.refresh_from_db()
        self.assertEqual(self.ausencia.motivo, "Enfermedad")


class RecordatorioModelTest(TestCase):
    
    def setUp(self):
        self.user_medico = User.objects.create_user(username="med_rec", password="123")
        self.user_paciente = User.objects.create_user(username="pac_rec", password="123")
        self.especialidad = Especialidad.objects.create(nombre="Pediatría")
        self.obra_social = ObraSocial.objects.create(nombre="OSDE")

        
        self.medico = Medico.objects.create(
            usuario=self.user_medico,
            nombre="Laura", 
            apellido="Romero", 
            matricula="MP-9999", 
            especialidad=self.especialidad,
            obra_social=self.obra_social
        )
        
    
        self.paciente = Paciente.objects.create(
            usuario=self.user_paciente,
            nombre="Maria", 
            apellido="Gomez",
            dni="11111111",
            email="maria@mail.com",
            obra_social=self.obra_social
        )
        
        self.turno, _ = Turno.new(
            fecha_hora=timezone.now() + timedelta(days=1), medico=self.medico, paciente=self.paciente
        )
        self.recordatorio, _ = Recordatorio.new(
            turno=self.turno,
            fecha_envio=timezone.now(),
            tipo="SMS",
            asunto="Aviso",
            mensaje="Recordatorio"
        )

    # --- __str__ y métodos de negocio ---

    def test_str_incluye_asunto(self):
        self.assertIn("Aviso", str(self.recordatorio))

    def test_marcar_como_leido_modifica_estado_exitoso(self):
        """Método de negocio: caso exitoso."""
        self.assertFalse(self.recordatorio.leido)
        errors = self.recordatorio.marcar_como_leido()
        self.assertEqual(errors, [])
        self.assertTrue(self.recordatorio.leido)

        # --- validate ---

    def test_validate_datos_correctos_retorna_lista_vacia(self):
        errors = self.recordatorio.validate()
        self.assertEqual(errors, [])

    # --- new ---

    def test_new_crea_recordatorio_con_datos_validos(self):
        rec, errors = Recordatorio.new(
            turno=self.turno, fecha_envio=timezone.now(), tipo="EMAIL", asunto="Turno Mañana", mensaje="Test"
        )
        self.assertEqual(errors, [])
        self.assertIsNotNone(rec)
        self.assertTrue(Recordatorio.objects.filter(asunto="Turno Mañana").exists())

    # --- update ---

    def test_update_modifica_datos_correctamente(self):
        errors = self.recordatorio.update(asunto="Nuevo Asunto")
        self.assertEqual(errors, [])
        self.recordatorio.refresh_from_db()
        self.assertEqual(self.recordatorio.asunto, "Nuevo Asunto")

    # --- ESPECIALIDAD ---

class EspecialidadModelTest(TestCase):
    """Verifica comportamiento básico y validaciones del modelo Especialidad."""

    def setUp(self):
        self.especialidad, _ = Especialidad.new(
            nombre="Pediatría",
            descripcion="Cuidado médico de niños y adolescentes"
        )

    # --- __str__ y métodos simples ---
    
    def test_str_retorna_nombre_especialidad(self):
        self.assertEqual(str(self.especialidad), "Pediatría")

    # --- Métodos de Negocio  ---

    def test_tiene_detalles_con_descripcion_retorna_true(self):
        """Verifica que retorne True si la especialidad tiene descripción cargada."""
        self.assertTrue(self.especialidad.tiene_detalles())

    def test_tiene_detalles_vacio_retorna_false(self):
        """Verifica que retorne False si la descripción está en blanco o vacía."""
        esp_sin_desc, _ = Especialidad.new(nombre="Cardiología", descripcion="")
        self.assertFalse(esp_sin_desc.tiene_detalles())

    # --- validate ---

    def test_validate_datos_correctos_retorna_lista_vacia(self):
        errors = Especialidad.validate("Cardiología")
        self.assertEqual(errors, [])

    def test_validate_nombre_vacio_retorna_error(self):
        errors = Especialidad.validate("")
        self.assertTrue(len(errors) > 0)
        self.assertIn("El nombre de la especialidad es obligatorio.", errors)

    def test_validate_nombre_corto_retorna_error(self):
        errors = Especialidad.validate("Eco")  # Menos de 4 caracteres
        self.assertTrue(len(errors) > 0)
        self.assertIn("El nombre de la especialidad debe tener al menos 4 caracteres.", errors)

    # --- new ---

    def test_new_crea_especialidad_con_datos_validos(self):
        esp, errors = Especialidad.new("Dermatología", "Problemas de la piel")
        self.assertEqual(errors, [])
        self.assertIsNotNone(esp)
        self.assertEqual(esp.nombre, "Dermatología")
        self.assertTrue(Especialidad.objects.filter(nombre="Dermatología").exists())

    def test_new_con_datos_invalidos_no_crea_registro(self):
        count_antes = Especialidad.objects.count()
        esp, errors = Especialidad.new("   ")
        self.assertIsNone(esp)
        self.assertTrue(len(errors) > 0)
        self.assertEqual(Especialidad.objects.count(), count_antes)

    # --- update ---

    def test_update_modifica_datos_correctamente(self):
        errors = self.especialidad.update("Neurología Infantil", "Nueva descripción")
        self.assertEqual(errors, [])
        self.especialidad.refresh_from_db()
        self.assertEqual(self.especialidad.nombre, "Neurología Infantil")

    def test_update_con_datos_invalidos_no_modifica(self):
        errors = self.especialidad.update("")
        self.assertTrue(len(errors) > 0)
        self.especialidad.refresh_from_db()
        self.assertEqual(self.especialidad.nombre, "Pediatría")


class ObraSocialModelTest(TestCase):
    """Verifica comportamiento básico y validaciones del modelo ObraSocial."""

    def setUp(self):
        self.obra_social, _ = ObraSocial.new(
            nombre="Organización de Servicios Directos Empresarios",
            sigla="osde"
        )

    # --- __str__ y métodos simples ---

    def test_str_incluye_sigla_y_nombre_si_ambos_existen(self):
        self.assertEqual(str(self.obra_social), "OSDE - Organización de Servicios Directos Empresarios")

    def test_str_solo_incluye_nombre_si_no_hay_sigla(self):
        os_sin_sigla, _ = ObraSocial.new(nombre="Obra Social de Chóferes")
        self.assertEqual(str(os_sin_sigla), "Obra Social de Chóferes")

    # --- Métodos de Negocio  ---

    def test_obtener_identificador_comercial_con_sigla(self):
        """Verifica que devuelva la sigla si está cargada."""
        self.assertEqual(self.obra_social.obtener_identificador_comercial(), "OSDE")

    def test_obtener_identificador_comercial_sin_sigla(self):
        """Verifica que devuelva el nombre completo si no tiene sigla."""
        os_sin_sigla, _ = ObraSocial.new(nombre="Particular")
        self.assertEqual(os_sin_sigla.obtener_identificador_comercial(), "Particular")

    # --- validate ---

    def test_validate_datos_correctos_retorna_lista_vacia(self):
        errors = ObraSocial.validate("Programa de Atención Médica Integral")
        self.assertEqual(errors, [])

    def test_validate_nombre_vacio_retorna_error(self):
        errors = ObraSocial.validate("")
        self.assertTrue(len(errors) > 0)
        self.assertIn("El nombre de la obra social es obligatorio.", errors)

    def test_validate_nombre_corto_retorna_error(self):
        errors = ObraSocial.validate("OS")
        self.assertTrue(len(errors) > 0)
        self.assertIn("El nombre de la obra social debe tener al menos 3 caracteres.", errors)

    # --- new ---

    def test_new_crea_obra_social_con_datos_validos_y_sigla_en_mayusculas(self):
        os, errors = ObraSocial.new("Obra Social de la Unión del Personal Civil de la Nación", "upcn")
        self.assertEqual(errors, [])
        self.assertIsNotNone(os)
        self.assertEqual(os.sigla, "UPCN")
        self.assertTrue(ObraSocial.objects.filter(sigla="UPCN").exists())

    # --- update ---

    def test_update_modifica_datos_correctamente(self):
        errors = self.obra_social.update("Medicus SA", "med")
        self.assertEqual(errors, [])
        self.obra_social.refresh_from_db()
        self.assertEqual(self.obra_social.nombre, "Medicus SA")
        self.assertEqual(self.obra_social.sigla, "MED")