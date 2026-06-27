# TurnoYa

TurnoYa es un sistema web de gestion de turnos medicos para una clinica pequena.
Permite registrar pacientes, administrar medicos, solicitar turnos, aceptar turnos,
registrar ausencias, reprogramar turnos afectados y consultar recordatorios.

## Stack

- Python 3.13+
- Django 5.1+
- SQLite
- Django ORM
- Bootstrap 5
- Git y GitHub

## Funcionalidades principales

- Registro, login y logout de usuarios.
- Perfiles diferenciados para pacientes, medicos y administradores.
- Listado de medicos con filtros por especialidad y obra social.
- Solicitud de turnos por pacientes.
- Listado de turnos propio para medicos.
- Aceptacion y cancelacion de turnos.
- Validacion de franjas horarias y ausencias al crear turnos.
- Historial clinico del paciente para medicos.
- Edicion de observaciones del turno.
- Registro de ausencias medicas.
- Reprogramacion automatica de turnos afectados por ausencias.
- Recordatorios para pacientes.
- Panel de administracion configurado para los modelos principales.
- Templates responsivos con Bootstrap 5.

## Instalacion

Clonar el repositorio:

```bash
git clone https://github.com/6abriel43/turno-ya-grupo-2.git
cd turno-ya-grupo-2
```

Crear y activar el entorno virtual:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Aplicar migraciones:

```bash
python manage.py migrate
```

Opcionalmente cargar datos iniciales:

```bash
python manage.py loaddata initial_data
```

Levantar el servidor:

```bash
python manage.py runserver
```

Aplicacion: http://127.0.0.1:8000/

Admin: http://127.0.0.1:8000/admin/

## Comandos de verificacion

```bash
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test
python manage.py runserver
```

## Tests

El proyecto usa `django.test.TestCase`.

```bash
python manage.py test -v 2
python manage.py test app.tests.test_models -v 2
python manage.py test app.tests.test_views -v 2
python manage.py test app.tests.test_historial_paciente -v 2
```

## Rutas principales

- `/` panel de inicio.
- `/medicos/` listado de medicos.
- `/medicos/<id>/` detalle de medico.
- `/pacientes/` listado de pacientes para medicos.
- `/pacientes/<id>/historial/` historial clinico del paciente.
- `/turno/nuevo/` solicitud de turno para pacientes.
- `/turnos/` listado de turnos para medicos.
- `/mis-turnos/` turnos del paciente autenticado.
- `/ausencias/` listado de ausencias para medicos.
- `/ausencias/nueva/` registro de ausencia.
- `/recordatorios/` panel de recordatorios para medicos.
- `/mis-recordatorios/` recordatorios del paciente autenticado.
- `/registro/` registro de paciente.
- `/accounts/login/` login.

## Modelos principales

- `Especialidad`
- `ObraSocial`
- `Medico`
- `Paciente`
- `FranjaHoraria`
- `Turno`
- `Ausencia`
- `Recordatorio`

Los modelos implementan metodos de validacion y negocio usados por la entrega:
`validate()`, `new()`, `update()` y al menos un metodo propio segun corresponda.

## Integrantes

- Gabriel Guitian
- Fabrizio Verdu
- Mateo Mazuela
- Facundo Zamora
- Luca Mechulan

## Notas de uso

- Las vistas privadas usan `LoginRequiredMixin`.
- Las vistas de medicos, pacientes y administracion validan permisos por rol.
- Los pacientes no pueden ver paneles operativos de medicos.
- Los medicos ven solo los turnos y datos que les corresponden, salvo usuarios staff o superusuarios.
