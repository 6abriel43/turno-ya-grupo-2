from datetime import timedelta

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from app.models import Especialidad, Medico, ObraSocial, Paciente, Turno


class HistorialPacienteTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.usuario_medico = User.objects.create_user(username="medico_historial", password="123")
        self.usuario_otro_medico = User.objects.create_user(username="otro_medico", password="123")
        self.usuario_paciente = User.objects.create_user(username="paciente_historial", password="123")
        self.usuario_comun = User.objects.create_user(username="usuario_comun", password="123")

        self.especialidad = Especialidad.objects.create(nombre="Clinica medica")
        self.obra_social = ObraSocial.objects.create(nombre="OSDE")

        self.medico = Medico.objects.create(
            usuario=self.usuario_medico,
            nombre="Laura",
            apellido="Romero",
            matricula="MP-100",
            especialidad=self.especialidad,
            obra_social=self.obra_social,
        )
        self.otro_medico = Medico.objects.create(
            usuario=self.usuario_otro_medico,
            nombre="Carlos",
            apellido="Lopez",
            matricula="MP-200",
            especialidad=self.especialidad,
            obra_social=self.obra_social,
        )
        self.paciente = Paciente.objects.create(
            usuario=self.usuario_paciente,
            nombre="Ana",
            apellido="Perez",
            dni="12345678",
            email="ana@test.com",
            obra_social=self.obra_social,
        )

        self.turno_confirmado = Turno.objects.create(
            fecha_hora=timezone.now() - timedelta(days=5),
            medico=self.medico,
            paciente=self.paciente,
            motivo="Control",
            estado="CONFIRMADO",
        )
        self.turno_finalizado = Turno.objects.create(
            fecha_hora=timezone.now() - timedelta(days=2),
            medico=self.medico,
            paciente=self.paciente,
            motivo="Seguimiento",
            estado="FINALIZADO",
        )
        self.turno_pendiente = Turno.objects.create(
            fecha_hora=timezone.now() + timedelta(days=2),
            medico=self.medico,
            paciente=self.paciente,
            motivo="Pendiente",
            estado="PENDIENTE",
        )

    def test_medico_puede_ver_historial_de_paciente(self):
        self.client.login(username="medico_historial", password="123")
        url = reverse("app:historial_paciente", kwargs={"paciente_id": self.paciente.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "clinica/historial_paciente.html")
        self.assertEqual(response.context["paciente"], self.paciente)

    def test_usuario_no_medico_no_puede_ver_historial(self):
        self.client.login(username="usuario_comun", password="123")
        url = reverse("app:historial_paciente", kwargs={"paciente_id": self.paciente.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_historial_muestra_solo_confirmados_o_finalizados(self):
        self.client.login(username="medico_historial", password="123")
        url = reverse("app:historial_paciente", kwargs={"paciente_id": self.paciente.id})

        response = self.client.get(url)
        turnos = list(response.context["turnos"])

        self.assertIn(self.turno_confirmado, turnos)
        self.assertIn(self.turno_finalizado, turnos)
        self.assertNotIn(self.turno_pendiente, turnos)

    def test_medico_puede_guardar_observacion(self):
        self.client.login(username="medico_historial", password="123")
        url = reverse("app:editar_observacion", kwargs={"pk": self.turno_confirmado.id})

        response = self.client.post(url, {"observaciones": "Paciente evoluciona bien."})

        self.assertEqual(response.status_code, 302)

    def test_observacion_queda_guardada_en_turno(self):
        self.client.login(username="medico_historial", password="123")
        url = reverse("app:editar_observacion", kwargs={"pk": self.turno_confirmado.id})

        self.client.post(url, {"observaciones": "Indicar nuevo control."})
        self.turno_confirmado.refresh_from_db()

        self.assertEqual(self.turno_confirmado.observaciones, "Indicar nuevo control.")

    def test_medico_no_puede_editar_turno_de_otro_medico(self):
        self.client.login(username="otro_medico", password="123")
        url = reverse("app:editar_observacion", kwargs={"pk": self.turno_confirmado.id})

        response = self.client.post(url, {"observaciones": "No corresponde."})

        self.assertEqual(response.status_code, 404)
        self.turno_confirmado.refresh_from_db()
        self.assertEqual(self.turno_confirmado.observaciones, "")
