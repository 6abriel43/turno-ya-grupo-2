"""Pruebas unitarias del modelo Medico."""

from django.test import TestCase
from app.models import Medico, Turno, Paciente , Ausencia , Recordatorio  #Agregar imports de modelos faltantes
from django.utils import timezone
from datetime import timedelta

class MedicoModelTest(TestCase):
    """Verifica comportamiento básico y validaciones del modelo."""

    def setUp(self):
        self.medico = Medico.objects.create(
            nombre="Laura",
            apellido="Romero",
            matricula="MP-9999",
            especialidad="Pediatría",
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
        errors = Medico.validate("Ana", "García", "MP-0001", "Cardiología")
        self.assertEqual(errors, [])

    def test_validate_nombre_vacio_retorna_error(self):
        errors = Medico.validate("", "García", "MP-0001", "Cardiología")
        self.assertTrue(len(errors) > 0)

    def test_validate_matricula_vacia_retorna_error(self):
        errors = Medico.validate("Ana", "García", "", "Cardiología")
        self.assertTrue(len(errors) > 0)

    # --- new ---

    def test_new_crea_medico_con_datos_validos(self):
        medico, errors = Medico.new("Carlos", "López", "MP-1234", "Clínica Médica")
        self.assertEqual(errors, [])
        self.assertIsNotNone(medico)
        self.assertEqual(medico.apellido, "López")
        self.assertTrue(Medico.objects.filter(matricula="MP-1234").exists())

    def test_new_con_datos_invalidos_retorna_errores_y_no_crea(self):
        count_antes = Medico.objects.count()
        medico, errors = Medico.new("", "", "", "")
        self.assertIsNone(medico)
        self.assertTrue(len(errors) > 0)
        self.assertEqual(Medico.objects.count(), count_antes)

    # --- update ---

    def test_update_modifica_datos_correctamente(self):
        errors = self.medico.update("Laura", "Romero", "MP-9999", "Cardiología")
        self.assertEqual(errors, [])
        self.medico.refresh_from_db()
        self.assertEqual(self.medico.especialidad, "Cardiología")

    def test_update_con_datos_invalidos_no_modifica(self):
        errors = self.medico.update("", "", "", "")
        self.assertTrue(len(errors) > 0)
        self.medico.refresh_from_db()
        self.assertEqual(self.medico.nombre, "Laura")  # sin cambios

    # TODO: agregar tests para Paciente y Turno cuando los implementen
class TurnoModelTest(TestCase):

    """TESTS DE MODELO TURNO"""

    def setUp(self):
        self.medico = Medico.objects.create(
            nombre="Juan", apellido="Perez", matricula="MP-1", especialidad="Cardiología"
        )
        self.paciente = Paciente.objects.create(
            nombre="Maria", apellido="Gomez"
        )

    def test_cancelar_turno_exitoso(self):
        fecha = timezone.now() + timedelta(days=1)
        turno, _ = Turno.new(fecha_hora=fecha, medico=self.medico, paciente=self.paciente)
        errors = turno.cancelar()
        self.assertEqual(len(errors), 0)
        self.assertEqual(turno.estado, "CANCELADO")

    def test_cancelar_turno_pasado_falla(self):
        # Creamos un turno en el pasado 
        fecha_pasada = timezone.now() - timedelta(days=1)
        turno, _ = Turno.new(fecha_hora=fecha_pasada, medico=self.medico, paciente=self.paciente)
        errores = turno.cancelar()
        self.assertNotEqual(len(errores), 0)
        self.assertEqual(turno.estado, "PENDIENTE")
    
    def test_aceptar_turno_exitoso(self):
        turno, _ = Turno.new(fecha_hora=timezone.now() + timedelta(days=1), medico=self.medico, paciente=self.paciente)
        errores = turno.aceptar()
        self.assertEqual(len(errores), 0)
        self.assertEqual(turno.estado, "ACEPTADO")

    def test_aceptar_turno_ya_cancelado_falla(self):
        turno, _ = Turno.new(fecha_hora=timezone.now() + timedelta(days=1), medico=self.medico, paciente=self.paciente)
        turno.cancelar() #cancelamos primero
        #Intenta aceptarlo
        errores = turno.aceptar()
        #Verifico que falle
        self.assertNotEqual(len(errores), 0)
        self.assertEqual(turno.estado, "CANCELADO")

        ''''Test Modelos Ausencia + Recordatorio'''

class AusenciaModelTest(TestCase):

    def setUp(self):
        # Infraestructura base idéntica al ejemplo del profesor
        self.medico = Medico.objects.create(
            nombre="Laura",
            apellido="Romero",
            matricula="MP-9999",
            especialidad="Pediatría",
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
        self.medico = Medico.objects.create(
            nombre="Laura", apellido="Romero", matricula="MP-9999", especialidad="Pediatría"
        )
        self.paciente = Paciente.objects.create(nombre="Maria", apellido="Gomez")
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