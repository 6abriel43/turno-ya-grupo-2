"""Tests del modelo FranjaHoraria."""

from datetime import time

from django.test import TestCase

from app.models import FranjaHoraria


class FranjaHorariaModelTest(TestCase):
    def test_validate_con_dia_vacio(self):
        errors = FranjaHoraria.validate("", time(8, 0), time(9, 0))
        self.assertIn("El dia es obligatorio.", errors)

    def test_validate_con_dia_invalido(self):
        errors = FranjaHoraria.validate("XXX", time(8, 0), time(9, 0))
        self.assertIn("El dia no es valido.", errors)

    def test_validate_con_hora_inicio_mayor_o_igual_que_hora_fin(self):
        errors = FranjaHoraria.validate("LUN", time(10, 0), time(10, 0))
        self.assertIn("La hora de inicio debe ser menor que la hora de fin.", errors)

    def test_new_crea_franja_valida(self):
        franja, errors = FranjaHoraria.new("MAR", time(8, 30), time(10, 0))
        self.assertEqual(errors, [])
        self.assertIsNotNone(franja)
        self.assertEqual(franja.dia, "MAR")

    def test_new_rechaza_franja_invalida(self):
        cantidad_anterior = FranjaHoraria.objects.count()
        franja, errors = FranjaHoraria.new("XXX", time(8, 30), time(10, 0))
        self.assertIsNone(franja)
        self.assertTrue(errors)
        self.assertEqual(FranjaHoraria.objects.count(), cantidad_anterior)

    def test_update_modifica_franja_valida(self):
        franja, _ = FranjaHoraria.new("LUN", time(8, 0), time(9, 0))
        errors = franja.update("MIE", time(9, 0), time(11, 0))
        self.assertEqual(errors, [])
        franja.refresh_from_db()
        self.assertEqual(franja.dia, "MIE")
        self.assertEqual(franja.hora_inicio, time(9, 0))

    def test_update_rechaza_datos_invalidos_sin_guardar(self):
        franja, _ = FranjaHoraria.new("LUN", time(8, 0), time(9, 0))
        errors = franja.update("LUN", time(12, 0), time(10, 0))
        self.assertTrue(errors)
        franja.refresh_from_db()
        self.assertEqual(franja.hora_inicio, time(8, 0))
        self.assertEqual(franja.hora_fin, time(9, 0))

    def test_duracion_en_minutos(self):
        franja, _ = FranjaHoraria.new("JUE", time(8, 30), time(10, 0))
        self.assertEqual(franja.duracion_en_minutos(), 90)
